# 01_tratamento_finbra.R
# Lê os CSVs do FINBRA "Despesas por Função e Subfunção" (DCA), padroniza e
# filtra os municípios de Minas Gerais.
# Espelho do script Python — use a linguagem que preferir; as saídas são as mesmas.
#
# Antes de rodar: baixe os dados conforme data/raw/COMO_BAIXAR.md

library(tidyverse)

# ------------------------------------------------------------------ parâmetros
anos <- c(2023, 2024, 2025)
uf_alvo <- "MG"
# Estágio da despesa (escolha metodológica — documente no TCC):
# "Despesas Empenhadas" | "Despesas Liquidadas" | "Despesas Pagas"
coluna_despesa <- "Despesas Liquidadas"

ler_finbra <- function(ano) {
  arquivo <- file.path("data/raw", paste0("finbra_despesas_funcao_", ano, ".csv"))
  if (!file.exists(arquivo)) {
    message("[aviso] ", arquivo, " não encontrado — pulando ", ano, ".")
    return(NULL)
  }
  # padrão brasileiro: latin-1, separador ';', decimal ','
  read_csv2(
    arquivo,
    skip = 3, # linhas de título antes do cabeçalho — confira no seu arquivo
    locale = locale(encoding = "latin1", decimal_mark = ",", grouping_mark = "."),
    show_col_types = FALSE
  ) |>
    rename_with(str_trim) |>
    mutate(ano = ano)
}

classificar_conta <- function(conta) {
  # padrões usuais no FINBRA (confirme no seu arquivo e ajuste as regex):
  #   função    -> "10 - Saúde"
  #   subfunção -> "10.301 - Atenção Básica"
  case_when(
    str_detect(conta, "^\\d{2} - ")          ~ "funcao",
    str_detect(conta, "^\\d{2}\\.\\d{3} - ") ~ "subfuncao",
    .default = "agregado"
  )
}

dados <- map(anos, ler_finbra) |>
  compact() |>
  bind_rows() |>
  filter(UF == uf_alvo, Coluna == coluna_despesa) |>
  mutate(
    nivel = classificar_conta(Conta),
    `População` = na_if(`População`, 0),
    per_capita = Valor / `População`
  )

dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)

colunas <- c("ano", "Instituição", "Cod.IBGE", "População", "Conta", "Valor", "per_capita")

dados |>
  filter(nivel == "funcao") |>
  select(all_of(colunas)) |>
  write_csv("data/processed/gastos_funcao_mg.csv")

dados |>
  filter(nivel == "subfuncao") |>
  select(all_of(colunas)) |>
  write_csv("data/processed/gastos_subfuncao_mg.csv")

message("Cobertura do FINBRA — municípios de MG por exercício:")
dados |>
  group_by(ano) |>
  summarise(municipios = n_distinct(`Cod.IBGE`)) |>
  print()
