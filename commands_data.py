"""
Catálogo exaustivo de todos os comandos do firmware Codax ESP-MESH
Contém todas as funções de query, change e setting com documentação, dicas e exemplos de payload.
"""

CODAX_COMMANDS = [
    {
        "method": "query",
        "function": "mwifi_restart",
        "summary": "Chama mwifi_restart() para desatar deadlocks",
        "description": "Chama a função interna mwifi_restart() do ESP-IDF. Usar para tentar retirar os dispositivos de estados de deadlock (bug).",
        "tips": "Chama a função nativa mwifi_restart() sem reboot geral da placa. Útil para desatar nós em deadlock.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "mwifi_restart"
            }
        }
    },
    {
        "method": "query",
        "function": "meter_serial_number",
        "summary": "Consulta ID do medidor ABNT NBR 14522 multiponto",
        "description": "Retorna o ID do medidor configurado para o modo ABNT NBR 14522 multiponto.",
        "tips": "Usado para verificar a identificação do medidor óptico/serial conectado.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "meter_serial_number"
            }
        }
    },
    {
        "method": "query",
        "function": "block_topology",
        "summary": "Consulta bloqueio do envio automático de topologia",
        "description": "Retornará se o envio automático de topologia sempre que há mudança na malha está ativo ou bloqueado.",
        "tips": "Permite verificar se a malha está emitindo broadcasts automáticos a cada reconexão de nós.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "block_topology"
            }
        }
    },
    {
        "method": "query",
        "function": "protocol",
        "summary": "Consulta protocolo e interface em uso",
        "description": "Retornará o protocolo e a interface para aquisição de dados que a controladora está utilizando (ex: Modbus, NBR 14522, Pulse, One-Wire).",
        "tips": "Importante para validar se a interface física (RS485, RS232, RJ45) está de acordo com o hardware montado.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "protocol"
            }
        }
    },
    {
        "method": "query",
        "function": "core_dump",
        "summary": "Resgata registro do último crash da placa",
        "description": "Tentará resgatar o registro do último crash da controladora e dar upload no S3 bucket.",
        "tips": "ATENÇÃO: Por enquanto só o ROOT pode responder essa query.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "core_dump"
            }
        }
    },
    {
        "method": "query",
        "function": "info",
        "summary": "Retorna informações detalhadas do dispositivo",
        "description": "Retorna IP, GW IP, free heap, node num, device id, router SSID, router password, mesh id, mesh password, channel, layer, self MAC, parent MAC, parent RSSI, mesh_type, self_org, fix_root, parent_connected, root status, entre outros.",
        "tips": "Comando principal para obter diagnóstico completo de qualquer placa na rede.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "info"
            }
        }
    },
    {
        "method": "query",
        "function": "log_level",
        "summary": "Consulta nível de log ativo para uma TAG",
        "description": "Retorna o nível de log menos significante que será permitido da devida TAG passada por 'value'.",
        "tips": "Permite verificar se tags como PIMA_LEDAX, MESH, MODBUS estão em modo VERBOSE, DEBUG, INFO ou ERROR.",
        "value_type": "String com o nome da TAG",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "log_level",
                "value": "PIMA_LEDAX"
            }
        }
    },
    {
        "method": "query",
        "function": "back_trace",
        "summary": "Retorna os Program Counters (PC) do último crash",
        "description": "Retorna os program counter(PC) do back trace do último crash sofrido pela controladora, que poderá ser utilizado no esp-idf monitor para ver os trechos de código que foram percorridos antes do crash.",
        "tips": "ATENÇÃO: O back trace só será válido se o comando do xtensa apontar para o .elf da MESMA versão gravada.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "back_trace"
            }
        }
    },
    {
        "method": "query",
        "function": "self_organized",
        "summary": "Consulta se a rede auto-organizada está ativa",
        "description": "Retorna se a controladora está com self_organized_network da rede mesh ativado ou não.",
        "tips": "Se desativado, a topologia de pais e filhos fica fixa.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "self_organized"
            }
        }
    },
    {
        "method": "query",
        "function": "memory",
        "summary": "Consulta memória heap livre e mínima",
        "description": "Retorna quanto de heap livre atual e quanto foi o heap mínimo atingido da controladora desde o último reset.",
        "tips": "Útil para detectar vazamento de memória (memory leak) em tarefas contínuas.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "memory"
            }
        }
    },
    {
        "method": "query",
        "function": "mesh_id",
        "summary": "Retorna o Mesh ID da malha",
        "description": "Retorna o ID de malha (mesh id de 6 bytes) configurado na controladora.",
        "tips": "Controladoras só se comunicam se tiverem o mesmo mesh id e senha de malha.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "mesh_id"
            }
        }
    },
    {
        "method": "query",
        "function": "time",
        "summary": "Consulta horário do sistema e tempo ligado (uptime)",
        "description": "Retorna o horário do sistema do ESP e o tempo em segundos que ele está rodando contínuo.",
        "tips": "O buffer de contagem pode sofrer overflow após ~49 dias.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "time"
            }
        }
    },
    {
        "method": "query",
        "function": "partition",
        "summary": "Consulta partição ativa e secundária",
        "description": "Retorna dados da partição que está rodando e da partição secundária (versão, projeto, data compilação, IDF).",
        "tips": "Pode usar a chave 'value' para filtrar: ex '!2.1.1' para responder apenas as que NÃO estão nessa versão.",
        "value_type": "String opcional com versão (ex: '!2.1.1')",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "partition",
                "value": "!2.1.1"
            }
        }
    },
    {
        "method": "query",
        "function": "ping",
        "summary": "Ping na malha com layer e RSSI",
        "description": "Retorna layer, MAC address da controladora, e se for ROOT também retorna o MAC do roteador e sinal em dBm.",
        "tips": "O comando mais leve e rápido para checar presença de nós.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "ping"
            }
        }
    },
    {
        "method": "query",
        "function": "telemetry",
        "summary": "Consulta valores instantâneos dos totalizadores",
        "description": "Retorna o valor dos totalizadores de grandezas configuradas nos medidores.",
        "tips": "Retorna dados sem aguardar o ciclo periódico de envio.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "telemetry"
            }
        }
    },
    {
        "method": "query",
        "function": "counter",
        "summary": "Ativa envio de pulsos contínuos no MQTT por 5 min",
        "description": "Ativa ou desativa o contador de pulsos da controladora, enviando para o MQTT. Desativa sozinho após 5 minutos.",
        "tips": "Evitar usar durante mupgrade ou troca de rede para não sobrecarregar CPU e broker.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "counter"
            }
        }
    },
    {
        "method": "query",
        "function": "id",
        "summary": "Consulta ID de instalação na flash",
        "description": "Retorna o ID numérico de instalação atribuído à placa.",
        "tips": "Chave identificadora usada nos sistemas de faturamento e telemetria.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "id"
            }
        }
    },
    {
        "method": "query",
        "function": "network",
        "summary": "Consulta credenciais Wi-Fi configuradas",
        "description": "Retorna as credenciais do roteador Wi-Fi em que está conectado, tanto da flash quanto as da API.",
        "tips": "Permite auditar o SSID e saber se a controladora está no Wi-Fi correto.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "network"
            }
        }
    },
    {
        "method": "query",
        "function": "OTAlinkHTTP",
        "summary": "Consulta link HTTP gravado para OTA",
        "description": "Retorna o link HTTP que está gravado na memória flash para realização de mupgrade.",
        "tips": "Mostra qual URL a controladora usará caso receba ordem de upgrade sem link explícito.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "OTAlinkHTTP"
            }
        }
    },
    {
        "method": "query",
        "function": "topology",
        "summary": "Retorna topologia completa da malha",
        "description": "O ROOT retorna a topologia atual da rede mesh: layer de cada nó, id, parent_id, mac_addr, router_mac_addr e router_rssi. Se enviado para um node, ele repassa ao ROOT.",
        "tips": "DICA: Enviar para 'root' (ff:00:00:01:00:00) para receber a topologia de todas as malhas existentes.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "ff0000010000"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "topology"
            }
        }
    },
    {
        "method": "query",
        "function": "root",
        "summary": "Identifica a placa ROOT ('I'm GROOT')",
        "description": "Se a controladora que recebeu a mensagem for ROOT, responderá com 'I'm GROOT'.",
        "tips": "DICA: Enviar para 'any' fará com que apenas todas as ROOTs ativas respondam.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "ffffffffffff"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "root"
            }
        }
    },
    {
        "method": "query",
        "function": "test",
        "summary": "Comando de bancada dev/test (restart manual)",
        "description": "Compilado APENAS em builds DEV_ENV ou TEST_ENV. Reinicia na hora por esp_restart(), tageado no diagnóstico de reset.",
        "tips": "Em build de produção não faz nada por segurança.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "test"
            }
        }
    },
    {
        "method": "query",
        "function": "restart",
        "summary": "Soft reset com contagem regressiva de 10s",
        "description": "Retorna mensagem avisando que sofrerá um soft reset em 10 segundos e então reinicia.",
        "tips": "Soft reset geral do ESP32 com contagem regressiva de 10s. Pode ser enviado para 'root', 'any' ou 'broadcast'.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "restart"
            }
        }
    },
    {
        "method": "query",
        "function": "meter",
        "summary": "Consulta parâmetros cadastrados dos medidores",
        "description": "Retorna os parâmetros e modelos de medidores atualmente configurados na placa.",
        "tips": "Verifica IP do medidor, porta, modelo e grandezas monitoradas.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "meter"
            }
        }
    },
    {
        "method": "query",
        "function": "device_config",
        "summary": "Consulta metadados completos do device object",
        "description": "Retorna todos os parâmetros de comunicação, interface, protocolo e Ethernet cadastrados no dispositivo.",
        "tips": "Audita se a placa está em RS485, Modbus TCP/UDP ou NBR 14522.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "device_config"
            }
        }
    },
    {
        "method": "query",
        "function": "active_telemetry",
        "summary": "Consulta se a telemetria periódica está ativa",
        "description": "Retorna o status do active_telemetry (True se enviando, False se pausada).",
        "tips": "O estado é persistido na flash e sobrevive a reboots.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "active_telemetry"
            }
        }
    },
    {
        "method": "query",
        "function": "reset_diag_log",
        "summary": "Consulta anel de log de diagnóstico de reset e last_reset_reason",
        "description": "Retorna o estado da captura do anel de log de diagnóstico de reset e se há diagnóstico esperando publicação.\n\nDISPONIBILIDADE: Só existe em builds com CONFIG_RESET_DIAG_ENABLE ligado (default). Com o símbolo desligado, o comando responde como função desconhecida.\n\nCAMPOS RETORNADOS:\n• 'enabled': True se a captura do anel está habilitada (estado persistido em flash, sobrevive a reset).\n• 'pending': True se existe diagnóstico de um reset anterior ainda não publicado. Falso é o normal depois de um boot limpo: power-on, watchdog, brownout e reset por software de ponto não tageado NÃO geram diagnóstico, por design — apenas panic e os pontos de escalada do conn_bb_sitter geram.\n• 'last_reset_reason': o esp_reset_reason() do boot atual ('Power on - reason N').\n\nTABELA DE CÓDIGOS ESP-IDF v4.4.8 (esp_system.h):\n  0 = Desconhecido | 1 = Power-on | 2 = Pino externo | 3 = Software (esp_restart)\n  4 = Panic/Exceção | 5 = Watchdog de interrupção | 6 = Watchdog de task | 7 = Outros watchdogs\n  8 = Saída de deep sleep | 9 = Brownout (queda de tensão) | 10 = Reset via SDIO\n\nGeram campo 'reset_diag': apenas código 4 (sempre) e 3 (se vier de um dos 16 pontos tageados).",
        "tips": "Use para diagnosticar a causa exata de reinicializações inesperadas ou falhas de alimentação.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "reset_diag_log"
            }
        }
    },
    {
        "method": "query",
        "function": "pulse_monitor_threshold_ms",
        "summary": "Consulta threshold do monitor de pulsos",
        "description": "Retorna o limiar mínimo de duração em milissegundos para considerar um pulso válido.",
        "tips": "Usado apenas nas controladoras com interface PULSE_WIDTH e protocolo PULSE.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "pulse_monitor_threshold_ms"
            }
        }
    },
    {
        "method": "query",
        "function": "timezone",
        "summary": "Consulta deslocamento de timezone UTC",
        "description": "Retorna o valor atual do deslocamento em relação ao UTC para o timezone configurado.",
        "tips": "Verifica se a placa está ajustada corretamente com convenção POSIX.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "timezone"
            }
        }
    },
    {
        "method": "query",
        "function": "eth_status",
        "summary": "Consulta status da conexão Ethernet",
        "description": "Retorna se está usando DHCP ('Ethernet DHCP: Habilitado') ou IP Estático (com IP, Gateway e Netmask).",
        "tips": "Usado para verificar a conexão do módulo W5500 ou Ethernet nativo.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "eth_status"
            }
        }
    },
    {
        "method": "query",
        "function": "webserver_credentials",
        "summary": "Consulta logins e senhas do webserver",
        "description": "Retorna usuários e senhas de acesso ao webserver local. Se senha for padrão, exibe em texto claro; se personalizada, indica que não é recuperável.",
        "tips": "ATENÇÃO: Utilizar somente em contexto de suporte e recuperação de acesso.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "webserver_credentials"
            }
        }
    },
    {
        "method": "query",
        "function": "tel_clients",
        "summary": "Consulta estado do campo client na telemetria",
        "description": "Retorna se o campo 'client' está habilitado e qual a lista de clientes cadastrada.",
        "tips": "Resposta ex: {'id':'...', 'enabled':False, 'clients':[]}",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "query",
                "function": "tel_clients"
            }
        }
    },
    {
        "method": "change",
        "function": "meter_serial_number",
        "summary": "Define ID do medidor ABNT NBR 14522 multiponto",
        "description": "Grava novo ID numérico do medidor para o modo multiponto.",
        "tips": "Passe um número inteiro no campo value.",
        "value_type": "Número inteiro (ex: 187932)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "meter_serial_number",
                "value": 187932
            }
        }
    },
    {
        "method": "change",
        "function": "block_topology",
        "summary": "Bloqueia ou desbloqueia envio automático de topologia",
        "description": "Define se o envio de topologia automático quando há mudança na malha estará ativo ou não.",
        "tips": "value = False desbloqueia envio; value = True bloqueia.",
        "value_type": "Boolean (True ou False)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "block_topology",
                "value": True
            }
        }
    },
    {
        "method": "change",
        "function": "log_level",
        "summary": "Define nível de log para uma TAG específica",
        "description": "Define o nível de log mínimo permitido. Níveis: NONE, ERROR, WARN, INFO, DEBUG, VERBOSE.",
        "tips": "value deve ser um objeto com 'tag' e 'log_level'.",
        "value_type": "JSON Object com tag e log_level",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "log_level",
                "value": {
                    "tag": "PIMA_LEDAX",
                    "log_level": "INFO"
                }
            }
        }
    },
    {
        "method": "change",
        "function": "topology",
        "summary": "Força controladora a mudar para IDLE ou ROOT",
        "description": "Recebe 'IDLE' ou 'ROOT', forçando a controladora a alterar seu tipo na malha.",
        "tips": "ROOT faz a controladora ir para uma malha com o mesmo ID do seu MAC. Enviar para broadcast força todas nodes para root.",
        "value_type": "String ('ROOT' ou 'IDLE')",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "topology",
                "value": "ROOT"
            }
        }
    },
    {
        "method": "change",
        "function": "partition",
        "summary": "Troca de partição de firmware (com restart)",
        "description": "Troca para a partição da versão enviada, ou alterna entre primária e secundária se value for omitido.",
        "tips": "A controladora reinicia após 10 segundos em caso de êxito.",
        "value_type": "String com versão (ex: '2.1.4') ou omitido",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "partition",
                "value": "2.1.4"
            }
        }
    },
    {
        "method": "change",
        "function": "network",
        "summary": "Altera as credenciais de rede Wi-Fi da malha",
        "description": "Recebe novo SSID e password. A ROOT leva toda a malha para o novo canal após conexão bem sucedida.",
        "tips": "Em builds DEV ou TEST, ela procura redes com sufixo _DEV ou _TEST.",
        "value_type": "JSON Object com ssid e password",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "network",
                "value": {
                    "ssid": "testeDrive",
                    "password": "ab12cd34A@ax"
                }
            }
        }
    },
    {
        "method": "change",
        "function": "firmware",
        "summary": "Inicia processo de mupgrade via OTA",
        "description": "Recebe protocolo (HTTP/HTTPS), lista de controladoras que receberão e block (1 para interromper no erro, 2 para continuar).",
        "tips": "Finaliza com restart em caso de êxito.",
        "value_type": "JSON Object com protocol, addr e block",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "firmware",
                "value": {
                    "protocol": "HTTP",
                    "addr": [
                        "ffffffffffff"
                    ],
                    "block": 1
                }
            }
        }
    },
    {
        "method": "change",
        "function": "root",
        "summary": "Inicia votação na malha para eleger nova ROOT",
        "description": "A controladora iniciará uma votação com a rede mesh para eleger uma nova ROOT.",
        "tips": "A própria ROOT atual pode ser reeleita.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "root"
            }
        }
    },
    {
        "method": "change",
        "function": "id",
        "summary": "Grava novo ID de instalação na flash",
        "description": "Recebe novo ID na memória flash. Retorna aviso para reiniciar para atualizar nas instâncias.",
        "tips": "value é uma string numérica.",
        "value_type": "String com ID",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "id",
                "value": "467"
            }
        }
    },
    {
        "method": "change",
        "function": "OTAlinkHTTP",
        "summary": "Grava novo link HTTP padrão para OTA na flash",
        "description": "Recebe novo link padrão para mupgrade via HTTP.",
        "tips": "O link é persistido e usado em upgrades futuros.",
        "value_type": "String com URL",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "OTAlinkHTTP",
                "value": "http://ota.ledax.io/codax-m.bin"
            }
        }
    },
    {
        "method": "change",
        "function": "format_flash",
        "summary": "Formata a flash da controladora (limpa tudo)",
        "description": "Formata a flash da controladora apagando todo o conteúdo e configurações gravadas.",
        "tips": "CUIDADO: Operação irreversível, resetará todas as configurações de fábrica.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "format_flash"
            }
        }
    },
    {
        "method": "change",
        "function": "update_firmware",
        "summary": "Dispara mupgrade com link HTTP explícito",
        "description": "Recebe link HTTP/HTTPS para o binário, protocolo, lista de MACs e modo block (1 interrompe no erro, 0 continua).",
        "tips": "Comando padrão utilizado pelo nosso servidor local para atualizar as placas.",
        "value_type": "JSON Object com link, protocol, addr e block",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "update_firmware",
                "value": {
                    "link": "http://192.168.1.100:8000/firmware/codax-m.bin",
                    "protocol": "HTTP",
                    "addr": [
                        "ffffffffffff"
                    ],
                    "block": 1
                }
            }
        }
    },
    {
        "method": "change",
        "function": "timezone",
        "summary": "Define timezone UTC (sinal invertido POSIX)",
        "description": "Recebe deslocamento UTC com sinal invertido POSIX. Ex: Brasília (UTC-3) deve ser enviado como '+0300'.",
        "tips": "Atenção à inversão de sinal da norma POSIX.",
        "value_type": "String com offset POSIX (ex: '+0300')",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "timezone",
                "value": "+0300"
            }
        }
    },
    {
        "method": "change",
        "function": "webserver_password",
        "summary": "Altera ou reseta senha de acesso ao webserver",
        "description": "Sem value: reseta ambas as senhas (user e dev) para padrão. Com value: define nova senha para o role ('user' ou 'dev'). Mínimo 8 caracteres, 1 número e 1 especial.",
        "tips": "Invalida a sessão ativa no webserver forçando novo login.",
        "value_type": "JSON Object com role e new_pass (ou omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "change",
                "function": "webserver_password",
                "value": {
                    "role": "user",
                    "new_pass": "MinhaS3nha!"
                }
            }
        }
    },
    {
        "method": "setting",
        "function": "device_config",
        "summary": "Configuração completa de Interface, Protocolo, Ethernet, Wi-Fi e Mesh",
        "description": "Define os metadados e parâmetros operacionais do device object na memória flash:\n\n• 'interface': RS232, RS485, MODBUS_TCP, MODBUS_UDP, PULSE_WIDTH, ONE_WIRE, ON_OFF_STATUS\n• 'protocol': NBR_14522, MODBUS, PULSE, ONE_WIRE\n• 'eth_use_dhcp': True para DHCP automático ou False para IP fixo\n• 'eth_static_ip', 'eth_gateway', 'eth_netmask': Endereçamento Ethernet estático\n• 'router_ssid', 'router_password': Credenciais do roteador Wi-Fi (usado pelo ROOT)\n• 'mesh_id', 'mesh_password', 'channel': Parâmetros de formação da malha ESP-MESH\n• 'bttn_io', 'led_io', 'led_invert': GPIOs de hardware da controladora",
        "tips": "Após salvar alterações críticas de rede ou interface, recomenda-se reiniciar o nó para aplicar.",
        "value_type": "JSON Object com parâmetros de configuração",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "device_config",
                "value": {
                    "device_id": "ND",
                    "router_ssid": "MEDIDOR",
                    "router_password": "hPL561VAhKj",
                    "mesh_id": [
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "1"
                    ],
                    "mesh_capability": True,
                    "communication_protocol": "NBR_14522",
                    "communication_interface": "RS232"
                }
            }
        }
    },
    {
        "method": "setting",
        "function": "meter",
        "summary": "Cadastra medidores, portas de comunicação e grandezas a requisitar",
        "description": "Cadastra os medidores conectados à controladora:\n\nMODELOS SUPORTADOS:\n• 'MD50_MD30': Medidores de energia eletrônicos Modbus (MD50/MD30). Requer 'parameters' (ex: ['total', 'demand_max']).\n• 'PULSE_MONITOR': Monitoramento de pulsos digitais. Requer 'parameters': ['event_duration'].\n• 'DS18B20': Sensor de temperatura 1-Wire. Requer 'parameters': ['TEMPERATURE'].\n• 'ON_OFF_MONITOR': Monitoramento de estado ligado/desligado. Requer 'parameters': ['on_off_status'].\n\nCAMPOS:\n• 'id': Identificador único do medidor (usado como chave na telemetria e no raw_debug)\n• 'model': Modelo do equipamento (acima)\n• 'network_addr': Endereço IP (se UDP/TCP) ou endereço Modbus RTU\n• 'network_port': Porta de rede (padrão 502 para Modbus)\n• 'parameters': Array com as grandezas requisitadas periodicamente",
        "tips": "Para ON_OFF_MONITOR: parameters ['on_off_status']. Para PULSE_MONITOR: parameters ['event_duration'].",
        "value_type": "Array de objetos com id, model, parameters, network_addr, network_port",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "meter",
                "value": [
                    {
                        "id": "MD50_01",
                        "model": "MD50_MD30",
                        "network_addr": "192.168.0.150",
                        "network_port": 502,
                        "parameters": [
                            "total",
                            "demand_max"
                        ]
                    }
                ]
            }
        }
    },
    {
        "method": "setting",
        "function": "reset_tot",
        "summary": "Reseta todos os totalizadores para zero",
        "description": "Reseta todos os totalizadores monitorados para zero na memória flash.",
        "tips": "Útil para início de novo ciclo de medição em bancada.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "reset_tot"
            }
        }
    },
    {
        "method": "setting",
        "function": "self_organized",
        "summary": "Ativa ou desativa self_organized_network da malha",
        "description": "Recebe 0 para desativar ou 1 para ativar a rede auto-organizada.",
        "tips": "Ativar pode forçar a troca de nó pai (parent) caso o sinal esteja fraco.",
        "value_type": "Número (0 ou 1)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "self_organized",
                "value": 1
            }
        }
    },
    {
        "method": "setting",
        "function": "mesh_id",
        "summary": "Altera os 3 últimos números do Mesh ID",
        "description": "Recebe os 3 últimos números em hex. Os 3 primeiros referem-se à versão do firmware e não mudam.",
        "tips": "Ex: '4f49a4'.",
        "value_type": "String hex de 6 caracteres",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "mesh_id",
                "value": "4f49a4"
            }
        }
    },
    {
        "method": "setting",
        "function": "tot",
        "summary": "Define novo valor de totalizador (inativo)",
        "description": "Recebe um novo valor de totalizador gravado na flash. Reseta os pulsos para zero.",
        "tips": "Em desuso nas versões mais recentes.",
        "value_type": "String ou número decimal",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "tot",
                "value": "32412.43"
            }
        }
    },
    {
        "method": "setting",
        "function": "tot_plus",
        "summary": "Soma ou subtrai valor do totalizador (inativo)",
        "description": "Recebe um valor que será somado ou subtraído do totalizador. Não reseta os pulsos.",
        "tips": "Para valor positivo NÃO colocar '+'. Para subtrair colocar número negativo.",
        "value_type": "String ou número decimal",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "tot_plus",
                "value": "-84293.32"
            }
        }
    },
    {
        "method": "setting",
        "function": "debug",
        "summary": "Inicia modo debug como client",
        "description": "Recebe o MAC address do host_debug que receberá as mensagens. Aloca recursos da API mdebug.",
        "tips": "ATENÇÃO: Desativar após o uso antes de executar OTA ou troca de Wi-Fi.",
        "value_type": "String MAC address",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "debug",
                "value": "4417934f4fd8"
            }
        }
    },
    {
        "method": "setting",
        "function": "stop_debug",
        "summary": "Desliga modo debug (client ou host)",
        "description": "Desliga o modo debug da controladora, liberando tráfego de diagnóstico.",
        "tips": "Evitar enviar para controladoras que não estejam em debug.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "stop_debug"
            }
        }
    },
    {
        "method": "setting",
        "function": "host_debug",
        "summary": "Inicia modo debug como host",
        "description": "Inicia a controladora como receptora das mensagens de debug dos clientes.",
        "tips": "Um host pode receber mensagens de vários clients simultaneamente.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "host_debug"
            }
        }
    },
    {
        "method": "setting",
        "function": "active_telemetry",
        "summary": "Ativa ('start') ou pausa ('stop') a telemetria",
        "description": "Vale em TODOS os modos de medição. O estado é persistido na flash e sobrevive a reboots. 'stop' para envio; em largura de pulso continua gravando na flash.",
        "tips": "Use 'start' para retomar o envio ou 'stop' para suspender.",
        "value_type": "String ('start' ou 'stop')",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "active_telemetry",
                "value": "start"
            }
        }
    },
    {
        "method": "setting",
        "function": "reset_diag_log",
        "summary": "Liga ('start') ou desliga ('stop') anel de log de diagnóstico",
        "description": "Liga ou desliga a captura de um anel recente de log (até 4096 B, INFO/WARN/ERROR) anexado à mensagem de 'Power on - reason N' em conn/ após crash ou reset.",
        "tips": "Desligado por padrão para economizar ciclos de CPU. Persistido na flash.",
        "value_type": "String ('start' ou 'stop')",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "reset_diag_log",
                "value": "start"
            }
        }
    },
    {
        "method": "setting",
        "function": "config_state",
        "summary": "Coloca dispositivo em modo configuração AP + Webserver",
        "description": "Salva o estado na flash e reinicia em 10 segundos, entrando no modo de configuração (ponto de acesso Wi-Fi + webserver local).",
        "tips": "Ficará em modo de configuração até ser reconfigurado via comissionamento.",
        "value_type": "Nenhum (omitido)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "config_state"
            }
        }
    },
    {
        "method": "setting",
        "function": "pulse_monitor_threshold_ms",
        "summary": "Define limiar de pulso válido em milissegundos",
        "description": "Pulsos com duração inferior ao threshold são descartados. Aplicado imediatamente em memória e salvo na flash.",
        "tips": "Padrão: 500 ms. Recomenda-se valor 10x menor que a menor duração esperada.",
        "value_type": "Número inteiro em ms (ex: 500)",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "pulse_monitor_threshold_ms",
                "value": 500
            }
        }
    },
    {
        "method": "setting",
        "function": "tel_clients",
        "summary": "Configura campo client opcional na telemetria",
        "description": "Permite habilitar/desabilitar o campo e definir a lista de clientes incluída no array tel_json.",
        "tips": "Para desabilitar mantendo lista: {'enabled': False}. Para limpar lista: {'enabled': False, 'clients': []}.",
        "value_type": "JSON Object com enabled e clients",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "tel_clients",
                "value": {
                    "enabled": True,
                    "clients": [
                        "IQUIRA",
                        "LEDAX"
                    ]
                }
            }
        }
    },
    {
        "method": "setting",
        "function": "raw_debug",
        "summary": "Captura frames brutos trocados com medidores no tópico err/ (com filtros)",
        "description": "Publica no tópico err/ os frames BRUTOS trocados com medidores.\nRecebe a duração em segundos [10, 300] ou um JSON Object com filtros por medidor e/ou grandeza. Enviar 'value: 0' encerra a sessão na hora.\n\nPROTOCOLOS SUPORTADOS:\n• RS485 + MODBUS -> frame completo, rótulo de medidor e parâmetro\n• RJ45 + MODBUS_UDP -> frame completo, rótulo de medidor e parâmetro\n• RS232 + NBR_14522 -> frame completo, rótulo de medidor e contexto ('chg:N' / 'data:N')\n• USER + PIMA -> frame recebido, medidor pelo id do cadastro e número de série em BCD\n\nESTRUTURA DO PAYLOAD PUBLICADO EM err/:\n• 'proto': Driver que produziu as entradas (interface x protocolo)\n• 'f': Lote de trocas acumuladas desde a última publicação\n• 'id': ID do medidor no cadastro (mesma chave da telemetria)\n• 'net': Endereço de rede (IP no UDP, ID no RS485, Serial no ABNT/PIMA)\n• 'p': Parâmetro da troca ('chg:N' / 'data:N' ou nome da grandeza)\n• 'a': Tentativa dentro do laço de retry (0=saudável, 3-4=marginal, 0-24 vazio=medidor offline)\n• 'tx' / 'rx': Hexadecimais das trocas truncados em 48 bytes ('rx' vazio com 'rxn':0 = sem resposta)\n• 'txn' / 'rxn': Comprimento REAL do frame antes do truncamento\n• 'drop': Quantidade de frames descartados por estouro de buffer",
        "tips": "USE O FILTRO SEMPRE QUE POSSÍVEL para evitar perda (drop) de pacotes por saturação de buffer.",
        "value_type": "Número (segundos) ou JSON Object com seconds, meter e parameter",
        "example": {
            "addr": [
                "4417934f49a4"
            ],
            "type": "json",
            "data": {
                "method": "setting",
                "function": "raw_debug",
                "value": {
                    "seconds": 180,
                    "meter": "test_tel",
                    "parameter": "total"
                }
            }
        },
        "examples": [
            {
                "label": "Exemplo 0: Sem filtro (captura geral por 180s)",
                "payload": {
                    "addr": [
                        "4417934f49a4"
                    ],
                    "type": "json",
                    "data": {
                        "method": "setting",
                        "function": "raw_debug",
                        "value": 180
                    }
                }
            },
            {
                "label": "Exemplo 1: Filtrado pelo ID do cadastro",
                "payload": {
                    "addr": [
                        "4417934f49a4"
                    ],
                    "type": "json",
                    "data": {
                        "method": "setting",
                        "function": "raw_debug",
                        "value": {
                            "seconds": 180,
                            "meter": "test_tel",
                            "parameter": "total"
                        }
                    }
                }
            },
            {
                "label": "Exemplo 2: Filtrado pelo IP de rede",
                "payload": {
                    "addr": [
                        "4417934f49a4"
                    ],
                    "type": "json",
                    "data": {
                        "method": "setting",
                        "function": "raw_debug",
                        "value": {
                            "seconds": 180,
                            "meter": "192.168.0.179",
                            "parameter": "total"
                        }
                    }
                }
            },
            {
                "label": "Exemplo 3: Filtrado apenas pelo parâmetro",
                "payload": {
                    "addr": [
                        "4417934f49a4"
                    ],
                    "type": "json",
                    "data": {
                        "method": "setting",
                        "function": "raw_debug",
                        "value": {
                            "seconds": 180,
                            "parameter": "total"
                        }
                    }
                }
            },
            {
                "label": "Exemplo 4: Encerrar debug na hora",
                "payload": {
                    "addr": [
                        "4417934f49a4"
                    ],
                    "type": "json",
                    "data": {
                        "method": "setting",
                        "function": "raw_debug",
                        "value": 0
                    }
                }
            }
        ]
    }
]
