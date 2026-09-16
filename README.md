# AV1 - Sistemas Operacionais (COMP0472)

**Universidade Federal de Sergipe | 2026.2**  
Trilha C: RAG sobre PDF com Modelos de Linguagem Locais

**Discente:** Álex Felipe Santos Melo (202200025395)  
**Professor:** Glauco Estácio Gonçalves

---

## Requisitos

- Windows 11 com WSL2 (Ubuntu 22.04)
- [Ollama](https://ollama.com) >= 0.6.2
- Python >= 3.10
- Git

---

## Instalação

### 1. Modelos Ollama

    ollama pull deepseek-r1:7b
    ollama pull deepseek-r1:1.5b
    ollama pull nomic-embed-text

### 2. Aplicação RAG

    git clone https://github.com/dusty-nv/ollama_pdf_rag
    cd ollama_pdf_rag
    git checkout f17f9c9
    pip install -r requirements.txt

---

## Execução

Inicie o servidor Ollama (se não estiver rodando):

    ollama serve

Em outro terminal, suba a interface RAG:

    streamlit run app.py

Acesse `http://localhost:8501`, faça upload do PDF e envie sua query.

---

## Reprodução dos Experimentos

Cada configuração é identificada por um código (C1-A a C3-B). As métricas coletadas por rodada são TTFT (s), tempo total (ms) e uso de RAM (MB), medidas via API REST do Ollama e `ps`/`htop`.

| Config | Variante          | Observação                        |
|--------|-------------------|-----------------------------------|
| C1-A   | Padrão, curta     | Baseline - query curta            |
| C1-B   | Padrão, longa     | Baseline - query longa            |
| C2-A   | Concorrente       | 2 requisições simultâneas         |
| C2-B   | RAG ativo         | Pipeline ChromaDB ligado          |
| C3-A   | Modelo menor      | deepseek-r1:1.5b no lugar do 7b   |
| C3-B   | Contexto restrito | num_ctx=2048 (padrão: 8192)       |

Para cada configuração, execute ao menos **4 rodadas** e utilize as **2 últimas** para cálculo das médias (metodologia tail(2)).

Os scripts de análise e geração de gráficos estão em `parte-c/`.

---

## Estrutura do Repositório

    .
    +-- parte-a/                  # Ficha da aplicação e do modelo
    +-- parte-b/                  # Análise de processos e syscalls
    +-- parte-c/                  # Scripts de experimentos e gráficos
    |   +-- analise-experimentos.md
    |   +-- gerar_graficos.py
    |   +-- grafico-latencia.png
    |   +-- grafico-ram.png
    +-- README.md

---

## Licença

Uso acadêmico -- COMP0472/UFS 2026.2.
