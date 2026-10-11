# 🌐 Codax Mesh Hub (Servidor On-Premise IoT & OTA)

Plataforma completa de servidor local e bancada de testes para redes **ESP-MESH (ESP32)** com telemetria de medidores, gestão de firmware (OTA HTTP), inspeção de tráfego MQTT e controle de comandos.

Desenvolvido para substituir com total autonomia infraestruturas de nuvem (AWS IoT Core, S3), funcionando de forma 100% **On-Premise**, resiliente e independente de internet.

---

## 🚀 Principais Funcionalidades

### 1. 🎛️ Construtor Interativo de Comandos Codax
* **Destinatários Avançados (Múltiplos Destinos):** Menu flutuante acionado por setinha (`chevron-down`) com checklist completa de alvos broadcast (`ROOT`, `ANY`, `BROADCAST`), medidores cadastrados e placas detectadas.
* **Chips Interativos de Medidores:** Selecione ou desmarque alvos diretamente clicando nos chips, com contador em tempo real (`X alvos selecionados`).
* **Proteção Anti-Crash de Firmware:** Normalização e deduplicação estrita de MACs (`Set` sem repetição de endereços), impedindo que o firmware do ESP32 trave por MAC duplicado.
* **Function com Busca Instantânea & Filtros:** Campo com botão de setinha expansível e filtros por categoria (`🌐 Rede & Mesh`, `⚡ Medidores`, `🛠️ Diagnóstico`, `📦 Sistema & OTA`), exibindo badges de tipo de valor e resumo técnico.
* **Catálogo Exaustivo (62 Comandos):** Autocomplete em tempo real para todos os métodos (`query`, `change`, `setting`) com documentação técnica, dicas e valores de exemplo.
* **Live JSON Preview & Formatação:** Visualização instantânea do JSON exato que será publicado no broker.

### 2. 🎚️ Topbar Moderna & Painel de Bancada na Barra Lateral
* **Barra Horizontal Primária:** Navegação completa de abas com design moderno SaaS, badges dinâmicos de contagem de medidores e console, indicador de IP do host, status do broker 1883 e alternador DEV/PROD.
* **Barra Lateral (Painel de Operações & Telemetria):** Eliminação de redundâncias visuais, transformando a lateral em monitor de bancada com contagem de nós em tempo real, tópico de comando ativo, seletor de alvo global, botões de emergência (`Ping Malha`, `Ler Topologia`, `mwifi_restart`) e mini-feed de retornos MQTT ao vivo.

### 3. ⚡ Cadastro Centralizado de Medidores & Placas
* **Identificação Amigável:** Associe o MAC da placa a nomes reais (ex: *ROOT Laboratório*, *Medidor Bancada 01*).
* **Campos Específicos de Medição:**
  * Número de Série do Medidor (ex: `MED-LAB-01`, `ABNT-998822`);
  * Protocolo e Interface (*ABNT NBR 14522*, *Modbus RTU/UDP*, *Pulso*, *DS18B20*, etc.);
  * Papel na Malha (*ROOT*, *NODE* ou *IDLE*);
  * Observações e localização física.
* **Persistência Permanente:** Dados salvos em `devices.json`.
* **Auto-Descoberta de Nós:** O servidor escuta o tráfego MQTT e a topologia. Ao detectar novos nós na rede, disponibiliza o botão `+ Cadastrar Este Nó` em 1 clique.

### 4. 🌳 Árvore Visual de Topologia Mesh
* **Renderização Gráfica por Camadas:** Exibe a hierarquia da malha (Camada 1 ROOT, Camada 2 nós intermediários, Camada 3 folhas).
* **Métricas de Link:** Intensidade de sinal RSSI do pai (*parent RSSI*), MACs de origem/destino e status online/offline.
* **Ação Direta:** Botão `Selecionar Alvo ⚡` no próprio cartão do nó da árvore para enviá-lo ao construtor de comandos.

### 5. 📖 Dicionário Oficial & Especificação de Arquitetura
* **Filtro "Regras & Arquitetura":**
  * Credencial global da malha: `QNfW7kyR1bAM` (com 1 clique para copiar);
  * Definições de papéis (`ROOT`, `NODE`, `IDLE`);
  * Endereços especiais:
    * `ROOTs Only`: `ff:00:00:01:00:00` (`ff0000010000`)
    * `Broadcast Geral (ANY)`: `ff:ff:ff:ff:ff:ff` (`ffffffffffff`)
    * `Broadcast NODEs`: `ff:ff:ff:ff:ff:fe` (`fffffffffe`)
  * Template oficial Codax e regras do protocolo (case-insensitivity, respostas obrigatórias, flags `for_mesh` e `type: json`).
* **Documentação Detalhada com Exemplos Práticos:**
  * `setting raw_debug`: Inclui os 5 exemplos de captura de frames brutos (sem filtro, por medidor, por IP, por grandeza e parada imediata), além de guia de diagnóstico de retry do RS485 (`a` de 0 a 24).
  * `query reset_diag_log`: Tabela com os 10 códigos de boot/reset do ESP-IDF v4.4.8 (`esp_reset_reason`).

