# Parte C - Analise dos Experimentos

## Configuracao do ambiente

Todos os experimentos foram executados em 15/09/2026 em WSL2 (Ubuntu) com CPU Intel x64,
7,8 GB de RAM disponiveis, Ollama 0.6.2, modelo principal DeepSeek-R1-Distill-Qwen-7B
(GGUF Q4_K_M, 4,7 GB) para inferencia e nomic-embed-text para embeddings RAG.
Nenhuma GPU foi utilizada. Inferencia 100% CPU.

---

## Tabela consolidada de experimentos

| Config | Variante | Rep | TTFT (s) | Total (ms) | RAM (MB) | Threads | Obs |
|--------|----------|-----|----------|------------|----------|---------|-----|
| C1-A | padrao/curta | 1 | 71,48 | 71.801 | 5.847 | 15 | |
| C1-A | padrao/curta | 2 | 60,13 | 60.488 | 5.865 | 15 | |
| C1-B | padrao/longa | 1 | 337,00 | 343.199 | 5.981 | 19 | |
| C1-B | padrao/longa | 2 | 535,16 | 536.360 | 6.021 | 15 | |
| C2-A | concorrente | 1 | 139,07 | 230.013 | 5.315 | 15 | 2 req simultaneas |
| C2-A | concorrente | 2 | 84,42 | 117.180 | 5.346 | 15 | 2 req simultaneas |
| C2-B | rag-ativo/curta | 1 | 62,68 | 66.013 | 6.429 | 15 | RAG pipeline ativo |
| C2-B | rag-ativo/curta | 2 | 132,49 | 132.870 | 6.444 | 15 | RAG pipeline ativo |
| C3-A | quant-1.5b | 1 | 23,37 | 55.324 | 6.602 | 26 | modelo menor |
| C3-A | quant-1.5b | 2 | 31,35 | 31.542 | 6.616 | 26 | modelo menor |
| C3-B | ctx-2048 | 1 | 28,92 | 188.217 | 6.399 | 26 | ctx restrito (reload) |
| C3-B | ctx-2048 | 2 | 38,05 | 38.542 | 6.411 | 26 | ctx restrito |

**Total: 12 execucoes validas em 6 sub-configuracoes.**

### Medias por configuracao

| Config | Descricao | TTFT medio (s) | Total medio (ms) | RAM media (MB) |
|--------|-----------|----------------|-----------------|----------------|
| C1-A | padrao, query curta | 65,81 | 66.145 | 5.856 |
| C1-B | padrao, query longa | 436,08 | 439.780 | 6.001 |
| C2-A | concorrente (2 req) | 111,75 | 173.597 | 5.331 |
| C2-B | RAG pipeline ativo | 97,59 | 99.442 | 6.437 |
| C3-A | modelo 1.5b | 27,36 | 43.433 | 6.609 |
| C3-B | ctx=2048 | 33,49 | 113.380 | 6.405 |

---

## Secao 9 - Analise e Discussao

### Q16 - Por que a Trilha C e adequada a disciplina de SO?

O pipeline RAG sobre PDF mobiliza os quatro pilares classicos de SO de forma direta e
mensuravel. No eixo de processos, a aplicacao cria uma hierarquia de quatro processos
distintos (ollama serve, dois llama-server, Streamlit) com papeis bem definidos de
orquestrador e worker, permitindo observar estados R/S/Ssl, hierarquia de PID/PPID e
uso de threads. No eixo de memoria, o modelo deepseek-r1:7b em GGUF Q4_K_M ocupa 4,7 GB
de RAM, forcando o kernel a gerenciar mmap, KV-cache dinamica e pressao de memoria real
em hardware limitado (7,8 GB disponiveis). No eixo de E/S, o Ollama serve requisicoes
HTTP via epoll_pwait e o pipeline RAG le PDFs do disco, gera embeddings e grava vetores
no ChromaDB. No eixo de armazenamento, o modelo em GGUF e o banco vetorial persistem em
disco e sao carregados sob demanda. Os experimentos produziram metricas concretas de cada
um desses recursos, tornando a Trilha C um caso de estudo integrado dos conceitos da
disciplina.

---

### Q17 - Qual modelo foi escolhido, seus parametros e justificativa?

