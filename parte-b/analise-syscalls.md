# Parte B — Análise de Chamadas de Sistema (strace)

## Contexto da Captura

Processo rastreado: ollama serve (PID 157, processo orquestrador)
Duração: ~3 minutos durante processamento de uma query ao deepseek-r1:7b
Ferramenta: strace -f -c -p <PID> (modo contagem, com threads filhas)
Total de syscalls capturadas: 45 chamadas em 0,030 segundos de CPU

Nota: o strace foi aplicado ao processo pai (ollama serve), que atua como
proxy HTTP e orquestrador. O processamento pesado (inferência) ocorre no
subprocesso llama-server (PID 1059), que não foi rastreado diretamente por
já ter encerrado antes da captura. Os dados refletem o comportamento do
orquestrador enquanto aguarda a resposta do subprocesso.

## Tabela de Syscalls Observadas

% tempo   syscall          chamadas   Família         Interpretação
76,59%    futex                  20   Sincronização   Mutex/espera de thread
15,81%    nanosleep              15   Temporização    Sleep controlado
 3,40%    restart_syscall         1   Controle        Reinício após sinal
 2,31%    sched_yield             5   Escalonamento   Cede CPU voluntariamente
 1,69%    epoll_pwait             3   I/O assíncrono  Aguarda eventos de rede
 0,20%    sched_getaffinity       1   CPU             Consulta afinidade de CPU

## Análise por Família

**Família 1 — Sincronização (futex, 76,59%)**
O futex (fast userspace mutex) é o mecanismo central de sincronização entre
threads no Linux. Sua dominância (76% do tempo de CPU) revela que o
ollama serve passa a maior parte do tempo bloqueado aguardando que o
llama-server (subprocesso de inferência) conclua o processamento. Em termos
de SO, isso corresponde ao estado "waiting" no modelo de estados de processo:
o orquestrador libera a CPU enquanto espera, permitindo que outras threads
ou processos sejam escalonados. Os 2 erros registrados são ETIMEDOUT normais
(timeout de espera expirado antes de nova tentativa).

**Família 2 — Temporização (nanosleep, 15,81%)**
Chamadas de sleep com precisão de nanossegundos, usadas pelo Ollama para
implementar polling com backoff: verifica periodicamente se o llama-server
terminou sem consumir 100% de CPU em busy-wait. Ilustra o conceito de
escalonamento cooperativo — o processo voluntariamente dorme para ceder CPU.

**Família 3 — I/O assíncrono de rede (epoll_pwait, 1,69%)**
O epoll é o mecanismo de I/O multiplexado do Linux, usado para monitorar
múltiplos file descriptors (conexões HTTP) com uma única syscall. O ollama
serve usa epoll para aguardar novas requisições na porta 11434 sem bloquear
uma thread por conexão. Relaciona-se ao modelo de I/O não bloqueante
estudado em SO: o processo não fica preso esperando dados chegarem, podendo
atender múltiplas conexões simultaneamente.

**Família 4 — Escalonamento (sched_yield, sched_getaffinity, 2,51%)**
sched_yield cede o processador voluntariamente ao escalonador do kernel,
útil em situações de contenção de lock. sched_getaffinity consulta em
quais CPUs o processo pode executar. Ambas refletem a interação direta
com o escalonador de processos do SO.

## Conclusão

O perfil de syscalls do ollama serve confirma seu papel de orquestrador
leve: quase todo o tempo é gasto em espera (futex + nanosleep = 92%),
não em computação. A inferência real ocorre no subprocesso llama-server,
que internamente emitiria famílias distintas: mmap/mmap2 para mapear os
pesos do modelo em memória, read/write para I/O de tokens, e clone para
criar threads de computação paralela. A separação entre orquestrador e
worker em subprocessos distintos é um padrão de SO que isola falhas e
permite escalar modelos independentemente do servidor HTTP.
