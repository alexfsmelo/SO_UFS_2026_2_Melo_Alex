# Declaração de Uso de IA Generativa

## Ferramenta e modelo utilizados

Claude Sonnet 4.6 (Anthropic), acessado via interface Claude Cowork durante a elaboração deste trabalho.

---

## Finalidade de cada uso

- Geração do script Python para produção dos gráficos de latência e RAM (`parte-c/gerar_graficos.py`), a partir dos dados brutos coletados manualmente nos experimentos.
- Auxílio na redação e formatação do relatório (.docx), incluindo estruturação das seções, tabela de resultados e respostas às questões Q16-Q26 com base nas observações dos experimentos.
- Elaboração do `README.md` com instruções de instalação e reprodução dos experimentos.

---

## Alguns prompts usados

1. *"Gere um script Python que plote os gráficos de TTFT e uso de RAM para as configurações C1-A a C3-B, usando os dados abaixo."*
2. "Crie um script Bash que envie uma query para a API do Ollama, meça o TTFT e o tempo total de resposta em segundos, capture o uso de RAM do processo ollama com ps, e salve tudo em CSV com cabeçalho config, rep, ttft_s, total_ms, ram_mb."
3. *"Me ajude a montar o README.md com instalação, execução e reprodução dos experimentos."*

---


## Verificação das respostas

- Todos os valores numéricos da tabela de resultados (TTFT, tempo total, RAM) foram coletados diretamente via API REST do Ollama e `ps`/`htop`, e conferidos contra os dados brutos antes de inserção no relatório.
- Os gráficos gerados foram comparados visualmente com os dados da tabela para validar escala e valores.