Modelo: DeepSeek-R1-Distill-Qwen-7B. Organizacao: DeepSeek AI. Familia: destilacao do
DeepSeek-R1 sobre base Qwen-7B. Parametros: 7 bilhoes. Quantizacao utilizada: GGUF Q4_K_M
(4 bits, mixed precision), aproximadamente 4,7 GB em disco. Janela de contexto configurada:
8.192 tokens (original: 128.000). Licenca: MIT.

URL HuggingFace: https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B

Tag Ollama: `deepseek-r1:7b`

A escolha se justifica pela combinacao de qualidade de raciocinio com viabilidade em
hardware restrito: dentro do orcamento de 8 GB de RAM disponiveis, o 7B em Q4_K_M foi
o maior modelo que coube sem swap. Sua cadeia de pensamento explicita (`<think>`) torna
o processo de inferencia observavel, o que e pedagogicamente relevante para a disciplina
de SO. Em comparacao com modelos menores como phi3 ou tinyllama, oferece melhor
compreensao semantica dos chunks do PDF para perguntas de multiplas etapas.

---

### Q18 - Impacto de formato, quantizacao, contexto e tamanho em RAM e armazenamento

Os experimentos C3-A e C3-B isolaram dois parametros distintos:

**C3-A (tamanho e quantizacao do modelo):** substituicao do deepseek-r1:7b (Q4_K_M,
4,7 GB, TTFT medio de 65,81 s) pelo deepseek-r1:1.5b (GGUF Q4, aproximadamente 1 GB,
TTFT medio de 27,36 s). A reducao de tamanho produziu 58% menos latencia e
aproximadamente 3,7 GB a menos em disco. Em RAM, porem, o total subiu para 6.609 MB
porque ambos os modelos permaneceram carregados simultaneamente (7B + 1.5B + overhead).
O numero de threads observado subiu de 15 para 26, refletindo dois processos llama-server
coexistindo.

**C3-B (tamanho de contexto):** reduzir `num_ctx` de 8.192 para 2.048 tokens reduziu
a KV-cache maxima alocada em aproximadamente 4x e produziu TTFT medio de 33,49 s.
A primeira repeticao teve tempo total de 188.217 ms com TTFT de 28,92 s: a discrepancia
revela que a mudanca de contexto forcou o Ollama a recarregar o modelo com nova alocacao
de KV-cache, adicionando aproximadamente 160 s de overhead de reload. A segunda repeticao,
com modelo ja estabilizado, levou 38.542 ms. O custo de mudar `num_ctx` em producao e,
portanto, uma reinicializacao completa do processo llama-server.

---

### Q19 - Processos e threads observados na inicializacao e na inferencia

Na inicializacao do Ollama (antes de qualquer requisicao), apenas `ollama serve`
(PID 157, PPID 1/systemd, 12 threads, estado Ssl) estava presente. Ao carregar o
modelo de embeddings, surgiu `llama-server` para `nomic-embed-text` (PID 1029, PPID 157,
11 threads, estado S, aproximadamente 10% CPU durante indexacao). Ao receber a primeira
query de chat, surgiu um segundo `llama-server` para `deepseek-r1:7b` (PID 1059,
PPID 157, 11 threads, estado R durante inferencia, 97-98% CPU).

O Streamlit foi iniciado por `run.py` (PID 846, PPID 394) e manteve 21 threads em
estado S para gerenciar conexoes WebSocket via Tornado/asyncio. Durante a inferencia,
o total de threads observado nos experimentos C1/C2 foi de 15 (11 do deepseek + 1
ollama serve + 3 do Python/Streamlit em background) e subiu para 26 em C3-A (dois
llama-server simultaneos). Nao foram observados estados D ou Z em nenhum momento.

Hierarquia de processos:
- PID 1 (systemd) -> PID 157 (ollama serve, 12 threads)
- PID 157 -> PID 1029 (llama-server nomic-embed-text, 11 threads)
- PID 157 -> PID 1059 (llama-server deepseek-r1:7b, 11 threads, 97% CPU)
- PID 846 (run.py/Streamlit, 21 threads, estado S)

---

### Q20 - Chamadas de sistema relevantes para carga, comunicacao e logs

O strace capturado no processo ollama serve (PID 157) durante aproximadamente 3 minutos
de inferencia registrou 45 chamadas em 0,030 s de CPU com o seguinte perfil:

`futex` (76,59%, 20 chamadas): sincronizacao entre o ollama serve e o subprocesso
llama-server. O orquestrador bloqueia em futex_wait aguardando a resposta do worker,
liberando CPU enquanto espera. Cada camada do transformer requer uma barreira de
sincronizacao entre threads, tornando o futex a syscall mais frequente de longe.

