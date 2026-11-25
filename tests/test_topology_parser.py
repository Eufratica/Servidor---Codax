"""
Teste isolado do parser de topologia (lógica pura, sem MQTT/rede).
Executar:  python tests/test_topology_parser.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from topology_parser import parse_topology_payload, build_mesh_tree, clean_mac  # noqa: E402

# Payload REAL capturado na bancada em 19/11/2026 (dev/topo/shopba/mesh/704bca491d9c)
REAL = {
    "page": 1, "root": "70:4b:ca:49:1d:9c(Teste)", "router_mac": "bc:07:1d:57:11:76",
    "router_rssi(dB)": -52, "total_devices": 2,
    "mesh": [
        "|layer: 1|mac: 70:4b:ca:49:1d:9c|id: Teste             |parent_id: 0                 |rssi: -52 |",
        "|layer: 2|mac: 30:83:98:63:50:b0|id: 30:83:98:63:50:b0 |parent_id: Teste             |rssi: -20 |",
    ],
}


def flatten(node, depth=0, out=None):
    out = [] if out is None else out
    out.append((node["mac"], node.get("layer"), node.get("parent_mac")))
    for c in node["nodes"]:
        flatten(c, depth + 1, out)
    return out


def test_real_payload():
    p = parse_topology_payload(REAL)
    assert p["root_mac"] == "704bca491d9c"
    assert p["root_id"] == "Teste"
    assert p["router_mac"] == "bc071d571176"
    assert p["router_rssi"] == -52
    assert p["total_devices"] == 2
    assert len(p["entries"]) == 2
    assert p["entries"][1]["parent_ref"] == "Teste"

    t = build_mesh_tree(p["root_mac"], p["entries"])
    assert t["orphans"] == []
    assert flatten(t["root"]) == [
        ("704bca491d9c", 1, None),
        ("30839863 50b0".replace(" ", ""), 2, "704bca491d9c"),
    ]


def test_three_layers_by_id_and_softap_mac():
    payload = {
        "page": 1, "root": "aa:00:00:00:00:10(R)", "total_devices": 5,
        "mesh": [
            "|layer: 1|mac: aa:00:00:00:00:10|id: R |parent_id: 0 |rssi: -40 |",
            "|layer: 2|mac: aa:00:00:00:00:20|id: N2 |parent_id: R |rssi: -50 |",
            # pai informado pelo MAC SoftAP (STA + 1)
            "|layer: 2|mac: aa:00:00:00:00:30|id: aa:00:00:00:00:30 |parent_id: aa:00:00:00:00:11 |rssi: -55 |",
            "|layer: 3|mac: aa:00:00:00:00:40|id: N4 |parent_id: N2 |rssi: -70 |",
            "|layer: 4|mac: aa:00:00:00:00:50|id: N5 |parent_id: N4 |rssi: -80 |",
        ],
    }
    p = parse_topology_payload(payload)
    t = build_mesh_tree(p["root_mac"], p["entries"])
    flat = {mac: (layer, parent) for mac, layer, parent in flatten(t["root"])}
    assert flat["aa0000000020"] == (2, "aa0000000010")
    assert flat["aa0000000030"] == (2, "aa0000000010")
    assert flat["aa0000000040"] == (3, "aa0000000020")
    assert flat["aa0000000050"] == (4, "aa0000000040")
    assert t["orphans"] == []


def test_orphan_keeps_subtree():
    payload = {
        "root": "aa:00:00:00:00:10(R)",
        "mesh": [
            "|layer: 1|mac: aa:00:00:00:00:10|id: R |parent_id: 0 |rssi: -40 |",
            "|layer: 3|mac: aa:00:00:00:00:40|id: N4 |parent_id: SUMIU |rssi: -70 |",
            "|layer: 4|mac: aa:00:00:00:00:50|id: N5 |parent_id: N4 |rssi: -80 |",
        ],
    }
    p = parse_topology_payload(payload)
    t = build_mesh_tree(p["root_mac"], p["entries"])
    assert t["root"]["nodes"] == []
    assert len(t["orphans"]) == 1
    o = t["orphans"][0]
    assert o["mac"] == "aa0000000040" and o["parent_ref"] == "SUMIU"
    assert [c["mac"] for c in o["nodes"]] == ["aa0000000050"]


def test_non_topology_payloads():
    assert parse_topology_payload({"data": {"message": "hb parent=70:4b:ca:49:1d:9d layer=2 rssi=-19"}}) is None
    assert parse_topology_payload("texto") is None
    assert parse_topology_payload({"mesh": []}) is None


def test_clean_mac_rejects_names():
    assert clean_mac("Teste") is None
    assert clean_mac("70:4b:ca:49:1d:9c(Teste)") == "704bca491d9c"
    assert clean_mac("0") is None


def test_cycle_does_not_hang():
    payload = {
        "root": "aa:00:00:00:00:10(R)",
        "mesh": [
            "|layer: 1|mac: aa:00:00:00:00:10|id: R |parent_id: 0 |rssi: -40 |",
            "|layer: 2|mac: aa:00:00:00:00:20|id: A |parent_id: B |rssi: -50 |",
            "|layer: 2|mac: aa:00:00:00:00:30|id: B |parent_id: A |rssi: -50 |",
        ],
    }
    p = parse_topology_payload(payload)
    t = build_mesh_tree(p["root_mac"], p["entries"])
    assert {o["mac"] for o in t["orphans"]} == {"aa0000000020", "aa0000000030"}


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"OK  {fn.__name__}")
    print(f"\n{len(tests)} testes passaram.")
