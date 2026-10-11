import os
import json
import socket
import asyncio
from datetime import datetime
from typing import List, Optional, Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import paho.mqtt.client as mqtt
from commands_data import CODAX_COMMANDS

# ================= CONFIGURAÇÕES =================
BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("BROKER_PORT", 1883))
WEB_PORT = int(os.getenv("WEB_PORT", 8000))
FIRMWARE_DIR = os.path.abspath("./firmware")

# Tópicos
CMD_TOPIC_PROD = "config/shopba/mesh"
CMD_TOPIC_DEV = "dev/config/shopba/mesh"

ADDR_ROOT = "ff0000010000"
ADDR_ANY = "ffffffffffff"
ADDR_BROADCAST = "fffffffffe"

os.makedirs(FIRMWARE_DIR, exist_ok=True)

# Helper para obter o IP local da máquina
def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

# ================= FASTAPI & ESTADO GLOBAL =================
app = FastAPI(title="Codax Mesh IoT & OTA Hub")

# Servir arquivos de firmware diretamente para download OTA (HTTP GET)
app.mount("/firmware", StaticFiles(directory=FIRMWARE_DIR), name="firmware")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()

# Estado da Aplicação
app_state = {
    "current_env": "PROD",
    "broker_connected": False,
    "local_ip": LOCAL_IP,
    "web_port": WEB_PORT,
    "recent_messages": [],
    "nodes": {},
    "last_topology": None,
    "subscribed_topics": ["#"]
}

# ================= CADASTRO & REGISTRO DE MEDIDORES =================
DEVICES_FILE = os.path.abspath("./devices.json")

def load_devices() -> Dict[str, Dict[str, Any]]:
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DISPOSITIVOS] Erro ao ler {DEVICES_FILE}: {e}")
    # Dispositivos padrão pré-carregados para facilitar bancada
    defaults = {
        "4417934f49a4": {
            "mac": "4417934f49a4",
            "name": "ROOT Laboratório (Principal)",
            "meter_serial": "MED-LAB-01",
            "meter_type": "ABNT NBR 14522",
            "role": "ROOT",
            "notes": "Controladora principal conectada ao Wi-Fi"
        },
        "44179358768c": {
            "mac": "44179358768c",
            "name": "Medidor Bancada 01 (Nó L2)",
            "meter_serial": "MED-01-BANCADA",
            "meter_type": "Modbus RTU",
            "role": "NODE",
            "notes": "Medidor na bancada de testes 1"
        },
        "441793516dcc": {
            "mac": "441793516dcc",
            "name": "Medidor Bancada 02 (Nó L3)",
            "meter_serial": "MED-02-BANCADA",
            "meter_type": "Pulso",
            "role": "NODE",
            "notes": "Medidor secundário com sensor de pulsos"
        }
    }
    save_devices(defaults)
    return defaults

