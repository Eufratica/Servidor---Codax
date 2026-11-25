"""
Parser puro da topologia ESP-MESH (resposta de `query topology`).

Sem I/O: recebe o payload já decodificado e devolve estruturas Python.
Formato real emitido pelo firmware Codax (tópico [dev/]topo/shopba/mesh/<root>):

    {"page": 1, "root": "70:4b:ca:49:1d:9c(Teste)", "router_mac": "bc:07:1d:57:11:76",
     "router_rssi(dB)": -52, "total_devices": 2,
     "mesh": ["|layer: 1|mac: 70:4b:ca:49:1d:9c|id: Teste |parent_id: 0 |rssi: -52 |",
              "|layer: 2|mac: 30:83:98:63:50:b0|id: 30:83:98:63:50:b0 |parent_id: Teste |rssi: -20 |"]}

Regras importantes:
- `parent_id` é o **id (nome)** do pai, não o MAC. "0" significa o roteador Wi-Fi (nó ROOT).
- Quando o pai é informado por MAC, o ESP-MESH costuma reportar o MAC da interface
  SoftAP, que é o MAC base (STA) + 1. Por isso a resolução também tenta MAC - 1.
- A resposta pode vir paginada (`page` / `total_devices`).
"""

import re
from typing import Any, Dict, List, Optional

_HEX = "0123456789abcdef"


def clean_mac(value: Any) -> Optional[str]:
    """'70:4b:ca:49:1d:9c(Teste)' -> '704bca491d9c'. Retorna None se não for MAC válido."""
    if value is None:
        return None
    base = str(value).split("(")[0].strip().lower()
    cleaned = "".join(c for c in base if c in _HEX)
    if len(cleaned) != 12:
        return None
    # Um id textual como "Teste" não tem 12 hex; mas "cafe" + lixo poderia ter — exige formato de MAC.
    if not re.fullmatch(r"[0-9a-f]{12}|([0-9a-f]{2}[:\-]){5}[0-9a-f]{2}", base):
        return None
    return cleaned


def mac_offset(mac: str, delta: int) -> Optional[str]:
    try:
        v = int(mac, 16) + delta
    except (TypeError, ValueError):
        return None
    if v < 0 or v > 0xFFFFFFFFFFFF:
        return None
    return format(v, "012x")


def _to_int(value: Any) -> Optional[int]:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _paren_label(value: Any) -> Optional[str]:
    """'70:4b:ca:49:1d:9c(Teste)' -> 'Teste'."""
    m = re.search(r"\(([^)]*)\)", str(value or ""))
    return m.group(1).strip() if m and m.group(1).strip() else None


def parse_mesh_line(line: str) -> Optional[Dict[str, Any]]:
    """Converte '|layer: 2|mac: ...|id: ...|parent_id: ...|rssi: -20 |' em dict."""
    if not isinstance(line, str) or "mac" not in line.lower():
        return None
    fields: Dict[str, str] = {}
    for part in line.split("|"):
        if ":" not in part:
            continue
        key, _, val = part.partition(":")
        fields[key.strip().lower()] = val.strip()
    mac = clean_mac(fields.get("mac"))
    if not mac:
        return None
    return {
        "mac": mac,
        "id": fields.get("id") or None,
        "layer": _to_int(fields.get("layer")),
        "parent_ref": fields.get("parent_id", "").strip() or None,
        "rssi": _to_int(fields.get("rssi")),
    }


def _flatten_nested(node: Dict[str, Any], parent_mac: Optional[str], layer: int, out: List[Dict[str, Any]]):
    """Formato legado aninhado: {mac_addr, layer, nodes:[...]}."""
    mac = clean_mac(node.get("mac_addr") or node.get("mac"))
    if not mac:
        return
    rssi = node.get("parent_rssi", node.get("router_rssi", node.get("rssi")))
    out.append({
        "mac": mac,
        "id": node.get("id"),
        "layer": _to_int(node.get("layer")) or layer,
        "parent_ref": parent_mac or ("0" if layer == 1 else None),
        "rssi": _to_int(rssi),
    })
    for child in node.get("nodes") or []:
        if isinstance(child, dict):
            _flatten_nested(child, mac, layer + 1, out)


