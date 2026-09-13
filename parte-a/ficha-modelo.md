# Ficha Técnica — Modelo deepseek-r1:7b

## Identificação

| Campo | Valor |
|---|---|
| Organização | DeepSeek AI |
| Nome do modelo | DeepSeek-R1-Distill-Qwen-7B |
| Tag Ollama | `deepseek-r1:7b` |
| URL Hugging Face | https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B |
| Número de parâmetros | 7 bilhões (7B) |
| Finalidade | Raciocínio e geração de texto (chat/instrução), com cadeia de pensamento explícita (`<think>`) |
| Idiomas | Multilíngue — primário: inglês e chinês; suporte a português limitado |
| Licença | MIT License |

## Formato e Quantização

| Campo | Valor |
|---|---|
| Formato | GGUF |
| Quantização (Ollama padrão) | Q4_K_M (4 bits, mixed precision) |
| Tamanho do arquivo | ~4,7 GB |
| Janela de contexto (original) | 128.000 tokens |
| Janela de contexto (configurada) | 8.192 tokens (`num_ctx=8192`) |

## Requisitos de Hardware

| Recurso | Valor |
|---|---|
| RAM mínima recomendada | 8 GB |
| RAM utilizada neste experimento | ~5–6 GB (CPU only, WSL2) |
| VRAM (GPU) | Não utilizado — inferência 100% CPU |
| Tempo médio de resposta observado | 8–10 minutos por query (CPU, WSL2, 7,8 GB RAM) |

## Riscos e Viés

- Raciocínio interno (`<think>`) gerado predominantemente em inglês, mesmo com prompts em português
- Possibilidade de alucinação em respostas longas, especialmente fora do contexto fornecido
- Viés cultural orientado ao contexto acadêmico e técnico ocidental/asiático
- Respostas em português podem apresentar construções sintáticas atípicas

## Justificativa de Escolha (≤ 100 palavras)

O `deepseek-r1:7b` foi escolhido por ser o modelo de raciocínio de maior qualidade disponível localmente dentro da restrição de 8 GB de RAM. Sua arquitetura de destilação do DeepSeek-R1 preserva a cadeia de pensamento explícita, tornando o processo de inferência observável e analisável — relevante para os objetivos da atividade. A licença MIT permite uso irrestrito em contexto acadêmico. Em comparação com modelos menores como `phi3` ou `tinyllama`, oferece melhor compreensão semântica dos chunks do PDF, gerando respostas mais coerentes no pipeline RAG.
