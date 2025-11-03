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
        if any(freq > 0.9):
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


def resetar_config():
    """Restaura o arquivo heuristicas.config.json para o estado padrão."""
    estado_inicial = {
        "heuristicas": [],
        "arquivo_csv": None
    }
    with open("heuristicas.config.json", "w", encoding="utf-8") as f:
        json.dump(estado_inicial, f, indent=4, ensure_ascii=False)
    print("Arquivo 'heuristicas.config.json' foi resetado para o estado inicial.\n")


def main():
    # --- Lê arquivo de configuração ---
    try:
        with open("heuristicas.config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Arquivo 'heuristicas.config.json' não encontrado. Rode `node configurar-heuristicas.js` antes.")
        sys.exit(1)

    heuristicas_escolhidas = config.get("heuristicas", [])
    arquivo_csv = config.get("arquivo_csv", None)

    if not arquivo_csv:
        print("Nenhum arquivo CSV definido em heuristicas.config.json.")
        sys.exit(1)

    if not heuristicas_escolhidas:
        print("Nenhuma heurística configurada.")
        sys.exit(1)

    print(f"Arquivo selecionado: {arquivo_csv}")
    print(f"Heurísticas que serão aplicadas: {', '.join(heuristicas_escolhidas)}\n")

    # --- Lê o CSV ---
    try:
        df = pd.read_csv(arquivo_csv)
    except Exception as e:
        print(f"Erro ao abrir '{arquivo_csv}': {e}")
        sys.exit(1)

    # --- Executa as heurísticas ---
    total_verificacoes = len(heuristicas_escolhidas)
    erros = []

    for nome in heuristicas_escolhidas:
        func = HEURISTICAS.get(nome)
        if func:
            resultado = func(df)
            if resultado:
                erros.append((nome, resultado))

    # --- Calcula estatísticas ---
    percentual_erros = (len(erros) / total_verificacoes) * 100 if total_verificacoes else 0
    percentual_corretos = 100 - percentual_erros

    print(f"\nTotal de verificações: {total_verificacoes}")
    print(f"Lints detectados: {len(erros)}")
    print(f"Porcentagem de lints encontrados: {percentual_erros:.2f}%")
    print(f"Porcentagem de dados corretos: {percentual_corretos:.2f}%\n")

    # --- Exibe resultados ---
    if erros:
        print("Heurísticas (Lints) encontradas:")
        for categoria, erro in erros:
            print(f"  * [{categoria.upper()}] {erro}")
        print()

    # --- Resetar configuração antes de sair ---
    resetar_config()

    # --- Sair com código apropriado ---
    if erros:
        sys.exit(1)
    else:
        print("Nenhum erro identificado com as heurísticas aplicadas.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
