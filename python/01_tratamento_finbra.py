"""
01_tratamento_finbra.py
Lê os CSVs do FINBRA "Despesas por Função e Subfunção" (DCA), padroniza os
dados e filtra os municípios de Minas Gerais.

Saídas (em data/processed/):
  - gastos_funcao_mg.csv     -> município x função x ano
  - gastos_subfuncao_mg.csv  -> município x subfunção x ano

Antes de rodar:
  1. Baixe os CSVs conforme data/raw/COMO_BAIXAR.md
  2. Salve como data/raw/finbra_despesas_funcao_<ANO>.csv
"""

from pathlib import Path
import re

import pandas as pd

# ------------------------------------------------------------------ parâmetros
ANOS = [2023, 2024, 2025]
UF_ALVO = "MG"
# Estágio da despesa usado na análise (escolha metodológica — documente no TCC):
# "Despesas Empenhadas" | "Despesas Liquidadas" | "Despesas Pagas"
COLUNA_DESPESA = "Despesas Liquidadas"

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)


def ler_finbra(ano: int) -> pd.DataFrame:
    """Lê um CSV do FINBRA no padrão brasileiro (latin-1, ';', decimal ',')."""
    arquivo = RAW / f"finbra_despesas_funcao_{ano}.csv"
    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="latin-1",
        skiprows=3,   # linhas de título antes do cabeçalho — confira no seu arquivo
        decimal=",",  # decimal brasileiro: evita o clássico erro de separador
        thousands=".",
    )
    df.columns = [c.strip() for c in df.columns]
    df["ano"] = ano
    return df


def classificar_conta(conta: str) -> str:
    """Separa as linhas da coluna 'Conta' em função, subfunção e agregados.

    Padrões usuais no FINBRA (confirme no seu arquivo e ajuste as regex):
      função    -> "10 - Saúde"
      subfunção -> "10.301 - Atenção Básica"
    """
    conta = str(conta).strip()
    if re.match(r"^\d{2} - ", conta):
        return "funcao"
    if re.match(r"^\d{2}\.\d{3} - ", conta):
        return "subfuncao"
    return "agregado"  # totais e demais linhas


def tratar(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["UF"] == UF_ALVO].copy()
    df = df[df["Coluna"] == COLUNA_DESPESA].copy()

    df["nivel"] = df["Conta"].map(classificar_conta)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df["Cod.IBGE"] = pd.to_numeric(df["Cod.IBGE"], errors="coerce").astype("Int64")

    # população zerada ou ausente viraria divisão por zero no per capita
    df["População"] = pd.to_numeric(df["População"], errors="coerce")
    df.loc[df["População"] <= 0, "População"] = pd.NA
    df["per_capita"] = df["Valor"] / df["População"]
    return df


def main() -> None:
    bases = []
    for ano in ANOS:
        try:
            bases.append(tratar(ler_finbra(ano)))
        except FileNotFoundError:
            print(f"[aviso] data/raw/finbra_despesas_funcao_{ano}.csv não encontrado — pulando {ano}.")

    if not bases:
        raise SystemExit("Nenhum arquivo do FINBRA encontrado em data/raw/.")

    df = pd.concat(bases, ignore_index=True)
    colunas = ["ano", "Instituição", "Cod.IBGE", "População", "Conta", "Valor", "per_capita"]

    df.loc[df["nivel"] == "funcao", colunas].to_csv(OUT / "gastos_funcao_mg.csv", index=False)
    df.loc[df["nivel"] == "subfuncao", colunas].to_csv(OUT / "gastos_subfuncao_mg.csv", index=False)

    print("\nMunicípios de MG presentes por exercício (cobertura do FINBRA):")
    print(df.groupby("ano")["Cod.IBGE"].nunique().to_string())
    print(f"\nOK -> {OUT / 'gastos_funcao_mg.csv'}")
    print(f"OK -> {OUT / 'gastos_subfuncao_mg.csv'}")


if __name__ == "__main__":
    main()
