import csv
import os
import re
import unicodedata
import pandas as pd

# Constantes de caminhos
PASTA = r"C:\Users\dguer\OneDrive\Documentos\Projetos Analista\Gov - Analise do IBGE e Bolsa Familia\dados"
ARQUIVO_DOM = os.path.join(PASTA, "População e Domicílios.csv")
ARQUIVO_REN = os.path.join(PASTA, "Trabalho e Rendimento.csv")

def normalizar_chave(nome: str, uf: str) -> str:
    """Normaliza o nome do município e combina com a UF para criar uma chave única."""
    s = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode()
    return f"{uf}|{re.sub(r'[^A-Za-z]', '', s).upper()}"

def converter_para_numero(s: pd.Series) -> pd.Series:
    """Converte colunas de texto com formato brasileiro para numérico."""
    return pd.to_numeric(
        s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )

def ler_sidra(caminho: str) -> dict[str, pd.DataFrame]:
    """Lê arquivos CSV do SIDRA/IBGE estruturados em blocos por variável."""
    blocos, var_atual = {}, None
    with open(caminho, "r", encoding="utf-8", errors="replace", newline="") as f:
        for campos in csv.reader(f, delimiter=";"):
            if not campos:
                continue
            primeiro = campos[0].strip()
            if primeiro.startswith("Variável - "):
                var_atual = primeiro[len("Variável - ") :]
                blocos[var_atual] = []
                continue
            m = re.match(r"^(.*)\s\(([A-Z]{2})\)$", primeiro)
            if var_atual and m and len(campos) >= 2:
                blocos[var_atual].append((m.group(1), m.group(2), campos[-1].strip()))
                
    return {
        v: pd.DataFrame(l, columns=["municipio", "uf", "valor_txt"])
        for v, l in blocos.items()
    }

def extrair_variavel_sidra(blocos: dict, trecho: str) -> pd.DataFrame:
    """Extrai uma variável específica dos blocos SIDRA e converte os valores."""
    for var, df in blocos.items():
        if trecho in var:
            return df.assign(valor=converter_para_numero(df["valor_txt"]))[["municipio", "uf", "valor"]]
    raise ValueError(f"Variável contendo '{trecho}' não encontrada.")

def carregar_e_processar_ibge() -> pd.DataFrame:
    """Carrega as bases do SIDRA, extrai domicílios, moradores e renda, e retorna o DataFrame limpo."""
    print("=" * 60)
    print("1. Lendo dados do IBGE (SIDRA)...")
    dom = ler_sidra(ARQUIVO_DOM)
    ren = ler_sidra(ARQUIVO_REN)

    print("-> Consolidando dados demográficos do IBGE...")
    ibge = (
        extrair_variavel_sidra(dom, "(Domicílios)").rename(columns={"valor": "domicilios"})
        .merge(extrair_variavel_sidra(dom, "(Pessoas)").rename(columns={"valor": "moradores"}), on=["municipio", "uf"])
        .merge(extrair_variavel_sidra(ren, "nominal médio").rename(columns={"valor": "renda_media"}), on=["municipio", "uf"])
        .merge(extrair_variavel_sidra(ren, "nominal mediano").rename(columns={"valor": "renda_mediana"}), on=["municipio", "uf"])
    )
    ibge["chave"] = [normalizar_chave(n, u) for n, u in zip(ibge["municipio"], ibge["uf"])]
    return ibge

if __name__ == "__main__":
    df_ibge = carregar_e_processar_ibge()
    print(df_ibge.head())