`nanosleep` (15,81%, 15 chamadas): polling com backoff. O Ollama dorme brevemente entre
verificacoes do estado do llama-server para evitar busy-wait, cedendo CPU ao escalonador.

`sched_yield` (2,31%, 5 chamadas): cessao voluntaria de CPU ao escalonador, usada em
situacoes de leve contencao de lock.

`epoll_pwait` (1,69%, 3 chamadas): monitoramento de conexoes HTTP na porta 11434. Permite
que o ollama serve atenda multiplas conexoes sem bloquear uma thread por cliente.

`sched_getaffinity` (0,20%, 1 chamada): consulta de afinidade de CPU, provavelmente na
inicializacao para identificar nucleos disponiveis e configurar o numero de threads do
llama-server.

O perfil confirma que o ollama serve e um orquestrador leve: 92% do tempo esta em espera
(futex + nanosleep), nao em computacao. A inferencia real ocorre no llama-server.

---

### Q21 - O aumento de concorrencia melhorou responsividade ou vazao? Quais custos surgiram?

Nao. O experimento C2-A enviou 2 requisicoes simultaneas ao Ollama e revelou que o
servidor serializa internamente: a requisicao 1 foi processada primeiro (TTFT de 139,07 s
e 84,42 s nas duas reps), enquanto a requisicao 2 aguardou na fila. O tempo de wall-clock
total foi de 230.013 ms e 117.180 ms respectivamente, contra 66.145 ms em media para
C1-A com requisicao unica. O overhead de fila foi de aproximadamente 91 s na rep 1
(230.013 - 139.070 = 90.943 ms) e aproximadamente 33 s na rep 2.

O Ollama em CPU nao implementa batching real: o llama-server utiliza todos os nucleos
disponiveis para uma unica geracao, sem capacidade ociosa para paralelizar. O custo da
concorrencia foi maior latencia percebida para todos os clientes, sem ganho de throughput.
Em GPU, batching verdadeiro permitiria processar multiplas requisicoes simultaneamente,
pois a VRAM e a largura de banda de memoria sao suficientes para multiplos contextos.

---

### Q22 - Houve competicao por CPU, memoria, armazenamento, GPU ou rede?

**CPU:** intensa. O llama-server deepseek-r1:7b ocupou 97-98% de CPU durante toda a
inferencia, competindo com o Windows/WSL2 host e com os demais processos do sistema.
O CFS distribuiu os time slices entre as 11 threads do llama-server e os demais,
causando a alta variancia observada (CV de 17% a 50% dependendo da configuracao).

**Memoria RAM:** significativa. O modelo 7B consumiu aproximadamente 4,7 GB de 7,8 GB
disponiveis. Quando o RAG stack (Streamlit + ChromaDB) estava ativo (C2-B), o uso subiu
para 6.437 MB vs 5.856 MB em C1-A, diferenca de aproximadamente 581 MB. Em C3-A (dois
modelos carregados), o uso chegou a 6.609 MB. Nenhum swap foi ativado, mas a margem
restante era inferior a 1,2 GB.

**GPU:** sem competicao. Nenhuma GPU foi utilizada; a inferencia ocorreu 100% em CPU.

**Rede:** sem competicao relevante. Toda comunicacao foi via loopback (127.0.0.1:11434),
com overhead negligivel (epoll_pwait representou apenas 1,69% das syscalls). O PDF
nunca trafegou pela rede externa.

**Armazenamento:** baixa competicao. O modelo GGUF foi mapeado em memoria no carregamento
via mmap; acessos subsequentes ocorrem em RAM, sem I/O de disco durante a inferencia.

---

### Q23 - Como entradas ou contextos maiores afetaram desempenho e recursos?

**C1-A vs C1-B (tamanho da query de saida, num_ctx=8192 fixo):** o TTFT medio saltou de
65,81 s para 436,08 s, diferenca de 6,6x. A RAM subiu de 5.856 para 6.001 MB (+145 MB).
O fator determinante foi o tamanho da resposta gerada: query longa exige muito mais tokens
de saida, e com custo linear por token em CPU, a latencia cresce proporcionalmente.
O tempo total segue o TTFT de perto (diferenca < 1%), confirmando que o gargalo e a
geracao de tokens, nao overhead de rede ou pre-processamento.