def parse_topology_payload(payload: Any) -> Optional[Dict[str, Any]]:
    """
    Reconhece uma resposta de topologia e normaliza para:
      {root_mac, root_id, router_mac, router_rssi, page, total_devices, entries:[{mac,id,layer,parent_ref,rssi}]}
    Retorna None se o payload não for uma topologia.
    """
    if not isinstance(payload, dict):
        return None

    entries: List[Dict[str, Any]] = []
    mesh = payload.get("mesh")
    if isinstance(mesh, list):
        for item in mesh:
            parsed = parse_mesh_line(item) if isinstance(item, str) else None
            if parsed:
                entries.append(parsed)
    elif isinstance(payload.get("nodes"), list) and (payload.get("mac_addr") or payload.get("mac")):
        _flatten_nested(payload, None, 1, entries)
    else:
        return None

    if not entries:
        return None

    root_mac = clean_mac(payload.get("root"))
    root_entry = next((e for e in entries if e["layer"] == 1), None)
    if not root_mac and root_entry:
        root_mac = root_entry["mac"]
    if not root_mac:
        return None

    router_rssi = payload.get("router_rssi(dB)", payload.get("router_rssi"))
    return {
        "root_mac": root_mac,
        "root_id": _paren_label(payload.get("root")) or (root_entry or {}).get("id"),
        "router_mac": clean_mac(payload.get("router_mac") or payload.get("router_mac_addr")),
        "router_rssi": _to_int(router_rssi),
        "page": _to_int(payload.get("page")) or 1,
        "total_devices": _to_int(payload.get("total_devices")),
        "entries": entries,
    }


def build_mesh_tree(root_mac: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Monta a árvore a partir das entradas (todas as páginas). Puro e determinístico.
    Retorna {root: node|None, orphans: [node], edges: [(parent, child)]}
    onde node = {mac, id, layer, parent_mac, parent_ref, rssi, nodes:[...]}.
    """
    by_mac: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        if e.get("mac") and e["mac"] not in by_mac:
            by_mac[e["mac"]] = {**e, "parent_mac": None, "nodes": []}

    if root_mac not in by_mac:
        by_mac[root_mac] = {"mac": root_mac, "id": None, "layer": 1, "parent_ref": "0",
                            "rssi": None, "parent_mac": None, "nodes": [], "placeholder": True}

    by_id: Dict[str, str] = {}
    for mac, n in by_mac.items():
        if n.get("id"):
            by_id.setdefault(str(n["id"]).strip(), mac)

    def resolve(node: Dict[str, Any]) -> Optional[str]:
        ref = (node.get("parent_ref") or "").strip()
        if node["mac"] == root_mac or node.get("layer") == 1 or ref in ("", "0"):
            return None
        if ref in by_id and by_id[ref] != node["mac"]:
            return by_id[ref]
        ref_mac = clean_mac(ref)
        if ref_mac:
            for cand in (ref_mac, mac_offset(ref_mac, -1), mac_offset(ref_mac, +1)):
                if cand and cand in by_mac and cand != node["mac"]:
                    return cand
        return None

    edges = []
    for mac, n in by_mac.items():
        p = resolve(n)
        if p:
            n["parent_mac"] = p
            by_mac[p]["nodes"].append(n)
            edges.append((p, mac))

    # Alcançáveis a partir do ROOT (protege contra ciclos)
    reachable = set()
    stack = [root_mac]
    while stack:
        cur = stack.pop()
        if cur in reachable:
            continue
        reachable.add(cur)
        stack.extend(c["mac"] for c in by_mac[cur]["nodes"])

    # Remove filhos que fecham ciclo para garantir árvore finita
    def prune(node, seen):
        seen = seen | {node["mac"]}
        node["nodes"] = [c for c in node["nodes"] if c["mac"] not in seen]
        node["nodes"].sort(key=lambda c: (c.get("layer") or 99, str(c.get("id") or c["mac"])))
        for c in node["nodes"]:
            prune(c, seen)

    root = by_mac[root_mac]
    prune(root, set())

    # Órfãos: nós cujo pai não foi encontrado na topologia. Levam sua subárvore junto.
    unreachable = [n for mac, n in by_mac.items() if mac not in reachable]
    orphans = []
    covered = set()
    for n in sorted(unreachable, key=lambda n: (n.get("layer") or 99, n["mac"])):
        if n.get("parent_mac") is None:
            prune(n, set())
            orphans.append(n)
            stack = [n]
            while stack:
                cur = stack.pop()
                covered.add(cur["mac"])
                stack.extend(cur["nodes"])
    # Restos (ciclos entre nós sem ligação ao ROOT) entram soltos
    for n in unreachable:
        if n["mac"] not in covered:
            orphans.append({**n, "nodes": []})

    return {"root": root, "orphans": orphans, "edges": edges}
