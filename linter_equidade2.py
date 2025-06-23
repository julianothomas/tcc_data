import sys
import pandas as pd
import numpy as np

# 1. Leitura com captura de erro
try:
    df = pd.read_csv("data/dados_invalidos.csv")
except Exception as e:
    print(f"Erro ao ler CSV: {e}")
    sys.exit(1)

# 2. Erro de estrutura: colunas sem nome
if any(col is None or str(col).startswith("Unnamed") for col in df.columns):
    print("⚠️ Erro de empacotamento: coluna sem nome encontrada.")
    sys.exit(1)

# 3. Erro de estrutura: colunas completamente nulas
null_cols = df.columns[df.isnull().all()]
if len(null_cols) > 0:
    print(f"⚠️ Erro de empacotamento: colunas totalmente vazias: {list(null_cols)}")
    sys.exit(1)

# 4. Duplicatas
if df.duplicated().any():
    print("❌ Dados duplicados detectados!")
    sys.exit(1)

# 5. Desequilíbrio de categorias
if 'sexo' in df.columns:
    proporcoes = df['sexo'].value_counts(normalize=True)
    if proporcoes.max() > 0.7:
        print(f"⚠️ Coluna 'sexo' com desequilíbrio: {proporcoes.to_dict()}")
        sys.exit(1)

# 6. Miscoding: strings onde deveriam ser números
for col in df.select_dtypes(include='object'):
    try:
        pd.to_numeric(df[col])
        print(f"⚠️ Possível miscoding: coluna '{col}' parece conter números codificados como texto.")
    except:
        pass  # ok, continua como texto

# 7. Miscoding: categorias inconsistentes (exceto nomes próprios)
for col in df.select_dtypes(include='object'):
    if col.lower() == 'nome':
        continue  # ignora a coluna de nomes

    unique_vals = df[col].dropna().unique()
    for val in unique_vals:
        if isinstance(val, str) and val != val.lower() and val != val.upper():
            print(f"⚠️ Inconsistência de capitalização na coluna '{col}': '{val}' pode estar fora de padrão.")
            sys.exit(1)

# 8. Outliers e escala
for col in df.select_dtypes(include=[np.number]):
    col_zscore = (df[col] - df[col].mean()) / df[col].std()
    outliers = df[col][(col_zscore > 3) | (col_zscore < -3)]
    if len(outliers) > 0:
        print(f"⚠️ Outliers detectados na coluna '{col}': {len(outliers)} valores fora de escala.")
        sys.exit(1)

print("✅ Dados passaram por todas as verificações de lint.")
