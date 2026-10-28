from processar_ibge import carregar_e_processar_ibge
from processar_siafi import processar_siafi_e_cruzar
from processar_bf import agregar_pagamentos_bolsa_familia
from consolidar_final import consolidar_bases
import pandas as pd
import os

PASTA = r"C:\Users\dguer\OneDrive\Documentos\Projetos Analista\Gov - Analise do IBGE e Bolsa Familia\dados"
ARQUIVO_SIAFI = os.path.join(PASTA, "tabela_municipio_siafi.csv")

def main():
    # Passo 1: Lê e processa as bases do IBGE (SIDRA)
    ibge_df = carregar_e_processar_ibge()

    # Passo 2: Lê o SIAFI e resolve as divergências com o IBGE
    ibge_final = processar_siafi_e_cruzar(ibge_df)

    # Passo 3: Agrega o Bolsa Família via DuckDB
    bf_mun = agregar_pagamentos_bolsa_familia()

    # Carrega a tabela SIAFI pura necessária para o último passo
    siafi_df = pd.read_csv(
        ARQUIVO_SIAFI,
        sep=";",
        header=None,
        names=["cod_siafi", "cnpj", "nome", "uf", "cod_ibge"],
        dtype=str,
        encoding="latin-1",
    )

    # Passo 4: Consolida tudo, calcula métricas e salva os arquivos finais
    consolidar_bases(bf_mun, ibge_final, siafi_df)
    
    print("\n Pipeline executado do início ao fim com sucesso!")

if __name__ == "__main__":
    main()