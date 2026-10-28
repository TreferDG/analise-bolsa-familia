import duckdb

SAIDA = r"C:\Users\dguer\OneDrive\Documentos\Projetos Analista\Gov - Analise do IBGE e Bolsa Familia\dados\bf_202608.parquet"

duckdb.sql(f"CREATE OR REPLACE VIEW bf AS SELECT * FROM '{SAIDA}'")

# 1) Linhas e dinheiro por mês de referência
duckdb.sql(f"""
SELECT mes_referencia,
       COUNT(*) AS linhas,
       ROUND(SUM(valor)/1e6, 2) AS total_milhoes
FROM bf
GROUP BY 1 ORDER BY 1 
""").show()


# 2) Quantas vezes cada NIS aparece
duckdb.sql(f"""
SELECT n_linhas, COUNT(*) AS qtd_nis
FROM (SELECT nis, COUNT(*) AS n_linhas FROM bf GROUP BY nis)
GROUP BY 1
ORDER BY 1 
""").show()

# 3) Distribuição dos valores
duckdb.sql(f"""
SELECT 
  quantile_cont(valor, 0.01)  AS p01,
  quantile_cont(valor, 0.25)  AS p25,
  quantile_cont(valor, 0.50)  AS mediana,
  quantile_cont(valor, 0.75)  AS p75,
  quantile_cont(valor, 0.99)  AS p99,
  quantile_cont(valor, 0.999) AS p999,
  COUNT(*) FILTER (WHERE valor > 2000) AS linhas_acima_2000
FROM bf
""").show()

# 4) Municípios com menos linhas (para achar o código "a mais")
duckdb.sql("""
SELECT cod_siafi, municipio, uf, COUNT(*) AS linhas
FROM bf
GROUP BY 1, 2, 3
ORDER BY linhas ASC
LIMIT 10
""").show()

# 5) Linhas sem NIS
duckdb.sql("""
SELECT nis IS NULL AS nis_vazio,
       COUNT(*) AS linhas,
       ROUND(SUM(valor), 2) AS total_reais
FROM bf
GROUP BY 1
""").show()

# 6) Cidades (mesma UF e nome) com mais de um código
duckdb.sql("""
SELECT uf, municipio, COUNT(DISTINCT cod_siafi) AS codigos, COUNT(*) AS linhas
FROM bf
GROUP BY 1, 2
HAVING COUNT(DISTINCT cod_siafi) > 1
""").show()

# 7) Códigos com mais de um nome
duckdb.sql("""
SELECT cod_siafi, COUNT(DISTINCT municipio) AS nomes, COUNT(*) AS linhas
FROM bf
GROUP BY 1
HAVING COUNT(DISTINCT municipio) > 1
""").show()

duckdb.sql("""
CREATE OR REPLACE TABLE municipio_bf AS
SELECT
  cod_siafi,
  uf,
  municipio,
  COUNT(DISTINCT nis)  AS familias,
  ROUND(SUM(valor), 2) AS total_pago,
  ROUND(SUM(valor) FILTER (WHERE nis IS NOT NULL) / COUNT(DISTINCT nis), 2) AS valor_medio_familia,
  ROUND(100.0 * SUM(valor) / SUM(SUM(valor)) OVER (), 4) AS pct_do_total
FROM bf
GROUP BY 1, 2, 3
""")

duckdb.sql("SELECT COUNT(*) AS municipios FROM municipio_bf").show()

duckdb.sql("""
SELECT municipio, uf, familias, total_pago, valor_medio_familia, pct_do_total
FROM municipio_bf
ORDER BY total_pago DESC
LIMIT 10
""").show()
