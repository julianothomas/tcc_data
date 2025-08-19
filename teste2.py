import subprocess
import pandas as pd
import numpy as np
import os
import sys

COLUNAS_EXCECAO = {'nome', 'nome_completo', 'nome_aluno', 'first_name', 'last_name'}

# Se não receber arquivos como argumento, exibe ajuda
if len(sys.argv) < 2:
    print("Nenhum arquivo CSV informado para verificação.")
    sys.exit(0)

erros_detectados = False

for arquivo in sys.argv[1:]:
    if not arquivo.endswith(".csv"):
        continue

    erros = []
    total_verificacoes = 0

    print(f"\nVerificando arquivo: {arquivo}")

    try:
        df = pd.read_csv(arquivo)
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV '{arquivo}': {e}")
        erros_detectados = True
        continue

    print(f"Arquivo carregado com {df.shape[0]} linhas e {df.shape[1]} colunas.\n")

# ---- Colunas sem nome ----
total_verificacoes += 1
if any(col is None or str(col).startswith("Unnamed") for col in df.columns):
    erros.append(("estrutura", "Colunas sem nome ou marcadas como 'Unnamed'."))

# ---- Colunas completamente vazias ----
total_verificacoes += 1
null_cols = df.columns[df.isnull().all()]
if len(null_cols) > 0:
    erros.append(("estrutura", f"Colunas totalmente vazias: {list(null_cols)}"))

# ---- Linhas duplicadas ----
total_verificacoes += 1
if df.duplicated().any():
    erros.append(("estrutura", "Linhas duplicadas detectadas."))

# ---- Desequilíbrio de categorias ----
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    if df[col].nunique() <= 10:
        proporcoes = df[col].value_counts(normalize=True)
        if proporcoes.max() > 0.7:
            erros.append(("equidade", f"Coluna '{col}' com desequilíbrio: {proporcoes.to_dict()}"))

# ---- Miscoding: números como texto ----
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    try:
        pd.to_numeric(df[col])
        erros.append(("miscoding", f"Possível miscoding: coluna '{col}' contém números como texto."))
    except:
        pass

# ---- Miscoding: capitalização inconsistente ----
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    if col.lower() in COLUNAS_EXCECAO:
        continue
    unique_vals = df[col].dropna().unique()
    if any(isinstance(val, str) and val != val.lower() and val != val.upper() for val in unique_vals):
        erros.append(("miscoding", f"Inconsistência de capitalização em '{col}'."))

# ---- Outliers numéricos ----
for col in df.select_dtypes(include=np.number):
    total_verificacoes += 1
    if df[col].nunique() <= 1:
        continue
    std = df[col].std(ddof=0)
    mean = df[col].mean()

    if pd.isna(std) or std == 0:
        continue

    z_scores = (df[col] - mean) / std
    outliers = df[(z_scores > 3) | (z_scores < -3)]

    if not outliers.empty:
        erros.append(("outlier", f"Outliers na coluna '{col}': {len(outliers)} com valores irregulares."))

# ---- Resultados finais ----
percentual_erros = (len(erros) / total_verificacoes) * 100 if total_verificacoes else 0
percentual_corretos = 100 - percentual_erros

print(f"\nTotal de verificações: {total_verificacoes}")
print(f"Lints detectados: {len(erros)}")
print(f"Porcentagem de erros: {percentual_erros:.2f}%")
print(f"Porcentagem de dados corretos: {percentual_corretos:.2f}%\n")

if erros:
    print("Heurísticas (Lints) encontradas:")
    for categoria, erro in erros:
        print(f"  * [{categoria.upper()}] {erro}")
    erros_detectados = True
else:
    print("Nenhum erro identificado com as heurísticas aplicadas.")

# Encerra com código de erro se necessário
sys.exit(1 if erros_detectados else 0)
