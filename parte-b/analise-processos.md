# Parte B — Análise de Processos e Threads

## Hierarquia de Processos (captura durante inferência ativa)

    systemd (PID 1)
    ├── ollama serve (PID 157) [12 threads]
    │   ├── llama-server nomic-embed-text (PID 1029) [11 threads, ~10% CPU]
    │   └── llama-server deepseek-r1:7b  (PID 1059) [11 threads, ~97% CPU]
    │
    └── run.py (PID 846) [1 thread]
        └── streamlit (PID 847) [21 threads]

## Tabela de Processos Principais

| Processo | PID | PPID | Estado | NLWP | CPU% | Observação |
|---|---|---|---|---|---|---|
| ollama serve | 157 | 1 | Ssl | 12 | 0% | Daemon principal |
| llama-server (nomic-embed-text) | 1029 | 157 | S | 11 | 10% | Embeddings; contexto 2048 tokens |
| llama-server (deepseek-r1:7b) | 1059 | 157 | R | 11 | 97-98% | Inferencia ativa; contexto 8192 tokens |
| python3 run.py | 846 | 394 | S | 1 | 0% | Processo pai do Streamlit |
| streamlit | 847 | 846 | S | 21 | 0% | Interface web; 21 threads para I/O |

## Análise por Processo

ollama serve (PID 157): Daemon central do Ollama, iniciado como servico do sistema (PPID 1). Mantém 12 threads em estado Ssl e consome CPU mínimo em idle. Age como roteador: recebe requisicoes HTTP na porta 11434 e delega para os subprocessos llama-server.

llama-server nomic-embed-text (PID 1029): Processo filho do Ollama responsável pelos embeddings. Roda com contexto de 2048 tokens e flag --embedding. Apresenta CPU de ~10% durante indexacao do PDF; estado S quando ocioso.

llama-server deepseek-r1:7b (PID 1059): Processo filho do Ollama responsável pela inferencia de chat. Durante a captura, threads 1059 e 1072 apresentaram 97% e 98% de CPU — inferencia ativa em CPU sem GPU. Contexto 8192 tokens. As demais 9 threads ficam em estado S aguardando I/O.

streamlit (PID 847): Processo filho de run.py (PID 846). Mantém 21 threads para gerenciar conexoes WebSocket e polling de sessao via Tornado/asyncio. Permanece em estado S durante inferencia, aguardando resposta do Ollama.

## Estados de Processo Observados

Durante inferencia CPU-only, o llama-server alterna entre R (running) e S (sleeping interruptivel). Nao foram observados estados D (I/O nao interruptivel) nem Z (zombie). O alto numero de threads no Streamlit reflete o modelo assincrono do framework, nao carga real de CPU.
