# 00_pacotes.R
# Instala as dependências do projeto (rodar uma única vez).

pacotes <- c("tidyverse", "sf", "geobr")

novos <- pacotes[!pacotes %in% rownames(installed.packages())]
if (length(novos) > 0) install.packages(novos)

invisible(lapply(pacotes, library, character.only = TRUE))
message("Pacotes carregados: ", paste(pacotes, collapse = ", "))