**C1-A vs C3-B (num_ctx=8192 vs num_ctx=2048, mesma query curta):** o TTFT caiu de
65,81 s para 33,49 s (-49%). A reducao do contexto encolheu a KV-cache maxima alocada
em aproximadamente 4x, liberando RAM e reduzindo stalls de memoria durante a geracao.
O custo foi a impossibilidade de processar documentos longos ou historicos de conversa
extensos.

O experimento C3-B tambem revelou que a primeira execucao com um novo num_ctx tem
overhead adicional de aproximadamente 160 s de reload do modelo: o Ollama precisa
reiniciar o llama-server com nova alocacao de heap, conforme observado na discrepancia
entre total_ms (188.217) e ttft_s (28,92) na repeticao 1. A repeticao 2, com modelo ja
estabilizado no novo tamanho, levou apenas 38.542 ms total.

---

### Q24 - Como a arquitetura local contribui para privacidade, disponibilidade e controle de dados?

**Privacidade:** o PDF enviado pelo usuario e processado inteiramente dentro do WSL2, sem
trafego de rede externo. Os vetores gerados pelo nomic-embed-text sao armazenados no
ChromaDB local. Nenhum fragmento do documento chega a servidores de terceiros, o que e
critico para documentos sensiveis (contratos, dados pessoais, pesquisa nao publicada).
Em comparacao, APIs remotas como OpenAI ou Google recebem o conteudo dos chunks como
contexto de cada requisicao, o que implica transferencia de dados para infraestrutura
fora do controle do usuario.

**Disponibilidade:** a inferencia funciona sem conexao a internet apos o download inicial
dos modelos. Nao ha dependencia de SLA de terceiros, limites de rate, janelas de
manutencao ou mudancas de preco. O tempo de resposta e determinado pelo hardware local.

**Controle de dados:** o usuario controla integralmente os modelos utilizados, as versoes,
os parametros de inferencia (num_ctx, temperatura) e os logs gerados. E possivel auditar
cada etapa do pipeline. Isso esta alinhado com requisitos de conformidade (LGPD, GDPR)
onde a transferencia de dados para terceiros requer consentimento explicito.

**Contrapartida de custo:** a latencia e significativamente maior (65-436 s vs menos de
5 s em GPU cloud), e o hardware requer investimento inicial. Para uso academico ou
processamento assincrono de documentos sensiveis, o tradeoff e favoravel.

---

### Q25 - Quais limitacoes ameacam a validade dos resultados?

**WSL2 vs Linux nativo:** o WSL2 introduz camada de virtualizacao entre o Linux e o
hardware Windows. O CFS do Linux guest compete com o scheduler do Windows host, e o
acesso a memoria passa por uma camada de traducao adicional. Latencias medidas em WSL2
sao tipicamente 10-30% maiores que em Linux bare-metal com hardware equivalente.

**Carga variavel do Windows:** processos do Windows (antivirus, OneDrive, atualizacoes)
competiram por CPU e RAM durante os experimentos, sem controle ou isolamento. Isso
explica parte da variancia observada (CV de 17% a 50% conforme a configuracao).

**Ausencia de GPU:** todos os experimentos usaram inferencia CPU. Com GPU (mesmo uma
RTX 3080 de entrada), a latencia seria 10-50x menor, mudando completamente o perfil de
recursos (mais VRAM, menos RAM, menos threads de CPU). Os resultados nao sao
generalizaveis para ambientes com aceleracao de hardware.

**Numero reduzido de repeticoes:** apenas 2 repeticoes por sub-configuracao. Para calcular
intervalos de confianca estatisticamente robustos, seriam necessarias pelo menos 30
repeticoes por condicao. Os resultados indicam tendencias, nao medias estaveis.

**Ausencia de isolamento de processos:** o Streamlit e o ChromaDB permaneceram ativos
durante os experimentos de API direta (C1, C2), interferindo na RAM disponivel e
possivelmente na latencia de inferencia.

**Uma unica versao de modelo e quantizacao por configuracao:** nao foi possivel testar
Q4_K_M vs Q8_0 para o mesmo modelo 7B por limitacao de armazenamento e tempo de
download disponivel para os experimentos.

---

### Q26 - Informacoes geradas por IA que precisaram ser verificadas, corrigidas ou rejeitadas

Durante o desenvolvimento deste trabalho, o Claude Sonnet 4.6 (Anthropic), acessado via
Claude Cowork, foi utilizado como assistente principal. Os casos mais relevantes de
verificacao foram:

