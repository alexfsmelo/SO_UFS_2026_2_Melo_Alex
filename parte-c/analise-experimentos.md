# Parte C — Análise dos Experimentos

## Configuração do ambiente

Todos os experimentos foram executados em 15/09/2026 em WSL2 (Ubuntu) com CPU Intel x64,
7,8 GB de RAM disponíveis, Ollama 0.6.2, modelo principal DeepSeek-R1-Distill-Qwen-7B
(GGUF Q4_K_M, 4,7 GB) para inferência e nomic-embed-text para embeddings RAG.
Nenhuma GPU foi utilizada — 100% CPU.

---

## Tabela consolidada de experimentos

| Config | Variante | Rep | TTFT (s) | Total (ms) | RAM (MB) | Threads | Obs |
|--------|----------|-----|----------|------------|----------|---------|-----|
| C1-A | padrao/curta | 1 | 71,48 | 71.801 | 5.847 | 15 | |
| C1-A | padrao/curta | 2 | 60,13 | 60.488 | 5.865 | 15 | |
| C1-B | padrao/longa | 1 | 337,00 | 343.199 | 5.981 | 19 | |
| C1-B | padrao/longa | 2 | 535,16 | 536.360 | 6.021 | 15 | |
| C2-A | concorrente | 1 | 139,07 | 230.013 | 5.315 | 15 | 2 req simultâneas |
| C2-A | concorrente | 2 | 84,42 | 117.180 | 5.346 | 15 | 2 req simultâneas |
| C2-B | rag-ativo/curta | 1 | 62,68 | 66.013 | 6.429 | 15 | RAG pipeline ativo |
| C2-B | rag-ativo/curta | 2 | 132,49 | 132.870 | 6.444 | 15 | RAG pipeline ativo |
| C3-A | quant-1.5b | 1 | 23,37 | 55.324 | 6.602 | 26 | modelo menor |
| C3-A | quant-1.5b | 2 | 31,35 | 31.542 | 6.616 | 26 | modelo menor |
| C3-B | ctx-2048 | 1 | 28,92 | 188.217 | 6.399 | 26 | ctx restrito (reload) |
| C3-B | ctx-2048 | 2 | 38,05 | 38.542 | 6.411 | 26 | ctx restrito |

**Total: 12 execuções válidas em 6 sub-configurações.**

### Médias por configuração

| Config | Descrição | TTFT médio (s) | Total médio (ms) | RAM média (MB) |
|--------|-----------|----------------|-----------------|----------------|
| C1-A | padrao, query curta | 65,81 | 66.145 | 5.856 |
| C1-B | padrao, query longa | 436,08 | 439.780 | 6.001 |
| C2-A | concorrente (2 req) | 111,75 | 173.597 | 5.331 |
| C2-B | RAG pipeline ativo | 97,59 | 99.442 | 6.437 |
| C3-A | modelo 1.5b | 27,36 | 43.433 | 6.609 |
| C3-B | ctx=2048 | 33,49 | 113.380 | 6.405 |

---

## Q16 — Qual foi o impacto do tamanho da query no tempo de resposta (C1-A vs C1-B)?

A query longa (C1-B, pedindo explicação detalhada de escalonamento com exemplos) levou
em média 436 s de TTFT, contra 65,81 s da query curta (C1-A, definição em 2 frases).
Isso representa uma diferença de 6,6× no tempo de resposta para a mesma configuração de
hardware e modelo.

A causa direta é a quantidade de tokens gerados: o modelo precisa produzir muito mais
conteúdo para uma resposta detalhada. Como a inferência em CPU tem custo linear por
token, a latência cresce proporcionalmente ao tamanho da saída esperada. Isso confirma
que o gargalo do sistema não está na entrada (o prompt é lido rapidamente), mas na
geração token a token.

---

## Q17 — O tempo de resposta foi consistente entre repetições da mesma configuração?

Não. A variância foi alta em todas as configurações:

- C1-A (padrao/curta): 60,13 s a 71,48 s (amplitude de 11 s, ~17%)
- C1-B (padrao/longa): 337,00 s a 535,16 s (amplitude de 198 s, ~45%)
- C2-A (concorrente): 84,42 s a 139,07 s (amplitude de 55 s, ~50%)
- C3-A (quant-1.5b): 23,37 s a 31,35 s (amplitude de 8 s, ~29%)

