"""
03_mapas.py
Mapas coropléticos da despesa per capita por função, sobre a malha municipal
do IBGE (baixada automaticamente pelo pacote geobr — requer internet no
primeiro uso).

Requer: rodar antes o 01_tratamento_finbra.py
"""

from pathlib import Path

import geobr
import matplotlib.pyplot as plt
import pandas as pd

PROC = Path("data/processed")
MAPAS = Path("outputs/mapas")
MAPAS.mkdir(parents=True, exist_ok=True)

FUNCOES = ["10 - Saúde", "12 - Educação"]  # ajuste conforme o TCC
ANOS = [2023, 2024, 2025]

# malha territorial municipal do IBGE (ano de referência da malha: 2022)
malha = geobr.read_municipality(code_muni="MG", year=2022)
malha["code_muni"] = malha["code_muni"].astype(int)

dados = pd.read_csv(PROC / "gastos_funcao_mg.csv")
dados = dados.dropna(subset=["Cod.IBGE"])
dados["Cod.IBGE"] = dados["Cod.IBGE"].astype(int)

for funcao in FUNCOES:
    for ano in ANOS:
        recorte = dados[(dados["Conta"] == funcao) & (dados["ano"] == ano)]
        if recorte.empty:
            print(f"[aviso] sem dados para {funcao} em {ano} — pulando.")
            continue

        mapa = malha.merge(recorte, left_on="code_muni", right_on="Cod.IBGE", how="left")

        ax = mapa.plot(
            column="per_capita",
            cmap="viridis",
            legend=True,
            figsize=(10, 10),
            missing_kwds={"color": "#d9d9d9", "label": "sem dado (DCA não entregue)"},
            legend_kwds={"label": "R$ per capita", "shrink": 0.6},
        )
        ax.set_axis_off()
        ax.set_title(
            f"{funcao} — despesa liquidada per capita, {ano}\n"
            "Municípios de MG · FINBRA/SICONFI · malha IBGE",
            fontsize=12,
        )

        nome = funcao.split(" - ")[1].lower().replace(" ", "_")
        destino = MAPAS / f"mapa_{nome}_per_capita_{ano}.png"
        plt.savefig(destino, dpi=200, bbox_inches="tight")
        plt.close()
        print(f"OK -> {destino}")
