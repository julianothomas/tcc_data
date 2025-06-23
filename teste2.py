import sys
import pandas as pd
import numpy as np

# Lista para coletar os erros encontrados
erros = []

# 1. Leitura com captura de erro
try:
    df = pd.read_csv("data/all_disciplines_combined.csv")
except Exception as e:
    erros.append(f"Erro ao ler CSV: {e}")
    df = None

if df is not None:

    # 2. Erro de estrutura: colunas sem nome
    if any(col is None or str(col).startswith("Unnamed") for col in df.columns):
        erros.append("Erro de estrutura: coluna sem nome encontrada.")

    # 3. Erro de estrutura: colunas completamente nulas
    null_cols = df.columns[df.isnull().all()]
    if len(null_cols) > 0:
        erros.append(f"Erro de empacotamento: colunas totalmente vazias: {list(null_cols)}")

    # 4. Duplicatas
    if df.duplicated().any():
        erros.append("Dados duplicados detectados!")

    # 5. Desequilíbrio de categorias
    if 'sexo' in df.columns:
        proporcoes = df['sexo'].value_counts(normalize=True)
        if proporcoes.max() > 0.7:
            erros.append(f"Coluna 'sexo' com desequilíbrio: {proporcoes.to_dict()}")

    # 6. Miscoding: strings onde deveriam ser números
    for col in df.select_dtypes(include='object'):
        try:
            pd.to_numeric(df[col])
            erros.append(f"Possível miscoding: coluna '{col}' parece conter números codificados como texto.")
        except:
            pass

    # 7. Miscoding: categorias inconsistentes (exceto nomes próprios)
    for col in df.select_dtypes(include='object'):
        if col.lower() == 'nome':
            continue
        unique_vals = df[col].dropna().unique()
        for val in unique_vals:
            if isinstance(val, str) and val != val.lower() and val != val.upper():
                erros.append(f"Inconsistência de capitalização na coluna '{col}': '{val}' pode estar fora de padrão.")
                break

    # 8. Outliers e escala
    for col in df.select_dtypes(include=[np.number]):
        col_zscore = (df[col] - df[col].mean()) / df[col].std()
        outliers = df[col][(col_zscore > 3) | (col_zscore < -3)]
        if len(outliers) > 0:
            erros.append(f"Outliers detectados na coluna '{col}': {len(outliers)} valores fora de escala.")

# Resultado final
if erros:
    print("Problemas encontrados nos dados:")
    for erro in erros:
        print("*", erro)
    sys.exit(1)
else:
    print("Os dados passaram por todas as validações e heurísticas, e não apresentam erros.")