A variância é especialmente alta em queries longas e em configurações com carga extra
(concorrência, RAG ativo). Os fatores que causam variação são: decisões do escalonador
CFS do Linux sobre distribuição de time slice entre as 11 threads do llama-server;
crescimento dinâmico da KV-cache durante a geração; e possível competição de memória
com processos do WSL2/Windows em background.

---

## Q18 — Qual foi o comportamento de RAM ao longo dos experimentos?

O uso de RAM cresceu monotonicamente ao longo da sessão, de ~5.315 MB (C2-A, onde o
modelo foi brevemente descarregado) até ~6.616 MB (C3-A, com dois modelos carregados
simultaneamente). Esse crescimento tem dois componentes principais:

O primeiro é a KV-cache que o Ollama mantém em memória entre requisições para evitar
reprocessar tokens repetidos. O segundo é a carga cumulativa de modelos: no bloco C3-A,
o deepseek-r1:1.5b foi carregado sem descarregar o 7b, elevando o uso para ~6,6 GB
(4,7 GB do 7B + ~1 GB do 1.5B + overhead de runtime).

Em nenhum momento o sistema atingiu swap, mas o uso se aproximou do limite de 7,8 GB
disponíveis, o que pode explicar parte da variância em execuções tardias.

---

## Q19 — Como a concorrência afetou o desempenho (C2-A)?

No experimento C2-A, duas requisições foram enviadas simultaneamente ao Ollama. Os
resultados revelam que o Ollama serializa as requisições internamente: o tempo total
de wall-clock (230 s e 117 s) foi significativamente maior que o TTFT da primeira
requisição (139 s e 84 s), pois a segunda requisição aguardou na fila enquanto a
primeira era processada.

Isso contrasta com arquiteturas de inferência com GPU, onde batching verdadeiro
permite processar múltiplas requisições em paralelo. Na CPU, o llama-server usa todos
os núcleos disponíveis para uma única geração, não sobrando capacidade para paralelismo
real. O overhead de fila foi de aproximadamente 91 s na rep 1 (230 - 139) e 33 s na
rep 2, representando o tempo que a segunda requisição esperou.

---

## Q20 — O RAG pipeline ativo alterou o desempenho de inferência direta (C2-B vs C1-A)?

C2-B (RAG ativo, mesma query curta): TTFT médio de 97,59 s vs C1-A de 65,81 s.
Diferença de +32 s (+49%). O RAM médio de C2-B foi de 6.437 MB vs 5.856 MB de C1-A,
uma diferença de ~581 MB que corresponde à memória consumida pela pilha RAG
(Streamlit, ChromaDB com vetores indexados, dependências LangChain).

A hipótese é que a memória extra consumida pelo RAG reduziu o espaço disponível para
a KV-cache do modelo, forçando mais operações de alocação e, possivelmente, aumentando
a latência de acesso à memória durante a inferência. Como ambas as configurações usaram
a mesma query simples (sem passar pelo pipeline RAG), a lentidão vem puramente da
pressão de memória.

---

## Q21 — Qual foi o impacto de usar um modelo menor (C3-A: deepseek-r1:1.5b)?

O deepseek-r1:1.5b obteve TTFT médio de 27,36 s, comparado a 65,81 s do 7B para a
mesma query curta, uma redução de 58% na latência. O modelo 1.5B tem apenas ~1 GB em
GGUF Q4_K_M vs 4,7 GB do 7B, o que resulta em:

- Menos pesos para multiplicar por ativação em cada camada
- Modelo menor cabe em mais caches de CPU (L3), reduzindo stalls de memória
- Número de camadas e tamanho de atenção menores (menos operações por token)

O custo foi 26 threads observadas (vs 15 do 7B), pois o segundo modelo criou um novo
processo llama-server adicional que coexistiu com o do 7B. A qualidade da resposta do
1.5B é naturalmente inferior para tarefas complexas, mas para perguntas simples a
diferença prática é pequena.

---

## Q22 — O que o experimento C3-B revelou sobre o impacto do tamanho de contexto?

