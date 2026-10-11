import os
import sys
import time
import socket
import webbrowser
import subprocess
import uvicorn

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def free_port(port: int):
    try:
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True, text=True)
        my_pid = os.getpid()
        for line in output.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) >= 5 and "LISTENING" in line:
                pid = int(parts[-1])
                if pid != my_pid and pid > 0:
                    print(f"      Liberando porta {port} (encerrando PID antigo {pid})...")
                    subprocess.call(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(1)
    except Exception:
        pass

def main():
    print("=" * 65)
    print("      🚀 INICIANDO CODAX MESH HUB (ON-PREMISE SERVER)")
    print("=" * 65)

    # Liberar porta 8000 se houver processo antigo preso
    free_port(8000)

    local_ip = get_local_ip()

    # 1. Verificar Broker MQTT (Porta 1883)
    if not is_port_open(1883):
        print("[1/3] Broker MQTT (1883) não detectado. Iniciando AMQTT...")
        try:
            subprocess.Popen([sys.executable, "-m", "amqtt.scripts.broker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            if is_port_open(1883):
                print("      ✅ Broker MQTT iniciado com sucesso na porta 1883!")
            else:
                print("      ⚠️ Aviso: Broker pode estar iniciando em segundo plano.")
        except Exception as e:
            print(f"      ❌ Erro ao iniciar broker automaticamente: {e}")
    else:
        print("[1/3] ✅ Broker MQTT já está ativo na porta 1883!")

    # 2. Informações de Conexão para o ESP32
    print("\n[2/3] 📋 DADOS PARA O MENUCONFIG DO SEU ESP32:")
    print(f"      • MQTT Broker URL : {local_ip}")
    print(f"      • Porta MQTT      : 1883 (TCP / Inseguro)")
    print(f"      • Servidor OTA    : http://{local_ip}:8000/firmware/<arquivo.bin>")
    
    # 3. Abrir Navegador e Iniciar FastAPI
    web_url = f"http://localhost:8000"
    print(f"\n[3/3] 🌐 Abrindo Dashboard no Navegador: {web_url}")
    print("=" * 65)
    print("  Pressione Ctrl+C para encerrar o servidor a qualquer momento.\n")

    def open_browser():
        time.sleep(1.5)
        webbrowser.open(web_url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Rodar FastAPI com reload para refletir alterações
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
