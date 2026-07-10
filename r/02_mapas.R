# 02_mapas.R
# Mapas coropléticos da despesa per capita por função (ggplot2 + sf + geobr).
# A malha municipal do IBGE é baixada automaticamente pelo geobr
# (requer internet no primeiro uso).
#
# Requer: rodar antes o 01_tratamento_finbra.R (ou o equivalente em Python)

library(tidyverse)
library(sf)
library(geobr)

funcao_alvo <- "10 - Saúde" # ajuste conforme o TCC
ano_alvo <- 2024

# malha territorial municipal do IBGE (ano de referência da malha: 2022)
malha <- read_municipality(code_muni = "MG", year = 2022)

dados <- read_csv("data/processed/gastos_funcao_mg.csv", show_col_types = FALSE)

base <- malha |>
  left_join(
    dados |> filter(Conta == funcao_alvo, ano == ano_alvo),
    by = c("code_muni" = "Cod.IBGE")
  )

grafico <- ggplot(base) +
  geom_sf(aes(fill = per_capita), color = NA) +
  scale_fill_viridis_c(name = "R$ per capita", na.value = "grey85") +
  labs(
    title = paste0(funcao_alvo, " — despesa liquidada per capita (", ano_alvo, ")"),
    subtitle = "Municípios de Minas Gerais · cinza: DCA não entregue",
    caption = "Fontes: FINBRA/SICONFI (Tesouro Nacional) e malha territorial do IBGE (geobr)"
  ) +
  theme_void(base_size = 12)

dir.create("outputs/mapas", showWarnings = FALSE, recursive = TRUE)
arquivo <- paste0(
  "outputs/mapas/mapa_",
  str_to_lower(str_replace_all(str_extract(funcao_alvo, "(?<= - ).*"), " ", "_")),
  "_per_capita_", ano_alvo, "_R.png"
)
ggsave(arquivo, grafico, width = 8, height = 8, dpi = 200)
message("OK -> ", arquivo)

# Dica: para gerar todos os anos e funções de uma vez, envolva o bloco acima
# em purrr::walk2() / um loop sobre expand_grid(funcao, ano).
