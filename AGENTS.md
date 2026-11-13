# AGENTS.md - Contrato Central de Engenharia com Agentes de IA

Você está operando no repositório de telemetria, SCADA e gerenciamento de malha inteligente da **Ledax Energy**.
**Stack Principal**: Python 3.8+ (FastAPI, Uvicorn, Paho-MQTT, WebSockets, Pydantic) • Frontend Vanilla HTML5/CSS3/JavaScript (Tailwind CDN, Lucide Icons, SVG Nativo) • Firmware ESP-IDF 4.4 / C++ (ESP32 ESP-MESH, Modbus RTU RS485, NBR 14522, AWS IoT Core & Amazon Timestream).

---

## 🏛️ Regras Fundamentais (Invioláveis)

1. **Proibido Codificar Sem Planejamento Aprovado**:
   - Nenhuma alteração estrutural ou lógica deve ser implementada antes de um diagnóstico técnico, análise de impacto e perguntas de alinhamento com o operador.
2. **Decisão Pura vs. Efeitos Colaterais (Seams & I/O)**:
   - Parsers de payload (hexadecimal, frames NBR 14522, registradores Modbus, JSON MQTT) devem ser funções puras sem dependência de sockets ou I/O ativo de rede.
   - Chamadas de rede (boto3 Timestream, client MQTT, endpoints FastAPI) devem residir em camadas isoladas.
3. **Restrições de Ambiente e Estabilidade da Bancada**:
   - Manter compatibilidade com Python 3.8+ Windows.
   - Nunca quebrar contratos de tópicos MQTT em produção (`config/shopba/mesh`, `retorno/shopba/mesh/*`) sem espelhamento em `dev/*`.
   - Manter a integridade de `devices.json` e nunca sobrescrever identificadores sem validação.
4. **Contexto Vive no Git (Anti-Alucinação e Persistência)**:
   - Decisões de arquitetura e histórico não devem ficar na memória efêmera da conversa; devem ser documentados em arquivos versionados.

---

## 🔄 As 4 Etapas Obrigatórias de Desenvolvimento

Toda demanda ou correção deve seguir o pipeline estruturado:

```
[1. DIAGNÓSTICO & PLANO] ➔ [2. EXECUÇÃO CIRÚRGICA] ➔ [3. REVISÃO & TESTES] ➔ [4. PROMOÇÃO & ARQUIVO]
```

### 1. `ENTENDER` (Mentor de Planejamento)
- Diagnóstico da causa raiz.
- Análise de impacto nos tópicos MQTT, endpoints FastAPI e visualizadores da bancada.
- Perguntas de alinhamento com o operador antes de tocar em código.

### 2. `IMPLEMENTAR` (Execução Cirúrgica)
- Implementação atômica passo a passo.
- Proibidas refatorações invasivas fora do escopo do ticket.
- Preservar funcionalidades críticas existentes (zoom 4K/8K, árvore da malha, terminal de comandos, console WebSocket).

### 3. `REVISAR & TESTAR` (Mentor de Testes)
- Auditoria do `git diff`.
- Separação entre lógica pura (testável via scripts Python isolados) e efeitos de bancada (roteiro de validação manual / hardware).
- Compilação limpa garantida (`python -m py_compile`).

### 4. `PROMOVER & ARQUIVAR`
- Atualização da documentação permanente em `docs/ARQUITETURA.md` quando um comportamento novo vira regra do sistema.
- Congelamento de notas de decisão para consulta histórica futura.

---

## 🛡️ Limites de Operação do Agente
- O agente foca em mudanças cirúrgicas e pontuais.
- Não executa migrações destrutivas de banco em nuvem sem comando expresso do operador.
- Mantém o design corporativo industrial sóbrio, reservando o vidro fosco (*glassmorphism*) estritamente para menus flutuantes, seletores e modais.
