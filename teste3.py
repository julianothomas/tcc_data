import sys
import json
import pandas as pd

# --- Heurísticas implementadas ---
def colunas_sem_nome(df):
    return [col for col in df.columns if "Unnamed" in col]

def colunas_vazias(df):
    return [col for col in df.columns if df[col].isnull().all()]

def linhas_duplicadas(df):
    return df[df.duplicated()].index.tolist()

def desequilibrio_categorias(df):
    problemas = {}
    for col in df.select_dtypes(include=["object", "category"]):
        freq = df[col].value_counts(normalize=True)
        if any(freq > 0.9):  # Exemplo: uma categoria domina mais de 90%
            problemas[col] = freq.to_dict()
    return problemas

def miscoding_numerico(df):
    problemas = {}
    for col in df.select_dtypes(include=["object"]):
        try:
            pd.to_numeric(df[col])
        except ValueError:
            problemas[col] = "valores não numéricos detectados"
    return problemas

def miscoding_caps(df):
    problemas = {}
    for col in df.select_dtypes(include=["object"]):
        valores = df[col].dropna().unique()
        for v in valores:
            if str(v).lower() in [str(x).lower() for x in valores] and v not in ["", None]:
                if any(str(v) != str(x) for x in valores):
                    problemas[col] = "valores inconsistentes em maiúsculas/minúsculas"
    return problemas

def outliers(df):
    problemas = {}
    for col in df.select_dtypes(include=["number"]):
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        limites = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
        outliers = df[(df[col] < limites[0]) | (df[col] > limites[1])][col]
        if not outliers.empty:
            problemas[col] = outliers.tolist()
    return problemas

# --- Mapeamento de heurísticas ---
HEURISTICAS = {
    "colunas_sem_nome": colunas_sem_nome,
    "colunas_vazias": colunas_vazias,
    "linhas_duplicadas": linhas_duplicadas,
    "desequilibrio_categorias": desequilibrio_categorias,
    "miscoding_numerico": miscoding_numerico,
    "miscoding_caps": miscoding_caps,
    "outliers": outliers,
}

def main():
    # Arquivos CSV do stage (recebidos do pre-commit ou linha de comando)
    arquivos_csv = sys.argv[1:]
    if not arquivos_csv:
        print("⚠ Nenhum arquivo CSV informado.")
        sys.exit(0)

    # Carregar heurísticas escolhidas no JSON
    try:
        with open("heuristicas.config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            heuristicas_escolhidas = config.get("heuristicas", [])
    except FileNotFoundError:
        print("⚠ Arquivo 'heuristicas.config.json' não encontrado. Rode `node configurar-heuristicas.js` antes.")
        sys.exit(1)

    if not heuristicas_escolhidas:
        print("⚠ Nenhuma heurística configurada. Rode `node configurar-heuristicas.js` para definir.")
        sys.exit(1)

    print(f"🔍 Rodando heurísticas: {', '.join(heuristicas_escolhidas)}\n")

    erro_detectado = False

    for arquivo in arquivos_csv:
        print(f"📂 Verificando: {arquivo}")
        try:
            df = pd.read_csv(arquivo)
        except Exception as e:
            print(f"  ❌ Erro ao abrir {arquivo}: {e}")
            erro_detectado = True
            continue

        for nome in heuristicas_escolhidas:
            func = HEURISTICAS.get(nome)
            if func:
                resultado = func(df)
                if resultado:
                    print(f"  ⚠ Problema detectado em '{nome}': {resultado}")
                    erro_detectado = True

    if erro_detectado:
        sys.exit(1)  # Bloqueia o commit
    else:
        print("✅ Nenhum problema encontrado nos CSVs.")
        sys.exit(0)


if __name__ == "__main__":
    main()
