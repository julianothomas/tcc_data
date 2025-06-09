import sys
import pandas as pd

try:
    df = pd.read_csv("data/dados.csv")
except Exception as e:
    print(f"Erro ao ler CSV: {e}")
    sys.exit(1)

if df.duplicated().any():
    print("Dados duplicados detectados!")
    sys.exit(1)

if 'sexo' in df.columns:
    proporcoes = df['sexo'].value_counts(normalize=True)
    if proporcoes.max() > 0.7:
        print(f"Coluna 'sexo' com desequilíbrio: {proporcoes.to_dict()}")
        sys.exit(1)

print("Dados validados com sucesso.")
