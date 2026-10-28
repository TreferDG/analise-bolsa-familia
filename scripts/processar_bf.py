import os
import duckdb
import pandas as pd

PASTA = r"C:\Users\dguer\OneDrive\Documentos\Projetos Analista\Gov - Analise do IBGE e Bolsa Familia\dados"
ARQUIVO_BF = os.path.join(PASTA, "bf_202608.parquet")

def agregar_pagamentos_bolsa_familia() -> pd.DataFrame:
    """Lê o Parquet do Bolsa Família via DuckDB e agrega os pagamentos por município (SIAFI)."""
    print("=" * 60)
    print("3. Agregando pagamentos do Bolsa Família via DuckDB...")
    
    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE VIEW bf AS SELECT * FROM '{ARQUIVO_BF}';")
    
    query_agregada = """
        SELECT
          cod_siafi,
          uf,
          municipio,
          COUNT(DISTINCT nis) AS familias,
          ROUND(SUM(valor), 2) AS total_pago,
          ROUND(SUM(valor) FILTER (WHERE nis IS NOT NULL) / COUNT(DISTINCT nis), 2) AS valor_medio_familia
        FROM bf
        GROUP BY 1, 2, 3
        ORDER BY total_pago DESC;
    """
    df_municipio_bf = con.execute(query_agregada).df()
    con.close()
    
    print(f"-> Agregação concluída! Total de municípios nos pagamentos: {len(df_municipio_bf)}")
    return df_municipio_bf