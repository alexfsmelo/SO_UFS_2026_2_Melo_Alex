import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# Carregar CSV
df = pd.read_csv("parte-c/experimentos.csv")

# Remover linha com overflow se ainda existir
df = df[df["total_ms"] > 0]

# Mapeamento de configs para nomes legíveis e grupos
grupos = {
    "padrao":      ("C1-A/B Padrão", "#2196F3"),
    "concorrente": ("C2-A Concorrente", "#FF9800"),
    "rag-ativo":   ("C2-B RAG Ativo", "#9C27B0"),
    "quant-1.5b":  ("C3-A Modelo 1.5B", "#4CAF50"),
    "ctx-2048":    ("C3-B Ctx=2048", "#F44336"),
}

# Separar padrao/curta e padrao/longa
df["config_label"] = df.apply(
    lambda r: "padrao-longa" if r["config"] == "padrao" and r["query_size"] == "longa"
    else r["config"], axis=1
)

label_map = {
    "padrao":       "C1-A Padrão\n(curta)",
    "padrao-longa": "C1-B Padrão\n(longa)",
    "concorrente":  "C2-A\nConcorrente",
    "rag-ativo":    "C2-B\nRAG Ativo",
    "quant-1.5b":   "C3-A\nModelo 1.5B",
    "ctx-2048":     "C3-B\nCtx=2048",
}
cores = ["#2196F3","#1565C0","#FF9800","#9C27B0","#4CAF50","#F44336"]

order = ["padrao","padrao-longa","concorrente","rag-ativo","quant-1.5b","ctx-2048"]

# Filtrar apenas 2 reps mais recentes por sub-config para análise limpa
df_clean = []
for cfg in order:
    sub = df[df["config_label"] == cfg].tail(2)
    df_clean.append(sub)
df_clean = pd.concat(df_clean)

medias = df_clean.groupby("config_label")["ttft_s"].mean().reindex(order)
labels = [label_map[c] for c in order]

# === Gráfico 1: Latência TTFT média por configuração ===
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(labels, medias.values, color=cores, edgecolor="white", linewidth=0.5)

for bar, val in zip(bars, medias.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f"{val:.1f}s", ha="center", va="bottom", fontsize=9, fontweight="bold")

ax.set_ylabel("TTFT médio (segundos)", fontsize=11)
ax.set_title("Latência de inferência (TTFT) por configuração\nDeepSeek-R1 em CPU - WSL2, 7.8 GB RAM",
             fontsize=12, fontweight="bold")
ax.set_ylim(0, max(medias.values) * 1.15)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("parte-c/grafico-latencia.png", dpi=150)
plt.close()
print("✓ Salvo: parte-c/grafico-latencia.png")

# === Gráfico 2: RAM média por configuração ===
rams = df_clean.groupby("config_label")["ram_mb"].mean().reindex(order)

fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.bar(labels, rams.values, color=cores, edgecolor="white", linewidth=0.5)

for bar, val in zip(bars, rams.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
            f"{val/1024:.1f} GB", ha="center", va="bottom", fontsize=9, fontweight="bold")

ax.set_ylabel("RAM usada - media (MB)", fontsize=11)
ax.set_title("Uso de RAM por configuração", fontsize=12, fontweight="bold")
ax.set_ylim(0, max(rams.values) * 1.12)
ax.axhline(7800, color="red", linestyle="--", linewidth=1, alpha=0.7, label="Limite 7.8 GB")
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("parte-c/grafico-ram.png", dpi=150)
plt.close()
print("✓ Salvo: parte-c/grafico-ram.png")

print("\nTodos os gráficos gerados em parte-c/")