C3-B usou `num_ctx=2048` (vs o padrão de 8192 das outras configurações). O TTFT médio
foi de 33,49 s, similar ao C3-A com modelo 1.5B. A redução de contexto de 8192 para
2048 tokens diminui a KV-cache máxima alocada em ~4×, liberando RAM para outras
operações.

O experimento revelou um fenômeno importante: a repetição 1 de C3-B teve total de
188.217 ms, mas TTFT de apenas 28,92 s. A discrepância ocorreu porque mudar num_ctx
forçou o Ollama a recarregar o modelo com nova alocação de KV-cache, adicionando
~160 s de overhead de reload. A repetição 2, com o modelo já carregado no novo
tamanho, levou apenas 38.542 ms, confirmando que o custo foi de inicialização, não
de inferência.

---

## Q23 — Qual syscall dominou o processo ollama serve durante a inferência?

Conforme documentado na Parte B (strace-resumo.txt), a syscall `futex` representou
76,59% das chamadas no processo ollama serve. O futex (Fast Userspace muTEX) coordena
as 11 threads do llama-server sem precisar entrar no kernel quando não há contenção,
minimizando o custo de sincronização. Cada camada do transformer requer uma barreira
de sincronização entre threads, e com centenas de camadas por inferência, o futex é
a syscall mais frequente de longe.

---

## Q24 — O que os dados revelam sobre gargalos do sistema?

Os experimentos evidenciam três gargalos distintos:

O gargalo primário é a CPU: sem GPU, cada token requer multiplicações matriciais densas
nos 11 threads do llama-server. O modelo 7B demora em média 0,6-1,5 s por token,
resultando em latências de 60-570 s dependendo do tamanho da saída.

O gargalo secundário é a memória RAM: com 7,8 GB disponíveis e o modelo 7B consumindo
4,7 GB, sobram apenas ~3 GB para sistema, RAG e KV-cache. Quando o RAG ativo ou um
segundo modelo consomem parte desse espaço, a pressão de memória aumenta a latência.

O gargalo terciário é a serialização do Ollama: como demonstrado em C2-A, o servidor
não processa requisições em paralelo na CPU, criando fila de espera proporcional ao
número de clientes simultâneos.

---

## Q25 — Como o SO gerencia os recursos durante a inferência?

Durante os experimentos, o SO realizou as seguintes funções observadas:

**Escalonamento de CPU (CFS):** Distribuiu os time slices entre as 11 threads do
llama-server e os demais processos do sistema. O llama-server recebeu ~97% de uso de
CPU por ser CPU-bound e não realizar bloqueios desnecessários.

**Gerenciamento de memória:** O modelo foi mapeado via mmap no carregamento, permitindo
ao kernel paginar sob demanda. A KV-cache cresce dinamicamente com malloc; em C3-B,
a mudança de num_ctx forçou uma realocação do heap inteiro, visível nos 160 s de
overhead de reload.

**Sincronização de threads:** O kernel atendeu futex calls para as barreiras entre
camadas do transformer, com baixíssima contenção (retorno imediato em userspace na
maioria das chamadas).

**Escalonamento de I/O:** O Ollama serve requisições HTTP via epoll_pwait no loopback,
garantindo que a chegada de uma segunda requisição (C2-A) fosse detectada e enfileirada
sem busy-waiting.

---

## Q26 — Conclusão

Os experimentos confirmam que LLMs 7B em CPU são viáveis para uso acadêmico, mas
revelam limites claros: latência mínima de ~27 s (modelo 1.5B) a ~65 s (7B, query
curta) e até 535 s para respostas longas. A redução de contexto e o uso de modelos
menores são as alavancas mais efetivas para reduzir latência sem hardware especializado.

A relação entre SO e LLM é profunda: o escalonador CFS, o gerenciador de memória
virtual, o futex de sincronização e o epoll de I/O são os pilares que tornam possível
rodar um modelo de 4,7 GB em um laptop com 7,8 GB de RAM. Os experimentos tornaram
visíveis mecanismos que normalmente são transparentes ao usuário final, demonstrando
como o SO é o substrato indispensável de qualquer aplicação de IA local.