**Aproveitado sem modificacao:** a estrutura do script medir.sh com
`python3 -c "import time; print(int(time.time()*1000))"` para evitar overflow de
timestamp. Verificado com a primeira execucao bem-sucedida (total=95.326 ms valido).

**Sugerido e corrigido:** o script original usava `date +%s%3N` que produziu
total=-1.610.536.728.405.098.614 ms no WSL2 (nanosegundos em vez de milissegundos).
Identificado pelo resultado absurdo e corrigido com a alternativa em Python.

**Sugerido e rejeitado parcialmente:** o assistente numerou suas proprias perguntas Q16-Q26
no arquivo analise-experimentos.md com conteudo diferente das perguntas Q16-Q26 do
professor. O conteudo tecnico das respostas era correto, mas precisou ser reescrito
mapeando as perguntas corretas do enunciado oficial.

**Interpretacao incorreta corrigida:** o assistente sugeriu interpretar o campo
threads=26 como indicativo de alto paralelismo de inferencia do modelo. Na verdade, o
valor refletia dois processos llama-server coexistindo simultaneamente (um para o 7B,
outro para o 1.5B em C3-A), o que foi corrigido na analise.

**Verificado contra dados reais:** todas as medias e percentuais citados nas analises
foram conferidos manualmente contra o CSV (experimentos.csv) antes de serem incluidos
no relatorio. Por exemplo, o TTFT medio de C3-A foi calculado como
(23,37 + 31,35) / 2 = 27,36 s, confirmado no CSV.

**Erro de codigo depurado:** o gerar_graficos.py falhou com
`ModuleNotFoundError: No module named 'pandas'` porque o pip instalou no ambiente errado.
Corrigido com `pip install matplotlib pandas --break-system-packages`.

---

## Secao 10 - Declaracao de Uso de IA Generativa

Este trabalho utilizou o modelo Claude Sonnet 4.6 (Anthropic), acessado via Claude Cowork,
como ferramenta de apoio ao desenvolvimento e documentacao. O uso ocorreu nas seguintes
finalidades:

**Apoio a codificacao:** geracao e depuracao dos scripts `medir.sh` e `gerar_graficos.py`,
correcao de bugs como overflow de timestamp e ModuleNotFoundError. Todos os scripts foram
testados e executados pelo autor no ambiente WSL2, com saidas verificadas antes de
qualquer uso nos experimentos.

**Apoio a documentacao:** estruturacao inicial das fichas tecnicas (ficha-aplicacao.md,
ficha-modelo.md) e da analise de syscalls. Todos os dados tecnicos (PIDs, percentuais de
CPU, tempos de resposta, versoes de pacotes) foram coletados diretamente dos comandos
executados pelo autor e inseridos ou verificados manualmente no texto.

**Cinco prompts representativos utilizados:**

1. "Crie um script bash para medir TTFT e uso de RAM ao fazer uma query a API do Ollama,
   salvando em CSV."
2. "O script deu erro: total=-1610536728405098614ms. Como corrigir o timing?"
3. "Escreva a ficha tecnica do modelo deepseek-r1:7b com base na saida do `ollama list`
   e `pip list` que vou colar."
4. "Analise o output do strace que colei e explique cada familia de syscall no contexto
   de SO."
5. "Gere o script gerar_graficos.py que le o CSV e produz um grafico de barras de
   latencia media por configuracao, sem tracos duplos nos titulos."

**Sugestoes aproveitadas:** estrutura do script medir.sh; analise de familias de syscalls
baseada nos dados do strace; texto das fichas tecnicas como ponto de partida (revisado e
complementado pelo autor).

**Sugestoes corrigidas:** timing com `date +%s%3N` substituido por Python; numeracao
propria Q16-Q26 do assistente substituida pelas perguntas do professor; remocao de todos
os tracos duplos (travessoes) nos arquivos apos revisao.

**Sugestoes rejeitadas:** o assistente sugeriu interpretar threads=26 como alto paralelismo
de inferencia; na verdade era resultado de dois processos llama-server coexistindo
(7B + 1.5B), corrigido na analise.

**Como as respostas foram verificadas:** todos os comandos sugeridos pelo assistente foram
executados pelo autor no terminal WSL2; saidas foram revisadas antes de qualquer commit;
dados numericos foram conferidos contra o CSV e outputs de ps/strace. O autor e
responsavel integral pelo conteudo final entregue.
