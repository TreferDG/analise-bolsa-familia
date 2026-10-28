# Bolsa Família: para onde vai o dinheiro?

> 🚧 **Projeto em andamento.** Este README é atualizado conforme o trabalho avança. Veja o [diário de progresso](#diário-de-progresso) no final.

Análise de dados públicos do Bolsa Família por município e região do Brasil, cruzando os pagamentos do programa com dados demográficos e de renda do IBGE.

## Perguntas que o projeto quer responder

1. Qual a participação de cada município no total pago pelo programa e qual a cobertura (famílias beneficiárias por domicílio)?
2. Existe relação entre a renda por pessoa de um município e o valor médio recebido por família?
3. Quais municípios têm valor por pessoa ou por família muito acima da média nacional, e o que os dados sugerem sobre o motivo?
4. Como o valor pago e a cobertura se distribuem entre regiões e estados, e quão concentrado é o dinheiro entre os municípios?

## Fontes de dados

| Fonte | O que traz | Link |
|---|---|---|
| Portal da Transparência (CGU) | Pagamentos do Novo Bolsa Família, uma linha por beneficiário (agosto/2026) | https://portaldatransparencia.gov.br/download-de-dados |
| IBGE (SIDRA), tabela 9728 | Domicílios particulares permanentes ocupados e moradores por município (Censo 2022) | https://sidra.ibge.gov.br/tabela/9728 |
| IBGE (SIDRA), tabela 10295 | Rendimento domiciliar mensal per capita, médio e mediano, por município (Censo 2022) | https://sidra.ibge.gov.br/tabela/10295 |
| Portal Brasileiro de Dados Abertos | Tabela de correspondência entre código SIAFI e código IBGE dos municípios | https://dados.gov.br |

> Período analisado: agosto/2026 (um único mês)
>
> Os valores são nominais (sem correção pela inflação).

## Ferramentas

- **Python** (pandas) para leitura, tratamento leve e junção de tabelas de domínio.
- **DuckDB (SQL) e Parquet** para processar o arquivo massivo de pagamentos (cerca de 2 GB, 18,8 milhões de linhas) com alta performance sem sobrecarregar a memória RAM.
- **Power BI** (planejado) para os gráficos, mapas e o dashboard final.
- **Git e GitHub** para versionar e apresentar o projeto.

## Estrutura do projeto

```
bolsa-familia-ibge/
├── dados/                      # Arquivos brutos (CSVs, Parquets) e a base final municipio_final.parquet (ignorado no Git)
├── scripts/                    # Pipeline ETL modularizado
│   ├── processar_ibge.py       # Extração e normalização dos dados do SIDRA/IBGE
│   ├── processar_siafi.py      # Resolução de divergências SIAFI x IBGE via Fuzzy Matching
│   ├── processar_bf.py         # Agregação massiva de pagamentos do Bolsa Família via DuckDB
│   └── consolidar_final.py     # Cruzamento das bases, cálculo de métricas e exportação
├── main.py                     # Script orquestrador do pipeline de ponta a ponta
└── README.md
```

## Metodologia e decisões

**Conversão.** O CSV de pagamentos (separador `;`, codificação latin-1) foi convertido para Parquet. Na conversão, CPF e nome dos beneficiários foram descartados. Ficaram só o mês de competência, o mês de referência, a UF, o código e o nome do município, o NIS (usado apenas para contar famílias distintas) e o valor da parcela. Nenhum dado pessoal é publicado neste repositório, apenas totais agregados por município.

**Conferência dos dados (agosto/2026).**

| Verificação | Resultado |
|---|---|
| Linhas no arquivo | 18.809.420 |
| NIS distintos | 18.778.328 |
| Total pago | cerca de R$ 12,76 bilhões |
| Municípios | 5.571 (o Censo 2022 tem 5.570) |
| UFs | 27 |
| Valor da parcela | mínimo R$ 25, mediana R$ 650, média R$ 678,56, máximo R$ 4.040 |
| Linhas com valor acima de R$ 2.000 | 4.937 (cerca de 0,03%) |

**Decisões tomadas e Arquitetura ETL.**

- **Mês de referência.** 99,84% das linhas se referem a agosto. Os 0,16% restantes (referência de janeiro a julho) foram mantidos.
- **Contagem de famílias.** Usa `COUNT(DISTINCT nis)`. Cerca de 12 mil NIS (0,06%) aparecem em mais de uma linha.
- **Linhas sem NIS.** São 321 linhas (R$ 231.729). Entram no total pago, mas ficam fora da contagem de famílias.
- **Valores altos.** Foram mantidos. São raros e não há indício de erro.
- **Valor médio por família.** Calculado como total pago às famílias dividido pelo número de famílias distintas, e não como média das linhas.
- **Cruzamento SIAFI × IBGE (Automatizado):** A tabela do SIAFI possui 5.589 linhas, sendo 19 marcadores descartados (`0000000`). Para ligar os municípios do SIAFI aos do IBGE, implementou-se uma rotina de *Fuzzy Matching* (`difflib.SequenceMatcher`) no script `02_processar_siafi.py`. Isso permitiu resolver de forma automatizada e precisa as divergências de grafia dos 32 municípios problemáticos (ex: Paraty/Parati, Assú/Açu).
- **Mapeamento do Município Novo:** O município de Boa Esperança do Norte (MT) foi isolado no cruzamento com a base demográfica por ser um município recém-criado sem contagem oficial separada no Censo 2022.
- **Métricas Consolidadas:** O pipeline calcula e gera diretamente na tabela final as métricas de `regiao` (macro-regiões do Brasil), `pct_do_total` (participação percentual no bolo nacional), `cobertura_pct` (razão famílias/domicílios) e `valor_por_habitante` (repasse per capita).

## Principais achados (preliminares)

- As 10 cidades que mais recebem concentram cerca de **13,3%** de todo o dinheiro pago no mês. São as maiores cidades do país, com São Paulo no topo (3,29%). Isso reflete o tamanho da população, e a comparação justa depende da cobertura e do valor por habitante.
- O valor médio por família nessas 10 cidades é parecido, entre R$ 647 e R$ 698.
- A base final consolidada (`municipio_final.parquet`) foi gerada com sucesso contendo todos os 5.570 municípios do Censo 2022 com 100% dos códigos mapeados e com todas as métricas calculadas, pronta para consumo no Power BI.

## Limitações

- Análise de um único mês (agosto/2026): não mostra evolução ao longo do tempo.
- Os arquivos de pagamento não trazem o número de pessoas por família, a renda nem o tipo de benefício. A cobertura é calculada como famílias beneficiárias por domicílio, e não como porcentagem de pessoas.
- Não é possível testar diretamente se valores altos vêm de famílias maiores ou de adicionais do programa.
- Os dados do Censo são de 2022 e os pagamentos são de 2026, então a cobertura e o valor por habitante são aproximações.
- "Família" do programa não equivale a "domicílio" do IBGE. A razão entre os dois pode passar de 100% em algumas cidades sem que isso indique erro.
- **Boa Esperança do Norte (MT)** aparece nos pagamentos (116 famílias, R$ 78.936) mas não no Censo 2022, porque o município foi instalado em 2025. A população dele está contada em Sorriso e Nova Ubiratã, que ficam com a cobertura ligeiramente subestimada.
- A renda domiciliar per capita do IBGE exclui pensionistas, empregados domésticos e parentes de empregados domésticos que moram no domicílio. É uma estimativa de amostra, menos precisa em municípios muito pequenos, e já inclui benefícios de programas sociais. Por isso a pergunta 2 compara os dois valores sem tratar um como causa do outro.
- Municípios com poucas famílias têm médias instáveis e serão filtrados na pergunta 3.
- Os valores são nominais.

## Diário de progresso

- [x] Definir perguntas de pesquisa
- [x] Baixar dados do Portal da Transparência (agosto/2026)
- [x] Baixar dados do IBGE (domicílios, moradores e renda)
- [x] Converter o CSV de pagamentos para Parquet e conferir os números
- [x] Limpeza e padronização (cruzamento SIAFI × IBGE com Fuzzy Matching)
- [x] Arquitetura de pipeline ETL modularizada (`scripts/` e `main.py`)
- [x] Consolidação final e geração do arquivo `municipio_final.parquet` com métricas calculadas
- [ ] Análise exploratória
- [ ] Dashboard no Power BI
- [ ] Conclusões e revisão final do README

| Data | O que foi feito |
|---|---|
| 22/10/2026 | Definição das perguntas e criação do repositório |
| 26/10/2026 | Ajuste da pergunta 4 e escolha do recorte (agosto/2026). Download do CSV de pagamentos (2 GB), conversão para Parquet e conferência: linhas, NIS, valores, mês de referência. Projeto tirado do OneDrive |
| 27/10/2026 | Conferência de famílias repetidas, linhas sem NIS e município a mais. Primeira tabela por município (famílias, total pago, valor médio por família, participação no total). Download dos dados do IBGE (tabelas 9728 e 10295) e da tabela SIAFI → IBGE. Diagnóstico do cruzamento: 32 nomes de município conferidos à mão e identificação de Boa Esperança do Norte como município novo |
| 28/10/2026 | Estruturação e execução do pipeline ETL em 4 módulos (`01_processar_ibge.py`, `02_processar_siafi.py`, `03_processar_bf.py`, `04_consolidar_final.py`) com orquestrador `main.py`. Resolução automatizada das divergências do SIAFI com Fuzzy Matching (`difflib`). Processamento massivo dos pagamentos com DuckDB e exportação da base consolidada final `municipio_final.parquet`. |