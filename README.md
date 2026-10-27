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
| Portal da Transparência (CGU) | Pagamentos do Bolsa Família por município e mês | https://portaldatransparencia.gov.br/download-de-dados |
| IBGE (SIDRA) | População, domicílios e renda por município (Censo 2022) | https://sidra.ibge.gov.br |

> Período analisado: agosto/2026 (um único mês)
>
> Os valores são nominais (sem correção pela inflação).

## Ferramentas

_A preencher conforme o projeto avança (ex.: Python, pandas, DuckDB, Plotly, Streamlit)._

## Estrutura do projeto

```
bolsa-familia/
├── dados/         # arquivos originais baixados (não vão para o GitHub)
├── notebooks/     # análises e exploração
└── README.md
```

## Como reproduzir

_A preencher quando o projeto estiver mais completo._

## Principais achados

_Ainda não há resultados. Esta seção será preenchida ao final de cada etapa da análise._

## Limitações

- Análise de um único mês (agosto/2026): não mostra evolução ao longo do tempo.
- Os arquivos de pagamento não trazem o número de pessoas por família, a renda nem o tipo de benefício. A cobertura é calculada como famílias beneficiárias por domicílio, e não como porcentagem de pessoas.
- Não é possível testar diretamente se valores altos vêm de famílias maiores ou de adicionais do programa.
- O código de município do Portal da Transparência é o do SIAFI, não o do IBGE. O cruzamento com o Censo usa uma tabela de correspondência e pode deixar municípios sem par.
- Os valores são nominais.

_Seção a ser completada durante a análise._

## Diário de progresso

- [x] Definir perguntas de pesquisa
- [ ] Baixar dados do Portal da Transparência (agosto/2026)
- [ ] Baixar dados do IBGE
- [ ] Limpeza e padronização
- [ ] Análise exploratória
- [ ] Mapas e gráficos
- [ ] Dashboard
- [ ] Conclusões e revisão do README

| Data | O que foi feito |
|---|---|
| 22/10/2026 | Definição das perguntas e criação do repositório |
| 26/10/2026 | Ajuste da pergunta 4 e escolha do recorte: agosto/2026 |