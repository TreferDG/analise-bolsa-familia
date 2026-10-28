import os
import duckdb
import pandas as pd

PASTA = r"C:\Users\dguer\OneDrive\Documentos\Projetos Analista\Gov - Analise do IBGE e Bolsa Familia\dados"

REGIOES = {
    **dict.fromkeys(["AC", "AM", "AP", "PA", "RO", "RR", "TO"], "Norte"),
    **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Nordeste"),
    **dict.fromkeys(["DF", "GO", "MS", "MT"], "Centro-Oeste"),
    **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Sudeste"),
    **dict.fromkeys(["PR", "RS", "SC"], "Sul"),
}

def consolidar_bases(df_bf_mun: pd.DataFrame, df_ibge: pd.DataFrame, df_siafi: pd.DataFrame) -> pd.DataFrame:
    """Faz a união final das bases, calcula as métricas e exporta o Parquet e CSV."""
    print("=" * 60)
    print("4. Consolidando bases finais e calculando métricas...")

    siafi_real = df_siafi[df_siafi["cod_ibge"] != "0000000"].copy()

    final = (
        df_bf_mun.merge(siafi_real[["cod_siafi", "cod_ibge"]], on="cod_siafi", how="left")
              .merge(df_ibge[["cod_ibge", "domicilios", "moradores", "renda_media", "renda_mediana"]], on="cod_ibge", how="left")
    )

    final["regiao"] = final["uf"].map(REGIOES)
    final["pct_do_total"] = (100 * final["total_pago"] / final["total_pago"].sum()).round(4)
    final["cobertura_pct"] = (100 * final["familias"] / final["domicilios"]).round(2)
    final["valor_por_habitante"] = (final["total_pago"] / final["moradores"]).round(2)

    caminho_parquet = os.path.join(PASTA, "municipio_final.parquet")
    caminho_csv = os.path.join(PASTA, "municipio_final.csv")

    con = duckdb.connect()
    con.register("df_final", final)
    con.execute(f"COPY df_final TO '{caminho_parquet}' (FORMAT PARQUET)")
    con.close()

    final.to_csv(caminho_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    print("-> Pipeline concluído com sucesso! Arquivos salvos na pasta dados.")
    return final