### 6. 📦 Central de Firmware & OTA HTTP
* Upload de binários compilados (`.bin`) via interface ou arrastar-e-soltar.
* Servidor HTTP embutido para entrega de firmware de alta velocidade.
* Disparo de comando `mupgrade` apontando para o binário no servidor local com seleção de destino (`any`, `root` ou nó específico).

### 7. 📡 Console ao Vivo MQTT (WebSockets)
* Escuta em tempo real de todos os tópicos da malha.
* Filtros rápidos por categoria (*Retorno de Comandos*, *Telemetria*, *Topologia*, *Conexão*, *Erros de Barramento*).
* Busca textual dinâmica, formatação de payloads JSON e auto-scroll inteligente com pause.

### 8. 🔄 Alternador DEV / PROD
* Alterne entre tópicos de produção (`config/shopba/mesh`) e desenvolvimento (`dev/config/shopba/mesh`) com apenas um clique.

---

## 📊 Matriz de Tópicos MQTT

| Categoria | Tópico Produção | Tópico Desenvolvimento | Direção | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **Comandos** | `config/shopba/mesh` | `dev/config/shopba/mesh` | Servidor ➡️ Malha | Envio de JSONs para execução nas controladoras |
| **Retorno** | `retorno/shopba/mesh/#` | `dev/retorno/shopba/mesh/#` | Malha ➡️ Servidor | Respostas imediatas das controladoras para comandos |
| **Telemetria** | `telemetria/shopba/mesh/#` | `dev/telemetria/shopba/mesh/#` | Malha ➡️ Servidor | Leituras periódicas de medidores e grandezas |
| **Topologia** | `topo/shopba/mesh/#` | `dev/topo/shopba/mesh/#` | ROOT ➡️ Servidor | Mapa hierárquico da malha (pais, filhos, RSSI) |
| **Conexão** | `conn/shopba/mesh/#` | `dev/conn/shopba/mesh/#` | Malha ➡️ Servidor | Avisos de boot, LWT, reinicialização e disconnect |
| **Erros** | `err/shopba/mesh/#` | `dev/err/shopba/mesh/#` | Malha ➡️ Servidor | Frames brutos RS485/UDP capturados por `raw_debug` |

---

## 🛠️ Configuração no ESP32 (`menuconfig`)

Ao compilar o firmware no ESP-IDF, aponte os parâmetros de rede para o IP do computador rodando este servidor:

* **MQTT Broker URL:** `<IP_DO_SEU_PC>` (ex: `192.168.1.3` ou detectado no topo do Hub)
* **Porta MQTT:** `1883` (TCP / Inseguro)
* **Servidor OTA HTTP:** `http://<IP_DO_SEU_PC>:8000/firmware/<arquivo.bin>`
* **Mesh Password Padrão:** `QNfW7kyR1bAM`

---

## 💻 Instalação & Execução

### Pré-requisitos
* Python 3.8 ou superior instalado.
* Broker MQTT ativo na porta `1883` (o servidor inicia o `amqtt` embutido se nenhum outro broker estiver ativo, mas é totalmente compatível com Mosquitto).

### 1. Clonar o repositório
```bash
git clone https://github.com/Eufratica/Servidor---Codax.git
cd Servidor---Codax
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Iniciar o Servidor
* **No Windows (1-clique):**
  Dê dois cliques no arquivo `iniciar_servidor.bat` ou execute no terminal:
  ```cmd
  iniciar_servidor.bat
  ```

* **Ou via linha de comando:**
  ```bash
  python start_server.py
  ```

O sistema irá:
1. Verificar e disponibilizar o Broker MQTT na porta `1883`;
2. Detectar seu IP local na rede Wi-Fi/Ethernet;
3. Abrir automaticamente o Dashboard no navegador em: **[http://localhost:8000](http://localhost:8000)**.

---

## 📁 Estrutura do Projeto

```
C:\Servidor\
├── app.py                  # Backend FastAPI, API REST, WebSocket e cliente MQTT
├── commands_data.py        # Catálogo exaustivo com os 62 comandos Codax e exemplos
├── devices.json            # Base de dados permanente dos medidores e placas cadastradas
├── start_server.py         # Inicializador com verificação de portas, IP e abertura de browser
├── iniciar_servidor.bat    # Script de inicialização rápida em lote para Windows
├── requirements.txt        # Dependências do ecossistema Python
├── amqtt_config.yaml       # Configuração do broker MQTT local embutido
├── firmware/               # Diretório de armazenamento e entrega de binários (.bin) OTA
└── static/
    └── index.html          # Frontend responsivo SPA (Tailwind CSS, Lucide Icons, WebSocket)
```

---

## 🛡️ Segurança & Boas Práticas de Bancada
* **Deduplicação de MACs:** O servidor sanitiza todas as listas de endereços para garantir que nenhum MAC repetido chegue ao firmware.
* **Desativação de Debug:** Lembre-se de desligar o modo `debug` ou `raw_debug` (enviando `value: 0`) antes de disparar atualizações OTA de grande porte.
* **Portas Utilizadas:** `1883` (Broker MQTT), `8000` (FastAPI Web Dashboard & Servidor OTA HTTP).

---

## 📄 Licença
Projeto desenvolvido para a infraestrutura de medição e automação **Codax**. Uso restrito e homologado para bancada de testes e operação on-premise.
