"""
02_descritivas.py
Estatística descritiva da despesa por função: tabela-resumo por exercício e
gráficos de composição do gasto municipal agregado de MG.

Requer: rodar antes o 01_tratamento_finbra.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROC = Path("data/processed")
TAB = Path("outputs/tabelas")
FIG = Path("outputs/graficos")
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(PROC / "gastos_funcao_mg.csv")

# ------------------------------------------------ 1. resumo por função e ano
# n = municípios com a função; per capita permite comparar entes de portes distintos
resumo = (
    df.groupby(["ano", "Conta"])["per_capita"]
    .agg(
        n="count",
        media="mean",
        mediana="median",
        desvio="std",
        p25=lambda s: s.quantile(0.25),
        p75=lambda s: s.quantile(0.75),
    )
    .round(2)
    .reset_index()
)
resumo.to_csv(TAB / "descritivas_funcao_per_capita.csv", index=False)
print(f"OK -> {TAB / 'descritivas_funcao_per_capita.csv'}")

# --------------------------- 2. composição do gasto agregado de MG por função
total = df.groupby(["ano", "Conta"])["Valor"].sum().reset_index()
total["particip_pct"] = (
    total["Valor"] / total.groupby("ano")["Valor"].transform("sum") * 100
)
total.round(2).to_csv(TAB / "composicao_funcao.csv", index=False)

for ano, g in total.groupby("ano"):
    top = g.nlargest(10, "particip_pct").sort_values("particip_pct")
    plt.figure(figsize=(9, 6))
    plt.barh(top["Conta"], top["particip_pct"], color="#0C7C46")
    plt.xlabel("Participação no gasto total dos municípios de MG (%)")
    plt.title(f"Composição da despesa municipal por função — MG, {ano}")
    plt.tight_layout()
    plt.savefig(FIG / f"composicao_funcao_{ano}.png", dpi=200)
    plt.close()
    print(f"OK -> {FIG / f'composicao_funcao_{ano}.png'}")

# ------------------------- 3. exemplo de comparação entre entes (ranking)
FUNCAO_EXEMPLO = "10 - Saúde"  # ajuste conforme o TCC
rank = (
    df[df["Conta"] == FUNCAO_EXEMPLO]
    .sort_values(["ano", "per_capita"], ascending=[True, False])
    .groupby("ano")
    .head(20)[["ano", "Instituição", "per_capita"]]
    .round(2)
)
rank.to_csv(TAB / "ranking_saude_per_capita_top20.csv", index=False)
print(f"OK -> {TAB / 'ranking_saude_per_capita_top20.csv'}")
