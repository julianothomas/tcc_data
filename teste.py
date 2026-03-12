import sys
import json
import pandas as pd
import os
import time

# --- Heurísticas implementadas ---
def colunas_sem_nome(df):
    """Detecta colunas sem nome."""
    return [{"coluna": col} for col in df.columns if "Unnamed" in col]


def colunas_vazias(df):
    """Detecta colunas totalmente vazias."""
    return [{"coluna": col} for col in df.columns if df[col].isnull().all()]


def linhas_duplicadas(df):
    """Detecta linhas duplicadas e retorna os índices."""
    duplicadas = df[df.duplicated()]
    return [{"linha": i + 2} for i in duplicadas.index.tolist()]  # +2 para compensar cabeçalho


def desequilibrio_categorias(df):
    """Verifica colunas categóricas com valores dominantes (>90%)."""
    problemas = []
    for col in df.select_dtypes(include=["object", "category"]):
        freq = df[col].value_counts(normalize=True)
        if any(freq > 0.9):
            maior = freq.idxmax()
            problemas.append({
                "coluna": col,
                "valor_dominante": str(maior),
                "frequencia": f"{freq.max()*100:.1f}%"
            })
    return problemas


def miscoding_numerico(df):
    """Detecta colunas textuais que deveriam ser numéricas."""
    problemas = []
    for col in df.select_dtypes(include=["object"]):
        for i, v in df[col].dropna().items():
            try:
                float(v)
            except ValueError:
                problemas.append({
                    "coluna": col,
                    "linha": i + 2,  # Compensa o cabeçalho
                    "valor": str(v)
                })
    return problemas


def miscoding_caps(df):
    """Detecta inconsistência de maiúsculas/minúsculas em colunas categóricas."""
    problemas = []
    for col in df.select_dtypes(include=["object"]):
        valores = df[col].dropna().unique()
        lower_map = {}
        for v in valores:
            vlower = str(v).lower()
            if vlower not in lower_map:
                lower_map[vlower] = [v]
            else:
                lower_map[vlower].append(v)
        for base, variantes in lower_map.items():
            if len(set(variantes)) > 1:
                for i, valor in df[col].items():
                    if valor in variantes:
                        problemas.append({
                            "coluna": col,
                            "linha": i + 2,
                            "valor": valor
                        })
    return problemas


def outliers(df):
    """Detecta valores outliers em colunas numéricas (método IQR)."""
    problemas = []
    for col in df.select_dtypes(include=["number"]):
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        limite_inf = q1 - 1.5 * iqr
        limite_sup = q3 + 1.5 * iqr
        outliers_idx = df[(df[col] < limite_inf) | (df[col] > limite_sup)].index
        for i in outliers_idx:
            problemas.append({
                "coluna": col,
                "linha": i + 2,
                "valor": df.loc[i, col]
            })
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

# --- Reset das configurações heuristicas.config.json ---
def resetar_config():
    estado_inicial = {"heuristicas": [], "arquivo_csv": None}
    with open("heuristicas.config.json", "w", encoding="utf-8") as f:
        json.dump(estado_inicial, f, indent=4, ensure_ascii=False)
    print("Arquivo 'heuristicas.config.json' foi resetado para o estado inicial.\n")


def main():
    
    inicio = time.time()
    
    # --- Lê arquivo de configuração ---
    try:
        with open("heuristicas.config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Arquivo 'heuristicas.config.json' não encontrado. Rode `node configurar-heuristicas.js` antes.")
        sys.exit(1)

    heuristicas_escolhidas = config.get("heuristicas", [])
    arquivo_csv = config.get("arquivo_csv", None)

    if not arquivo_csv or not os.path.exists(arquivo_csv):
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
        for categoria, lista in erros:
            print(f"\n[{categoria.upper()}]")
            for item in lista[:30]:  # limita exibição
                detalhes = ", ".join([f"{k}: {v}" for k, v in item.items()])
                print(f"  - {detalhes}")
        print("\n(Exibindo no máximo 30 ocorrências por heurística)\n")

    # --- Mostra tempo total de execução ---
    fim = time.time()
    duracao = fim - inicio
    print(f"Tempo total de execução: {duracao:.2f} segundos\n")
    
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
