# Como baixar os dados do FINBRA (SICONFI)

1. Acesse https://siconfi.tesouro.gov.br
2. Menu **Consultas → Consultar FINBRA** (Finanças do Brasil).
3. Selecione:
   - **Declaração:** DCA — Declaração de Contas Anuais
   - **Exercício:** 2023 (repita depois para 2024 e 2025)
   - **Escopo:** Municípios — todos (o filtro de MG é feito nos scripts)
   - **Tabela/Anexo:** *Despesas por Função e Subfunção* (Anexo I-E da DCA; o nome exato pode variar na interface)
4. Baixe em **CSV** e salve nesta pasta como:
   - `finbra_despesas_funcao_2023.csv`
   - `finbra_despesas_funcao_2024.csv`
   - `finbra_despesas_funcao_2025.csv`

## Observações

- Os CSVs vêm em `latin-1`, separados por `;` e com decimal `,` — os scripts de tratamento já lidam com isso.
- Os arquivos do SICONFI trazem algumas linhas de título antes do cabeçalho da tabela. Abra o CSV e confira: o número de linhas a pular é o parâmetro `skiprows` (Python) / `skip` (R) nos scripts de tratamento.
- **2025:** a DCA do exercício é entregue pelos municípios ao longo de 2026; a cobertura pode estar incompleta dependendo da data do download.
- Para automação, o Tesouro também disponibiliza a **API do SICONFI** (Data Lake): https://apidatalake.tesouro.gov.br/docs
- A malha territorial municipal do IBGE é baixada automaticamente pelos scripts de mapas, via pacote `geobr` — não é preciso baixar shapefile manualmente.
