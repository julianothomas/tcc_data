import pandas as pd

def ler_arquivo_series(caminho_csv):
    try:
        # Lê o CSV com separador '|', sem usar a primeira linha como cabeçalho
        df = pd.read_csv(caminho_csv, sep='|', header=None, engine='python', on_bad_lines='skip')

        # Exibe dimensões do DataFrame
        print(f"✅ Arquivo lido com sucesso: {df.shape[0]} linhas e {df.shape[1]} colunas.")
        
        # Exibe primeiras linhas
        print("\n📋 Primeiras linhas dos dados:")
        print(df.head())

        return df
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo: {e}")
        return None


def data_linter(df):
    print("\n🔍 Iniciando análise de qualidade de dados...\n")

    total_rows = len(df)

    # 1. Verificar duplicatas
    duplicated = df[df.duplicated()]
    if not duplicated.empty:
        print(f"🔁 Duplicatas encontradas ({len(duplicated)} linhas):")
        print(duplicated)
    else:
        print("✅ Nenhuma linha duplicada encontrada.")

    # 2. Verificar valores nulos
    print("\n🕳️ Valores nulos por coluna:")
    null_counts = df.isnull().sum()
    print(null_counts[null_counts > 0] if null_counts.any() else "✅ Nenhum valor nulo encontrado.")

    # 3. Colunas constantes
    print("\n📌 Colunas com valor constante:")
    constant_cols = [col for col in df.columns if df[col].nunique(dropna=False) == 1]
    if constant_cols:
        print("⚠️", constant_cols)
    else:
        print("✅ Nenhuma coluna constante.")

    # 4. Colunas com alta cardinalidade
    print("\n📊 Colunas com alta cardinalidade (mais de 90% de valores únicos):")
    for col in df.columns:
        unique_ratio = df[col].nunique() / total_rows
        if unique_ratio > 0.9:
            print(f"- Coluna {col}: {df[col].nunique()} únicos ({unique_ratio:.1%})")

    print("\n✅ Análise finalizada.")


# Execução
if __name__ == "__main__":
    caminho = "imdb_fake_movies.csv"  # Certifique-se que o arquivo está no mesmo diretório do script
    df_series = ler_arquivo_series(caminho)

    if df_series is not None:
        data_linter(df_series)
