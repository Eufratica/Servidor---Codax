import os
import json
import threading
import http.server
import socketserver
import paho.mqtt.client as mqtt

# ================= CONFIGURAÇÕES =================
BROKER_HOST = "localhost"   # IP do broker MQTT (localhost ou IP da máquina)
BROKER_PORT = 1883
HTTP_PORT = 8080            # Porta HTTP onde os firmwares .bin ficam disponíveis
FIRMWARE_DIR = "./firmware"

# Tópico padrão onde a ROOT escuta os comandos
CURRENT_ENV = "PROD"
CMD_TOPIC_PROD = "config/shopba/mesh"
CMD_TOPIC_DEV = "dev/config/shopba/mesh"

# Endereços especiais definidos pelo firmware
ADDR_ROOT = "ff:00:00:01:00:00"
ADDR_ANY = "ff:ff:ff:ff:ff:ff"
ADDR_BROADCAST = "ff:ff:ff:ff:ff:fe"
# =================================================

os.makedirs(FIRMWARE_DIR, exist_ok=True)

# 1. SERVIDOR HTTP PARA OTA (Roda em segundo plano)
def run_http_server():
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=FIRMWARE_DIR, **kwargs)

    with socketserver.TCPServer(("", HTTP_PORT), CustomHandler) as httpd:
        print(f"[HTTP OTA] Servidor de firmware ativo em: http://0.0.0.0:{HTTP_PORT}/")
        print(f"[HTTP OTA] Coloque seus arquivos .bin na pasta '{FIRMWARE_DIR}'")
        httpd.serve_forever()

# 2. TRATAMENTO E FORMATAÇÃO DE COMANDOS
def normalize_mac(mac: str) -> str:
    return mac.replace(":", "").strip().lower()