def save_devices(devices_dict: Dict[str, Dict[str, Any]]):
    try:
        with open(DEVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(devices_dict, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[DISPOSITIVOS] Erro ao salvar {DEVICES_FILE}: {e}")

class DeviceModel(BaseModel):
    mac: str
    name: str
    meter_serial: Optional[str] = ""
    meter_type: Optional[str] = "ABNT NBR 14522"
    role: Optional[str] = "NODE"
    notes: Optional[str] = ""

# ================= REGRAS DE COMANDO & MESH =================
def normalize_mac(mac: str) -> str:
    return mac.replace(":", "").strip().lower()

def resolve_mac_alias(mac: str) -> str:
    m = mac.strip().lower()
    if m == "root":
        return ADDR_ROOT
    elif m == "any":
        return ADDR_ANY
    elif m == "broadcast":
        return ADDR_BROADCAST
    
    # Verificar se o usuário passou o nome amigável de um medidor cadastrado
    devices = load_devices()
    for d_mac, d_info in devices.items():
        if m == d_info.get("name", "").strip().lower():
            return d_mac

    return normalize_mac(mac)

class MeshCommandRequest(BaseModel):
    addr: List[str]
    method: str
    function: str
    value: Optional[Any] = None
    for_mesh: Optional[bool] = False
    env: Optional[str] = "PROD"

class MqttPublishRequest(BaseModel):
    topic: str
    payload: Any
    qos: Optional[int] = 0
    retain: Optional[bool] = False

class MqttSubscribeRequest(BaseModel):
    topic: str
    qos: Optional[int] = 0

def build_payload(addrs: List[str], method: str, function: str, value: Any = None, for_mesh: bool = False) -> Dict[str, Any]:
    seen = set()
    cleaned = []
    for m in addrs:
        norm = resolve_mac_alias(m)
        if norm and norm not in seen:
            seen.add(norm)
            cleaned.append(norm)

    if not cleaned:
        raise ValueError("Lista de endereços MAC não pode ser vazia.")

    payload = {
        "addr": cleaned,
        "data": {
            "method": method.lower(),
            "function": function.lower()
        }
    }
    if for_mesh:
        payload["for_mesh"] = True
    if value is not None:
        payload["data"]["value"] = value

    return payload

# ================= CLIENTE MQTT =================
mqtt_loop = None

def on_mqtt_connect(client, userdata, flags, rc):
    app_state["broker_connected"] = (rc == 0)
    print(f"[MQTT] Conectado ao Broker na porta {BROKER_PORT} (Código {rc})")
    for topic in app_state["subscribed_topics"]:
        client.subscribe(topic)

def on_mqtt_disconnect(client, userdata, rc):
    app_state["broker_connected"] = False
    print(f"[MQTT] Desconectado do Broker (Código {rc})")

def categorize_topic(topic: str) -> str:
    t = topic.lower()
    if "retorno" in t:
        return "retorno"
    elif "telemetria" in t:
        return "telemetria"
    elif "topo" in t:
        return "topologia"
    elif "err" in t:
        return "erro"
    elif "conn" in t:
        return "conexao"
    elif "config" in t:
        return "configuracao"
    return "mensagem"

def register_discovered_node(mac_candidate: str, timestamp: str, layer: int = None, parent_mac: str = None, rssi: int = None, data: Any = None, topic: str = None):
    m = normalize_mac(mac_candidate)
    if not m or len(m) != 12 or m.startswith("ff") or not all(c in "0123456789abcdef" for c in m):
        return
    existing = app_state["nodes"].get(m, {})
    app_state["nodes"][m] = {
        "mac": m,
        "last_seen": timestamp,
        "status": "online",
        "layer": layer if layer is not None else existing.get("layer", 1 if ("root" in str(topic).lower() or layer == 1) else 2),
        "parent_mac": parent_mac or existing.get("parent_mac"),
        "rssi": rssi if rssi is not None else existing.get("rssi"),
        "last_topic": topic or existing.get("last_topic"),
        "data": data or existing.get("data")
    }

def extract_macs_recursive(obj, timestamp: str, topic: str, layer: int = None, parent_mac: str = None):
    if isinstance(obj, dict):
        m = obj.get("mac_addr") or obj.get("addr") or obj.get("id")
        curr_layer = obj.get("layer", layer)
        curr_parent = obj.get("parent_mac", parent_mac)
        curr_rssi = obj.get("parent_rssi") or obj.get("router_rssi")

        if isinstance(m, list):
            for item_m in m:
                if isinstance(item_m, str):
                    register_discovered_node(item_m, timestamp, curr_layer, curr_parent, curr_rssi, obj, topic)
        elif isinstance(m, str):
            register_discovered_node(m, timestamp, curr_layer, curr_parent, curr_rssi, obj, topic)

        curr_mac_str = normalize_mac(obj.get("mac_addr", "")) if obj.get("mac_addr") else parent_mac

        for k, v in obj.items():
            if k == "nodes" and isinstance(v, list):
                for child in v:
                    extract_macs_recursive(child, timestamp, topic, layer=(curr_layer + 1) if curr_layer else 2, parent_mac=curr_mac_str)
            elif isinstance(v, (dict, list)):
                extract_macs_recursive(v, timestamp, topic, layer=curr_layer, parent_mac=curr_mac_str)
    elif isinstance(obj, list):
        for item in obj:
            extract_macs_recursive(item, timestamp, topic, layer=layer, parent_mac=parent_mac)

def on_mqtt_message(client, userdata, msg):
    try:
        raw_payload = msg.payload.decode("utf-8", errors="ignore")
        topic = msg.topic
        category = categorize_topic(topic)
        timestamp = datetime.now().strftime("%H:%M:%S")

        parsed_json = None
        try:
            parsed_json = json.loads(raw_payload)
        except Exception:
            pass

        # 1. Descobrir MAC a partir do tópico (ex: retorno/shopba/mesh/4417934f49a4)
        topic_parts = topic.strip().split('/')
        if topic_parts:
            register_discovered_node(topic_parts[-1], timestamp, topic=topic)

        # 2. Descobrir MACs e árvore de nós recursivamente no JSON recebido
        if parsed_json:
            extract_macs_recursive(parsed_json, timestamp, topic)
            if category == "topologia":
                app_state["last_topology"] = {
                    "timestamp": timestamp,
                    "data": parsed_json
                }

        msg_record = {
            "timestamp": timestamp,
            "topic": topic,
            "category": category,
            "payload": parsed_json if parsed_json is not None else raw_payload,
            "raw": raw_payload
        }

        # Guardar histórico recente (máximo 250)
        app_state["recent_messages"].append(msg_record)
        if len(app_state["recent_messages"]) > 250:
            app_state["recent_messages"].pop(0)

        # Transmitir via WebSocket para o navegador se houver loop rodando
        if mqtt_loop and mqtt_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast({"type": "mqtt_message", "message": msg_record}),
                mqtt_loop
            )

    except Exception as e:
        print(f"[MQTT] Erro ao processar mensagem: {e}")

try:
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
except Exception:
    mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_mqtt_connect
mqtt_client.on_disconnect = on_mqtt_disconnect
mqtt_client.on_message = on_mqtt_message

@app.on_event("startup")
async def startup_event():
    global mqtt_loop
    mqtt_loop = asyncio.get_event_loop()
    try:
        mqtt_client.connect_async(BROKER_HOST, BROKER_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"[MQTT] Aviso: Não foi possível conectar ao broker imediatamente ({e}). Tentará reconectar.")

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

# ================= ROTAS DE API =================
@app.get("/api/status")
def get_status():
    return {
        "broker_connected": app_state["broker_connected"],
        "local_ip": app_state["local_ip"],
        "web_port": app_state["web_port"],
        "current_env": app_state["current_env"],
        "active_topic": CMD_TOPIC_PROD if app_state["current_env"] == "PROD" else CMD_TOPIC_DEV,
        "nodes_count": len(app_state["nodes"]),
        "messages_count": len(app_state["recent_messages"]),
        "subscriptions": app_state["subscribed_topics"]
    }

@app.post("/api/env/toggle")
def toggle_env():
    app_state["current_env"] = "DEV" if app_state["current_env"] == "PROD" else "PROD"
    return {
        "current_env": app_state["current_env"],
        "active_topic": CMD_TOPIC_PROD if app_state["current_env"] == "PROD" else CMD_TOPIC_DEV
    }

@app.get("/api/messages")
def get_messages():
    return app_state["recent_messages"]

@app.post("/api/messages/clear")
def clear_messages():
    app_state["recent_messages"].clear()
    return {"status": "cleared"}

@app.post("/api/command/send")
def send_command(req: MeshCommandRequest):
    try:
        payload = build_payload(
            addrs=req.addr,
            method=req.method,
            function=req.function,
            value=req.value,
            for_mesh=req.for_mesh
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    topic = CMD_TOPIC_PROD if req.env.upper() == "PROD" else CMD_TOPIC_DEV
    payload_str = json.dumps(payload)

    res = mqtt_client.publish(topic, payload_str)
    return {
        "status": "success" if res.rc == mqtt.MQTT_ERR_SUCCESS else "queued",
        "topic": topic,
        "payload": payload
    }

# ================= ROTAS MQTT (PUBLICADOR & ASSINANTE) =================
@app.post("/api/mqtt/publish")
def custom_publish(req: MqttPublishRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Tópico não pode ser vazio.")
    
    body = req.payload
    if isinstance(body, (dict, list)):
        payload_str = json.dumps(body)
    else:
        payload_str = str(body)

    res = mqtt_client.publish(req.topic.strip(), payload_str, qos=req.qos, retain=req.retain)
    return {
        "status": "success" if res.rc == mqtt.MQTT_ERR_SUCCESS else "queued",
        "topic": req.topic,
        "payload": req.payload,
        "qos": req.qos,
        "retain": req.retain
    }

@app.post("/api/mqtt/subscribe")
def custom_subscribe(req: MqttSubscribeRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Tópico não pode ser vazio.")

    if topic not in app_state["subscribed_topics"]:
        app_state["subscribed_topics"].append(topic)
        mqtt_client.subscribe(topic, qos=req.qos)

    return {
        "status": "subscribed",
        "topic": topic,
        "subscriptions": app_state["subscribed_topics"]
    }

@app.post("/api/mqtt/unsubscribe")
def custom_unsubscribe(req: MqttSubscribeRequest):
    topic = req.topic.strip()
    if topic in app_state["subscribed_topics"]:
        app_state["subscribed_topics"].remove(topic)
        mqtt_client.unsubscribe(topic)

    return {
        "status": "unsubscribed",
        "topic": topic,
        "subscriptions": app_state["subscribed_topics"]
    }

@app.get("/api/mqtt/subscriptions")
def get_subscriptions():
    return {
        "subscriptions": app_state["subscribed_topics"]
    }

# ================= CENTRAL DE OTA =================
@app.get("/api/firmware/list")
def list_firmwares():
    files = []
    if os.path.exists(FIRMWARE_DIR):
        for fname in os.listdir(FIRMWARE_DIR):
            fpath = os.path.join(FIRMWARE_DIR, fname)
            if os.path.isfile(fpath):
                stat = os.stat(fpath)
                files.append({
                    "name": fname,
                    "size_bytes": stat.st_size,
                    "size_formatted": f"{stat.st_size / (1024 * 1024):.2f} MB" if stat.st_size >= 1024*1024 else f"{stat.st_size / 1024:.1f} KB",
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S"),
                    "url": f"http://{app_state['local_ip']}:{app_state['web_port']}/firmware/{fname}"
                })
    return files

@app.post("/api/firmware/upload")
async def upload_firmware(file: UploadFile = File(...)):
    if not file.filename.endswith(".bin"):
        raise HTTPException(status_code=400, detail="Apenas arquivos com extensão .bin são aceitos.")

    target_path = os.path.join(FIRMWARE_DIR, file.filename)
    with open(target_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {
        "filename": file.filename,
        "url": f"http://{app_state['local_ip']}:{app_state['web_port']}/firmware/{file.filename}"
    }

@app.post("/api/ota/start")
def start_ota(
    filename: str = Form(...),
    target_addr: str = Form("any"),
    block: int = Form(1),
    env: str = Form("PROD")
):
    target_path = os.path.join(FIRMWARE_DIR, filename)
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Arquivo binário não encontrado no servidor.")

    ota_url = f"http://{app_state['local_ip']}:{app_state['web_port']}/firmware/{filename}"

    try:
        payload = build_payload(
            addrs=[target_addr],
            method="change",
            function="update_firmware",
            value={
                "link": ota_url,
                "protocol": "HTTP",
                "addr": ["ffffffffffff"],
                "block": block
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    topic = CMD_TOPIC_PROD if env.upper() == "PROD" else CMD_TOPIC_DEV
    res = mqtt_client.publish(topic, json.dumps(payload))

    return {
        "status": "success" if res.rc == mqtt.MQTT_ERR_SUCCESS else "queued",
        "topic": topic,
        "ota_url": ota_url,
        "payload": payload
    }

# ================= TOPOLOGIA & MOCK =================
@app.get("/api/topology")
def get_topology():
    return {
        "topology": app_state["last_topology"],
        "nodes": app_state["nodes"]
    }

@app.post("/api/topology/mock")
def generate_mock_topology():
    mock_data = {
        "layer": 1,
        "id": "ROOT_01",
        "mac_addr": "4417934f49a4",
        "router_ssid": "LAB_LEDAX_IOT",
        "router_mac_addr": "24:4b:fe:11:22:33",
        "router_rssi": -52,
        "channel": 6,
        "ip": "192.168.1.150",
        "nodes": [
            {
                "layer": 2,
                "id": "NODE_02",
                "mac_addr": "44179358768c",
                "parent_id": "ROOT_01",
                "parent_mac": "4417934f49a4",
                "parent_rssi": -63,
                "nodes": [
                    {
                        "layer": 3,
                        "id": "NODE_03",
                        "mac_addr": "441793516dcc",
                        "parent_id": "NODE_02",
                        "parent_mac": "44179358768c",
                        "parent_rssi": -74,
                        "nodes": []
                    }
                ]
            },
            {
                "layer": 2,
                "id": "NODE_04",
                "mac_addr": "4417934f4fd8",
                "parent_id": "ROOT_01",
                "parent_mac": "4417934f49a4",
                "parent_rssi": -58,
                "nodes": []
            }
        ]
    }
    app_state["last_topology"] = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "data": mock_data
    }
    extract_macs_recursive(mock_data, datetime.now().strftime("%H:%M:%S"), "mock_topology")
    return mock_data

# ================= ROTAS DE MEDIDORES & DISPOSITIVOS =================
@app.get("/api/devices")
def get_registered_devices():
    devices = load_devices()
    result = []
    for mac, dev in devices.items():
        live = app_state["nodes"].get(mac, {})
        merged = {
            **dev,
            "status": live.get("status", "offline"),
            "last_seen": live.get("last_seen", "Desconhecido"),
            "layer": live.get("layer", 1 if dev.get("role") == "ROOT" else 2),
            "parent_mac": live.get("parent_mac"),
            "rssi": live.get("rssi")
        }
        result.append(merged)
    result.sort(key=lambda d: (0 if d.get("role") == "ROOT" else 1, d.get("name", "").lower()))
    return result

@app.post("/api/devices")
def create_or_update_device(dev: DeviceModel):
    devices = load_devices()
    norm_mac = normalize_mac(dev.mac)
    if not norm_mac or len(norm_mac) != 12:
        raise HTTPException(status_code=400, detail="MAC Address inválido. Deve ter exatamente 12 dígitos hexadecimais.")

    devices[norm_mac] = {
        "mac": norm_mac,
        "name": dev.name.strip() or f"Dispositivo {norm_mac}",
        "meter_serial": (dev.meter_serial or "").strip(),
        "meter_type": dev.meter_type or "ABNT NBR 14522",
        "role": (dev.role or "NODE").upper(),
        "notes": (dev.notes or "").strip()
    }
    save_devices(devices)
    return {"status": "saved", "device": devices[norm_mac]}

@app.delete("/api/devices/{mac}")
def delete_registered_device(mac: str):
    devices = load_devices()
    norm_mac = normalize_mac(mac)
    if norm_mac in devices:
        deleted = devices.pop(norm_mac)
        save_devices(devices)
        return {"status": "deleted", "mac": norm_mac}
    raise HTTPException(status_code=404, detail="Dispositivo não encontrado no cadastro.")

@app.get("/api/discovered")
def get_discovered_devices():
    devices = load_devices()
    discovered = []
    for mac, node in app_state["nodes"].items():
        is_registered = mac in devices
        discovered.append({
            "mac": mac,
            "registered": is_registered,
            "name": devices[mac]["name"] if is_registered else f"Nó Descoberto {mac[-4:].upper()}",
            "role": devices[mac]["role"] if is_registered else ("ROOT" if node.get("layer") == 1 else "NODE"),
            "meter_serial": devices[mac].get("meter_serial", "") if is_registered else "",
            "meter_type": devices[mac].get("meter_type", "") if is_registered else "",
            "layer": node.get("layer", 2),
            "parent_mac": node.get("parent_mac"),
            "rssi": node.get("rssi"),
            "last_seen": node.get("last_seen", "Agora"),
            "last_topic": node.get("last_topic")
        })
    return discovered

# ================= DICIONÁRIO DE TÓPICOS =================
@app.get("/api/topics/docs")
def get_topics_documentation():
    return [
        {
            "category": "Comandos & Configuração",
            "topic": "config/shopba/mesh",
            "dev_topic": "dev/config/shopba/mesh",
            "direction": "Servidor ➡️ Controladoras",
            "description": "Tópico de entrada principal onde as controladoras ROOT escutam comandos, consultas e alterações de configuração (JSON Template com addr, method, function e value).",
            "payload_example": '{"addr":["4417934f49a4"], "data":{"method":"query", "function":"ping"}}'
        },
        {
            "category": "Retorno de Comandos",
            "topic": "retorno/shopba/mesh/#",
            "dev_topic": "dev/retorno/shopba/mesh/#",
            "direction": "Controladoras ➡️ Servidor",
            "description": "Respostas imediatas das controladoras após receberem e executarem qualquer comando (query, change ou setting). Contém o resultado ou erro.",
            "payload_example": '{"addr":"4417934f49a4", "data":{"function":"ping", "layer":1, "parent_rssi":-55}}'
        },
        {
            "category": "Telemetria & Leituras",
            "topic": "telemetria/shopba/mesh/#",
            "dev_topic": "dev/telemetria/shopba/mesh/#",
            "direction": "Controladoras ➡️ Servidor",
            "description": "Leituras periódicas dos medidores (totalizadores de energia, pulsos, temperatura DS18B20, status liga/desliga, etc). Pode conter o array tel_json em tempo real ou reenvio de arquivos do LittleFS.",
            "payload_example": '{"id":"maquina01", "tel_json":[{"timestamp":1700000000, "total":12450.32}]}'
        },
        {
            "category": "Topologia da Malha",
            "topic": "topo/shopba/mesh/#",
            "dev_topic": "dev/topo/shopba/mesh/#",
            "direction": "Controladora ROOT ➡️ Servidor",
            "description": "Publicação do mapa completo da rede mesh (árvore de nós, camadas, RSSI do roteador, canal e vizinhos). Enviado periodicamente ou quando requisitado por query/topology.",
            "payload_example": '{"layer":1, "mac_addr":"4417934f49a4", "nodes":[{"layer":2, "mac_addr":"44179358768c"}]}'
        },
        {
            "category": "Conexão & Heartbeat",
            "topic": "conn/shopba/mesh/#",
            "dev_topic": "dev/conn/shopba/mesh/#",
            "direction": "Controladoras ➡️ Servidor",
            "description": "Mensagens de conexão e desconexão (LWT - Last Will and Testament), além de avisos de reinicialização com código esp_reset_reason ('Power on - reason N') e diagnósticos de reset.",
            "payload_example": '{"addr":"4417934f49a4", "data":{"id":"ND", "message":"Disconnected from broker"}}'
        },
        {
            "category": "Erros & Debug de Barramento",
            "topic": "err/shopba/mesh/#",
            "dev_topic": "dev/err/shopba/mesh/#",
            "direction": "Controladoras ➡️ Servidor",
            "description": "Logs de erro da controladora e frames brutos capturados pelo raw_debug (RS485, Modbus UDP, ABNT 14522, PIMA). Permite ver frames truncados ou sem resposta.",
            "payload_example": '{"proto":"modbus_udp", "f":[{"id":"medidor1", "tx":"0103008a0002e5e1", "rx":""}], "drop":0}'
        }
    ]

@app.get("/api/commands/docs")
def get_commands_documentation():
    return CODAX_COMMANDS

@app.get("/api/spec/rules")
def get_specification_rules():
    return {
        "mesh_password": "QNfW7kyR1bAM",
        "definitions": [
            {
                "term": "ROOT",
                "badge": "Camada 1 (Bridge)",
                "description": "Controladora da rede mesh que possui capacidade e credenciais para se conectar diretamente ao roteador Wi-Fi. É o nó de ponte que encaminha todo o tráfego MQTT da malha para o Broker."
            },
            {
                "term": "NODE",
                "badge": "Camada 2 ou inferior",
                "description": "Controladora da rede mesh que não é o ROOT. Conecta-se a um nó pai (parent) de camada superior através de saltos mesh seguros sem tocar no roteador Wi-Fi."
            },
            {
                "term": "IDLE",
                "badge": "Aguardando Associação",
                "description": "Controladora em estado inicial que pode se tornar NODE (se encontrar uma rede mesh ativa) ou ROOT (se encontrar o roteador Wi-Fi configurado)."
            }
        ],
        "special_addresses": [
            {
                "name": "ROOTs Only",
                "mac": "ff:00:00:01:00:00",
                "clean_mac": "ff0000010000",
                "description": "Envia a mensagem exclusivamente para as controladoras raiz (ROOTs) conectadas."
            },
            {
                "name": "Broadcast Geral (ANY)",
                "mac": "ff:ff:ff:ff:ff:ff",
                "clean_mac": "ffffffffffff",
                "description": "Envia a mensagem para TODAS as controladoras da rede mesh (ROOTs e todos os nós)."
            },
            {
                "name": "Broadcast NODEs",
                "mac": "ff:ff:ff:ff:ff:fe",
                "clean_mac": "fffffffffe",
                "description": "Envia a mensagem para todas as controladoras conectadas, EXCETO as ROOTs."
            }
        ],
        "cautions": [
            {
                "level": "critical",
                "title": "AVISO CRÍTICO: Prevenção contra Crash do ESP32",
                "text": "Se forem enviados endereços MAC duplicados na lista 'addr' de qualquer comando MQTT ou no 'mupgrade', o sistema da controladora pode crashar imediatamente! O servidor Codax Hub remove duplicatas automaticamente."
            },
            {
                "level": "info",
                "title": "Resposta Obrigatória",
                "text": "É esperado que as controladoras conectadas sempre respondam a qualquer mensagem recebida no tópico de comando, seja com o resultado positivo esperado ou com um payload de erro detalhado."
            },
            {
                "level": "info",
                "title": "Mensagens de Progresso em Processos Longos",
                "text": "Operações multi-etapas como 'mupgrade' (atualização de firmware) e troca de rede Wi-Fi devem emitir mensagens periódicas de progresso antes da conclusão."
            },
            {
                "level": "tip",
                "title": "Case-Insensitive & Formato de MAC",
                "text": "Os métodos ('method') e as funções ('function') são case insensitive no firmware. Os endereços MAC podem ser enviados com ou sem dois-pontos ':'."
            },
            {
                "level": "tip",
                "title": "Campo 'for_mesh' (Booleano Opcional)",
                "text": "O objeto 'for_mesh' serve para identificar se uma mensagem é para todas as controladoras que compartilham a mesma malha dos nós listados em 'addr'. Se omitido, o padrão é false."
            },
            {
                "level": "tip",
                "title": "Campo 'type' (Opcional)",
                "text": "Por padrão, mensagens omitidas são tratadas como 'type':'json'. Suporta 'string' ou 'bytes' para expansões futuras como OTA binário direto via MQTT."
            }
        ],
        "template": {
            "addr": ["4417934f49a4", "44179358768c"],
            "for_mesh": False,
            "type": "json",
            "data": {
                "method": "XXXX",
                "function": "YYYY",
                "value": "ZZZZ"
            }
        }
    }

@app.get("/api/nodes")
def get_active_nodes():
    return list(app_state["nodes"].keys())

# ================= WEBSOCKET =================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    await websocket.send_json({
        "type": "init",
        "status": {
            "broker_connected": app_state["broker_connected"],
            "local_ip": app_state["local_ip"],
            "web_port": app_state["web_port"],
            "current_env": app_state["current_env"],
            "active_topic": CMD_TOPIC_PROD if app_state["current_env"] == "PROD" else CMD_TOPIC_DEV,
            "subscriptions": app_state["subscribed_topics"]
        },
        "recent_messages": app_state["recent_messages"]
    })
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# ================= PÁGINA WEB DASHBOARD =================
@app.get("/", response_class=HTMLResponse)
def index_page():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Dashboard em construção...</h1>"

if __name__ == "__main__":
    import uvicorn
    print(f"Iniciando Codax Hub em: http://{LOCAL_IP}:{WEB_PORT}")
    uvicorn.run("app:app", host="0.0.0.0", port=WEB_PORT, reload=False)
