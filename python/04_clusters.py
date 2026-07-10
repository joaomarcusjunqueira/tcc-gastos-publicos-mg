"""
04_clusters.py
Análise de agrupamentos dos municípios mineiros pelo perfil de despesa
liquidada per capita por função, conforme a metodologia do TCC (seção 3.7):

  1. padronização das variáveis em escores z;
  2. etapa hierárquica: método de Ward (distância euclidiana quadrática);
  3. diagnósticos da quantidade de grupos: dendrograma, coeficientes de
     aglomeração e silhueta média das soluções candidatas;
  4. refinamento: K-means inicializado nos centroides da solução de Ward;
  5. caracterização dos grupos: médias per capita por função vs. conjunto.

IMPORTANTE: a escolha final do número de grupos é uma decisão analítica,
que combina dendrograma, coeficientes de aglomeração, silhueta média e
interpretabilidade. O script calcula os diagnósticos para todos os k
candidatos e adota, por padrão, o k de maior silhueta após o refinamento —
revise os diagnósticos antes de reportar no TCC.

Requer: rodar antes o 01_tratamento_finbra.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# ------------------------------------------------------------------ parâmetros
ANOS = [2023, 2024, 2025]
K_CANDIDATOS = range(2, 9)  # soluções candidatas avaliadas nos diagnósticos
SEMENTE = 42

PROC = Path("data/processed")
TAB = Path("outputs/tabelas")
FIG = Path("outputs/graficos")
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

dados = pd.read_csv(PROC / "gastos_funcao_mg.csv")


def centroides_ward(X: np.ndarray, rotulos: np.ndarray, k: int) -> np.ndarray:
    """Centroides dos grupos da solução hierárquica, usados como pontos de
    partida do K-means (integra as duas etapas em um procedimento único)."""
    return np.vstack([X[rotulos == g].mean(axis=0) for g in range(1, k + 1)])


for ano in ANOS:
    base = dados[dados["ano"] == ano].copy()
    if base.empty:
        print(f"[aviso] sem dados de {ano} em data/processed — pulando.")
        continue

    # municípios sem população declarada não têm per capita definido
    sem_pop = base.loc[base["per_capita"].isna(), "Cod.IBGE"].unique()
    if len(sem_pop) > 0:
        print(f"[aviso] {ano}: {len(sem_pop)} município(s) sem população — excluído(s) da matriz.")
        base = base[~base["Cod.IBGE"].isin(sem_pop)]

    # matriz municípios x funções; função sem registro = ausência de despesa
    # liquidada naquela função no exercício, logo per capita igual a zero
    matriz = base.pivot_table(
        index=["Cod.IBGE", "Instituição"],
        columns="Conta",
        values="per_capita",
        aggfunc="sum",
    ).fillna(0.0)

    # ------------------------------------------- 1. padronização em escores z
    # sem isso, funções de maior magnitude (saúde, educação) dominariam as
    # distâncias e distorceriam a formação dos grupos
    X = StandardScaler().fit_transform(matriz.values)

    # ------------------------------------- 2. etapa hierárquica (método de Ward)
    # o método de Ward opera sobre somas de quadrados: a cada passo funde o par
    # de grupos cuja união produz o menor aumento na soma de quadrados intragrupo
    Z = linkage(X, method="ward")

    # dendrograma (truncado nas últimas fusões, para legibilidade com 853 folhas)
    plt.figure(figsize=(10, 5))
    dendrogram(Z, truncate_mode="lastp", p=30, show_leaf_counts=True)
    plt.title(f"Dendrograma — método de Ward, municípios de MG ({ano})")
    plt.ylabel("Distância de fusão")
    plt.tight_layout()
    plt.savefig(FIG / f"dendrograma_{ano}.png", dpi=200)
    plt.close()

    # coeficientes de aglomeração das últimas fusões: aumentos percentuais
    # expressivos indicam a junção de grupos heterogêneos (ponto de parada)
    ultimas = Z[-10:, 2][::-1]  # da última fusão para trás
    coef = pd.DataFrame({
        "grupos_restantes": np.arange(1, len(ultimas) + 1),
        "coeficiente": ultimas,
    })
    coef["variacao_pct_vs_proxima"] = coef["coeficiente"].pct_change(-1) * 100
    coef.round(3).to_csv(TAB / f"coeficientes_aglomeracao_{ano}.csv", index=False)

    # ---------------- 3. silhueta média das soluções candidatas (Ward e K-means)
    diagnostico = []
    for k in K_CANDIDATOS:
        rotulos_w = fcluster(Z, t=k, criterion="maxclust")
        sil_ward = silhouette_score(X, rotulos_w)

        km = KMeans(
            n_clusters=k,
            init=centroides_ward(X, rotulos_w, k),
            n_init=1,
            random_state=SEMENTE,
        ).fit(X)
        sil_km = silhouette_score(X, km.labels_)

        diagnostico.append({"k": k, "silhueta_ward": sil_ward, "silhueta_kmeans": sil_km})

    diagnostico = pd.DataFrame(diagnostico)
    diagnostico.round(4).to_csv(TAB / f"silhueta_por_k_{ano}.csv", index=False)

    plt.figure(figsize=(7, 4))
    plt.plot(diagnostico["k"], diagnostico["silhueta_ward"], "o-", label="Ward (hierárquico)")
    plt.plot(diagnostico["k"], diagnostico["silhueta_kmeans"], "s-", label="K-means (refinado)")
    plt.xlabel("Quantidade de grupos (k)")
    plt.ylabel("Silhueta média")
    plt.title(f"Silhueta média das soluções candidatas ({ano})")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / f"silhueta_por_k_{ano}.png", dpi=200)
    plt.close()

    # -------------------- 4. solução adotada por padrão e refinamento final
    k_final = int(diagnostico.loc[diagnostico["silhueta_kmeans"].idxmax(), "k"])
    rotulos_w = fcluster(Z, t=k_final, criterion="maxclust")
    km = KMeans(
        n_clusters=k_final,
        init=centroides_ward(X, rotulos_w, k_final),
        n_init=1,
        random_state=SEMENTE,
    ).fit(X)

    resultado = matriz.copy()
    resultado["cluster"] = km.labels_ + 1
    (
        resultado.reset_index()[["Cod.IBGE", "Instituição", "cluster"]]
        .to_csv(TAB / f"clusters_{ano}.csv", index=False)
    )

    # ------------- 5. caracterização dos grupos (per capita médio por função)
    carac = resultado.groupby("cluster").mean()
    carac.loc["média geral"] = matriz.mean()
    carac["n_municipios"] = resultado.groupby("cluster").size().reindex(carac.index)
    carac.round(2).to_csv(TAB / f"caracterizacao_clusters_{ano}.csv")

    print(
        f"{ano}: {len(matriz)} municípios | k adotado por padrão = {k_final} "
        f"(maior silhueta pós-refinamento) | tamanhos: "
        f"{resultado['cluster'].value_counts().sort_index().tolist()}"
    )

print("\nDiagnósticos em outputs/tabelas e outputs/graficos.")
print("Revise dendrograma + coeficientes + silhueta antes de fixar o k do TCC.")
