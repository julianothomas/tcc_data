import sys
import pandas as pd
import numpy as np
import os

# Caminho do arquivo (permite argumento por linha de comando)
arquivo = sys.argv[1] if len(sys.argv) > 1 else "data/dados_validos.csv"

# Lista de erros detectados
erros = []
total_verificacoes = 0  # Contador de verificações feitas

# Conjunto de colunas a ignorar para miscoding (ex: nomes próprios)
COLUNAS_EXCECAO = {'nome', 'nome_completo', 'nome_aluno', 'first_name', 'last_name'}

# Leitura segura do CSV
try:
    df = pd.read_csv(arquivo)
except Exception as e:
    print(f"Erro ao ler o arquivo CSV: {e}")
    sys.exit(1)

print(f"Arquivo CSV '{os.path.basename(arquivo)}' carregado com {df.shape[0]} linhas e {df.shape[1]} colunas carregao com sucesso.\n")

# 1. Colunas sem nome
total_verificacoes += 1
if any(col is None or str(col).startswith("Unnamed") for col in df.columns):
    erros.append(("estrutura", "Colunas sem nome ou marcadas como 'Unnamed'."))

# 2. Colunas completamente vazias
total_verificacoes += 1
null_cols = df.columns[df.isnull().all()]
if len(null_cols) > 0:
    erros.append(("estrutura", f"Colunas totalmente vazias: {list(null_cols)}"))

# 3. Linhas duplicadas
total_verificacoes += 1
if df.duplicated().any():
    erros.append(("estrutura", "Linhas duplicadas detectadas."))

# 4. Desequilíbrio de categorias (para colunas categóricas com até 10 valores únicos)
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    if df[col].nunique() <= 10:
        proporcoes = df[col].value_counts(normalize=True)
        if proporcoes.max() > 0.7:
            erros.append(("equidade", f"Coluna '{col}' com desequilíbrio: {proporcoes.to_dict()}"))

# 5. Miscoding: números como texto
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    try:
        pd.to_numeric(df[col])
        erros.append(("miscoding", f"Possível miscoding: coluna '{col}' contém números como texto."))
    except:
        pass

# 6. Miscoding: capitalização inconsistente
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    if col.lower() in COLUNAS_EXCECAO:
        continue
    unique_vals = df[col].dropna().unique()
    if any(isinstance(val, str) and val != val.lower() and val != val.upper() for val in unique_vals):
        erros.append(("miscoding", f"Inconsistência de capitalização em '{col}'."))

# 7. Outliers numéricos (z-score > 3 ou < -3)
for col in df.select_dtypes(include=np.number):
    total_verificacoes += 1
    if df[col].nunique() <= 1:
        continue  # ignora colunas constantes ou binárias
    std = df[col].std(ddof=0)
    mean = df[col].mean()

    if pd.isna(std) or std == 0:
        continue  # ignora se o desvio padrão não é válido

    z_scores = (df[col] - mean) / std
    outliers = df[(z_scores > 3) | (z_scores < -3)]

    if not outliers.empty:
        erros.append(("outlier", f"Outliers na coluna '{col}': {len(outliers)} com valores irregulares."))

# Porcentagem de erros
percentual_erros = (len(erros) / total_verificacoes) * 100 if total_verificacoes else 0
percentual_corretos = 100 - percentual_erros
print(f"Total de verificações: {total_verificacoes}")
print(f"Lints detectados: {len(erros)}")
print(f"Porcentagem de lints encontrados: {percentual_erros:.2f}%")
print(f"Porcentagem de dados considerados corretos: {percentual_corretos:.2f}%")

# Resultado
if erros:
    print("Heurísticas(Lints) encontradas:")
    for categoria, erro in erros:
        print(f"  * [{categoria.upper()}] {erro}")
    print()
    sys.exit(1)
else:
    print("Nenhum erro identificado com as heurísticas aplicadas.\n")
    sys.exit(0)

