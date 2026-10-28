import os
import difflib
import pandas as pd
from processar_ibge import normalizar_chave

PASTA = r"C:\Users\dguer\OneDrive\Documentos\Projetos Analista\Gov - Analise do IBGE e Bolsa Familia\dados"
ARQUIVO_SIAFI = os.path.join(PASTA, "tabela_municipio_siafi.csv")

def processar_siafi_e_cruzar(ibge_df: pd.DataFrame) -> pd.DataFrame:
    """Lê o SIAFI, trata os dados e resolve as divergências de grafia com o IBGE."""
    print("=" * 60)
    print("2. Lendo e tratando a tabela SIAFI...")
    
    siafi = pd.read_csv(
        ARQUIVO_SIAFI,
        sep=";",
        header=None,
        names=["cod_siafi", "cnpj", "nome", "uf", "cod_ibge"],
        dtype=str,
        encoding="latin-1",
    )
    siafi["nome"] = siafi["nome"].str.strip()
    siafi["chave"] = [normalizar_chave(n, u) for n, u in zip(siafi["nome"], siafi["uf"])]

    print("-> Tratando divergências de nomes (Fuzzy Matching)...")
    siafi_real = siafi[siafi["cod_ibge"] != "0000000"].copy()
    ibge_m = ibge_df.merge(siafi_real[["chave", "cod_siafi", "cod_ibge"]], on="chave", how="left")

    ibge_sem = ibge_m[ibge_m["cod_ibge"].isna()]
    siafi_sobra = siafi_real[~siafi_real["chave"].isin(ibge_df["chave"])]

    cand = []
    for i, r in ibge_sem.iterrows():
        for j, s in siafi_sobra[siafi_sobra["uf"] == r["uf"]].iterrows():
            sim = difflib.SequenceMatcher(None, r["chave"].split("|")[1], s["chave"].split("|")[1]).ratio()
            cand.append((sim, i, j))
    cand.sort(reverse=True)

    usado_i, usado_j, pares = set(), set(), []
    for sim, i, j in cand:
        if i in usado_i or j in usado_j:
            continue
        usado_i.add(i)
        usado_j.add(j)
        pares.append((ibge_sem.loc[i, "municipio"], siafi_sobra.loc[j, "nome"], ibge_sem.loc[i, "uf"], round(sim, 2), siafi_sobra.loc[j, "cod_siafi"], siafi_sobra.loc[j, "cod_ibge"]))

    pares_df = pd.DataFrame(pares, columns=["nome_ibge", "nome_siafi", "uf", "semelhanca", "cod_siafi", "cod_ibge"])

    corr = pares_df.set_index(["nome_ibge", "uf"])["cod_ibge"].to_dict()
    ibge_final = ibge_m.copy()
    falta = ibge_final["cod_ibge"].isna()
    ibge_final.loc[falta, "cod_ibge"] = [
        corr[(n, u)] for n, u in zip(ibge_final.loc[falta, "municipio"], ibge_final.loc[falta, "uf"])
    ]
    
    assert ibge_final["cod_ibge"].notna().all() and ibge_final["cod_ibge"].is_unique
    print("-> Cruzamento de nomes concluído com sucesso!")
    return ibge_final