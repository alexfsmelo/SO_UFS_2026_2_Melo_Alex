# Ficha Técnica — Aplicação ollama_pdf_rag

## Identificação

| Campo | Valor |
|---|---|
| Nome | ollama_pdf_rag |
| URL do repositório | https://github.com/tonykipkemboi/ollama_pdf_rag |
| Autor / organização | Tony Kipkemboi |
| Licença | MIT License (Copyright © 2024 Tony Kipkemboi) |
| Commit utilizado | `f17f9c9` — tag `v3.0.0` (chore: Update changelog for v3.0.0 release) |
| Data de acesso | 2026-09-13 |

## Finalidade e Arquitetura

Aplicação de Recuperação Aumentada por Geração (RAG) sobre documentos PDF, executada localmente via Streamlit. O usuário faz upload de um ou mais PDFs, que são segmentados em chunks, vetorizados com embeddings e armazenados em um banco vetorial ChromaDB. Ao receber uma pergunta, o sistema recupera os trechos mais relevantes e os envia como contexto para um LLM local via Ollama, que gera a resposta.

**Componentes principais:**
- Interface web: Streamlit 1.63.0
- Pipeline RAG: LangChain 1.0.0 + LangChain-Community 0.4.2
- Banco vetorial: ChromaDB 1.5.9
- Embeddings: `nomic-embed-text` via Ollama
- LLM de resposta: `deepseek-r1:7b` via Ollama (ChatOllama)
- Carregamento de PDF: PyPDF 6.18.1 + PDFPlumber 0.11.10
- Recuperação: MultiQueryRetriever (LangChain)

## Dependências Instaladas

| Pacote | Versão |
|---|---|
| streamlit | 1.63.0 |
| langchain | 1.0.0 |
| langchain-community | 0.4.2 |
| langchain-chroma | 1.1.0 |
| langchain-ollama | 1.1.0 |
| langchain-core | 1.6.3 |
| chromadb | 1.5.9 |
| ollama | 0.6.2 |
| pypdf | 6.18.1 |
| pdfplumber | 0.11.10 |
| numpy | 2.5.3 |
| pillow | 12.3.0 |
| pydantic | 2.13.5 |

**Comando de instalação utilizado:**
```bash
pip install streamlit langchain langchain-community langchain-chroma \
  langchain-ollama chromadb pypdf pdfplumber \
  "Pillow>=11" "pydantic>=2.5" "numpy>=2.0"
```

> Nota: o `requirements.txt` original foi ignorado por incompatibilidades com Python 3.14 (numpy 1.26.4 sem wheel, pydantic-core exigindo gcc, pi_heif exigindo libheif). A instalação foi feita com versões compatíveis.

## Adaptações Realizadas

| Problema | Solução |
|---|---|
| `UnstructuredPDFLoader` exige pacote `unstructured` não disponível | Substituído por `PyPDFLoader` em `src/app/main.py` |
| Dropdown de modelos incluía `nomic-embed-text`, que era selecionado como padrão para chat | Adicionado filtro que exclui modelos com "embed" no nome antes de popular o `selectbox` |
| `MultiQueryRetriever.get_relevant_documents()` depreciado no LangChain 1.x | Substituído por `.invoke()` via `sed` |
| Contexto de 4096 tokens insuficiente para os chunks recuperados (erro 400) | `ChatOllama` inicializado com `num_ctx=8192` |
| `requirements.txt` incompatível com Python 3.14 | Instalação manual das dependências essenciais com versões atuais |