def build_payload(addrs, method, function, value=None, for_mesh=False):
    # REGRA CRÍTICA: Deduplicar MACs para evitar que a controladora crashe!
    seen = set()
    cleaned_addrs = []
    for mac in addrs:
        norm = normalize_mac(mac)
        if norm and norm not in seen:
            seen.add(norm)
            cleaned_addrs.append(norm)

    if not cleaned_addrs:
        print("[ERRO] Lista de MACs vazia.")
        return None

    payload = {
        "addr": cleaned_addrs,
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

# 3. CLIENTE MQTT (ESCUTA E ENVIO)
def on_connect(client, userdata, flags, rc):
    print(f"\n[MQTT] Conectado ao Broker (Código: {rc})")
    # Escutamos a tudo (#) para ver telemetria, erros, conexão e retornos
    client.subscribe("#")
    print("[MQTT] Monitorando todos os tópicos (telemetria, conn, topo, err, retorno)...\n")

def on_message(client, userdata, msg):
    try:
        conteudo = msg.payload.decode('utf-8')
        try:
            parsed = json.loads(conteudo)
            conteudo = json.dumps(parsed, indent=2, ensure_ascii=False)
        except Exception:
            pass

        topic = msg.topic
        
        # Categorizando os Tópicos para leitura mais fácil no terminal
        prefix = "💬 [MENSAGEM]"
        if "retorno" in topic:
            prefix = "✅ [RETORNO]"
        elif "telemetria" in topic:
            prefix = "📊 [TELEMETRIA]"
        elif "topo" in topic:
            prefix = "🌳 [TOPOLOGIA]"
        elif "err" in topic:
            prefix = "❌ [ERRO]"
        elif "conn" in topic:
            prefix = "📡 [CONEXÃO]"

        print(f"\n\n{prefix} Tópico: {topic}\n{conteudo}\n[1=Query | 2=Change | 3=Setting | 4=OTA | env=Mudar Tópico] > ", end="")
    except Exception as e:
        print(f"\n[MQTT] Erro ao decodificar no tópico {msg.topic}: {e}\n> ", end="")

def main():
    global CURRENT_ENV
    
    # Inicia o servidor HTTP em uma thread paralela
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except Exception:
        client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"[ERRO] Falha ao conectar no Broker MQTT ({BROKER_HOST}:{BROKER_PORT}): {e}")
        return

    # CLI simples no terminal para enviar comandos
    print("=" * 60)
    print("  SERVIDOR CODAX MESH - PAINEL DE CONTROLE")
    print("  1: Enviar 'query' (Ex: ping, info, telemetry, root)")
    print("  2: Enviar 'change' (Ex: network, update_firmware, root, topology)")
    print("  3: Enviar 'setting' (Ex: device_config, meter, active_telemetry)")
    print("  4: Iniciar OTA via HTTP (Atalho rápido)")
    print("  env: Alternar ambiente de envio (DEV <-> PROD)")
    print("  sair: Encerrar servidor")
    print("=" * 60)

    while True:
        try:
            cmd_topic = CMD_TOPIC_PROD if CURRENT_ENV == "PROD" else CMD_TOPIC_DEV
            cmd = input(f"\n[{CURRENT_ENV}] [1=Query | 2=Change | 3=Setting | 4=OTA | env=Mudar] > ").strip().lower()
            
            if cmd == "sair":
                break
                
            elif cmd == "env":
                CURRENT_ENV = "DEV" if CURRENT_ENV == "PROD" else "PROD"
                print(f"Ambiente alterado para: {CURRENT_ENV}")
                continue
            
            elif cmd in ["1", "2", "3"]:
                mac_raw = input("MAC Address (ex: 4417934f49a4, 'root', 'any' ou 'broadcast'): ").strip()
                
                # Traduzir atalhos para os endereços especiais
                if mac_raw.lower() == "root":
                    macs = [ADDR_ROOT]
                elif mac_raw.lower() == "any":
                    macs = [ADDR_ANY]
                elif mac_raw.lower() == "broadcast":
                    macs = [ADDR_BROADCAST]
                else:
                    macs = [m.strip() for m in mac_raw.split(",")]

                methods = {"1": "query", "2": "change", "3": "setting"}
                method = methods[cmd]

                function = input(f"Digite a function para {method} (ex: info, ping, network...): ").strip()
                
                val_raw = input("Digite o 'value' (JSON ou texto, deixe vazio se não precisar): ").strip()
                
                val = None
                if val_raw:
                    try:
                        val = json.loads(val_raw)
                    except Exception:
                        val = val_raw

                payload = build_payload(macs, method, function, val)
                if payload:
                    client.publish(cmd_topic, json.dumps(payload))
                    print(f"\n[ENVIADO] Tópico: {cmd_topic}\nPayload: {json.dumps(payload, indent=2)}")

            elif cmd == "4":
                mac_raw = input("MAC alvo (ex: 'any' para ffffffffffff, ou um MAC específico): ").strip()
                if mac_raw.lower() == "any":
                    macs = [ADDR_ANY]
                else:
                    macs = [m.strip() for m in mac_raw.split(",")]

                nome_arquivo = input("Nome do arquivo .bin na pasta ./firmware (ex: codax-m.bin): ").strip()
                meu_ip = input("Digite o IP da sua máquina na rede local (ex: 192.168.1.50): ").strip()
                ota_url = f"http://{meu_ip}:{HTTP_PORT}/{nome_arquivo}"

                payload = build_payload(
                    addrs=macs,
                    method="change",
                    function="update_firmware",
                    value={
                        "link": ota_url,
                        "protocol": "HTTP",
                        "addr": ["ffffffffffff"],
                        "block": 1
                    }
                )
                if payload:
                    client.publish(cmd_topic, json.dumps(payload))
                    print(f"\n[ENVIADO OTA] Tópico: {cmd_topic}\nPayload: {json.dumps(payload, indent=2)}")

        except (KeyboardInterrupt, EOFError):
            break

    client.loop_stop()
    print("\nServidor encerrado.")

if __name__ == "__main__":
    main()
,