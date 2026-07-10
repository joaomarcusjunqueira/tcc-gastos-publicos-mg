# Alocação de recursos públicos nos municípios mineiros: uma análise por função de governo

![Status](https://img.shields.io/badge/status-em%20andamento-D97706)
![Python](https://img.shields.io/badge/Python-pandas%20·%20SciPy%20·%20scikit--learn-3776AB)
![Método](https://img.shields.io/badge/clusters-Ward%20%2B%20K--means-6A3FB5)
![Dados](https://img.shields.io/badge/dados-FINBRA%2FSiconfi%20·%20IBGE-0C7C46)

Trabalho de Conclusão de Curso (Administração Pública — Universidade Federal de Lavras/UFLA): pesquisa **descritiva e quantitativa** sobre como os **853 municípios de Minas Gerais** distribuem seus recursos entre as **funções de governo**, nos exercícios de **2023, 2024 e 2025** (analisados separadamente), com identificação de **perfis de alocação** por análise de agrupamentos (clusters).

**Autor:** João Marcus Junqueira · [GitHub](https://github.com/joaomarcusjunqueira) · [LinkedIn](https://www.linkedin.com/in/joaomarcusjunqueira) · [Portfólio](https://joaomarcusjunqueira.github.io) · joaomarcus2012@gmail.com

---

## Pergunta e objetivos

**Pergunta de partida:** como se caracterizam os gastos públicos conforme sua finalidade nos municípios mineiros?

**Objetivo geral:** avaliar a caracterização dos gastos públicos conforme sua finalidade nos municípios mineiros.

**Objetivos específicos:** (a) descrever a caracterização dos gastos públicos conforme sua finalidade; (b) avaliar o agrupamento dos municípios mineiros por meio da classificação funcional do gasto público.

A fundamentação teórica articula federalismo fiscal (Oates), teoria dos bens públicos (Samuelson) e a função alocativa do orçamento (Musgrave & Musgrave): a composição do gasto — e não apenas seu volume — expressa as prioridades efetivas da ação estatal no nível local.

## Dados

| Fonte | Uso |
|---|---|
| **FINBRA / Siconfi** (Tesouro Nacional) — tabela *Despesas por Função* (Anexo I-E da DCA) | Despesa **liquidada** por função e subfunção e **população municipal**, para os 853 municípios de MG, exercícios de 2023, 2024 e 2025 |
| **IBGE — malha municipal digital** (GeoJSON, codificação IBGE) | Representação cartográfica dos resultados |

- Classificação funcional conforme a **Portaria n. 42/1999**, atualizada pela **Portaria SOF/ME n. 2.520/2022**.
- Estágio da despesa: **liquidada** (art. 63 da Lei n. 4.320/1964) — despesa efetivamente incorrida, preferível à empenhada (que antecipa) e à paga (que depende do fluxo de caixa).
- **Indicador central: despesa liquidada per capita por função** — expressa o esforço de gasto por habitante e torna comparáveis municípios de portes distintos.
- Coleta realizada em **junho de 2026** no portal do Siconfi. Passo a passo para reprodução: [`data/raw/COMO_BAIXAR.md`](data/raw/COMO_BAIXAR.md).

## Metodologia

1. **Tratamento** — leitura padronizada dos CSVs (latin-1, `;`, decimal `,`), filtro dos municípios de MG, exclusão das linhas totalizadoras, separação função × subfunção e cálculo da despesa per capita.
2. **Estatística descritiva** — média, mediana, desvio padrão, variância, coeficiente de variação e valores mínimo e máximo da despesa per capita, por função e exercício.
3. **Análise de agrupamentos** (conduzida separadamente para cada exercício):
   - padronização das variáveis em **escores z**;
   - etapa hierárquica pelo **método de Ward** (distância euclidiana quadrática);
   - quantidade de grupos identificada por **dendrograma**, **coeficientes de aglomeração** e **silhueta média** (Rousseeuw, 1987), considerando também a interpretabilidade dos grupos;
   - refinamento pelo algoritmo **K-means**, inicializado nos centroides da solução de Ward;
   - caracterização de cada grupo pelas despesas per capita médias das funções, em comparação com as médias do conjunto.
4. **Análise complementar no nível subfuncional** — mesmo procedimento aplicado à matriz de subfunções, para verificar se revela padrões distintos dos funcionais.
5. **Mapas** — representação cartográfica dos resultados sobre a malha municipal do IBGE.

Execução em **Python** (pandas, NumPy, SciPy, scikit-learn), conforme definido no projeto. Os scripts em R do repositório são apoio complementar para tratamento e mapas.

## Estrutura do repositório

```
tcc-gastos-publicos-mg/
├── data/
│   ├── raw/          # CSVs do FINBRA (não versionados — ver COMO_BAIXAR.md)
│   └── processed/    # bases tratadas geradas pelos scripts
├── python/
│   ├── 01_tratamento_finbra.py   # limpeza, filtro MG, função × subfunção, per capita
│   ├── 02_descritivas.py         # medidas descritivas e composição do gasto
│   ├── 03_mapas.py               # mapas coropléticos (malha IBGE via geobr)
│   └── 04_clusters.py            # Ward + K-means, diagnósticos de k e caracterização
├── r/                            # apoio complementar (tratamento e mapas)
├── outputs/
│   ├── tabelas/  ├── graficos/  └── mapas/
├── requirements.txt
└── README.md
```

## Como reproduzir

```bash
pip install -r requirements.txt
python python/01_tratamento_finbra.py   # requer os CSVs em data/raw/
python python/02_descritivas.py
python python/04_clusters.py
python python/03_mapas.py
```

## Resultados

🚧 Em construção — dendrogramas, diagnósticos de silhueta, caracterização dos perfis e mapas serão publicados aqui conforme a análise avança.

<!-- Exemplos (descomentar quando as figuras forem geradas):
![Dendrograma — método de Ward (2024)](outputs/graficos/dendrograma_2024.png)
![Composição da despesa por função — MG 2024](outputs/graficos/composicao_funcao_2024.png)
![Saúde: despesa liquidada per capita — municípios de MG, 2024](outputs/mapas/mapa_saude_per_capita_2024.png)
-->

## Status

- [x] Projeto de pesquisa (introdução, referencial teórico e metodologia)
- [x] Coleta dos dados no Siconfi (jun/2026)
- [ ] Tratamento e validação das bases (2023–2025)
- [ ] Estatísticas descritivas por função e exercício
- [ ] Análise de clusters (Ward + K-means) por exercício
- [ ] Análise complementar no nível subfuncional
- [ ] Mapas e caracterização dos perfis de alocação
- [ ] Redação final e defesa

## Licença

Código sob licença MIT. Os dados utilizados são públicos, disponibilizados pelo Tesouro Nacional (Siconfi/FINBRA) e pelo IBGE.
