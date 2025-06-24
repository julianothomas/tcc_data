import sys
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Caminho do arquivo
arquivo = sys.argv[1] if len(sys.argv) > 1 else "data/all_disciplines_combined.csv"
relatorio_path = "relatorio_linter.txt"

erros = []
total_verificacoes = 0

COLUNAS_EXCECAO = {'nome', 'nome_completo', 'nome_aluno', 'first_name', 'last_name'}

try:
    df = pd.read_csv(arquivo)
except Exception as e:
    print(f"Erro ao ler o arquivo CSV: {e}")
    sys.exit(1)

print(f"📥 CSV '{os.path.basename(arquivo)}' carregado com {df.shape[0]} linhas e {df.shape[1]} colunas.\n")

# ----------- VERIFICAÇÕES HEURÍSTICAS ------------

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

# 4. Desequilíbrio de categorias
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

# 6. Capitalização inconsistente
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    if col.lower() in COLUNAS_EXCECAO:
        continue
    unique_vals = df[col].dropna().unique()
    if any(isinstance(val, str) and val != val.lower() and val != val.upper() for val in unique_vals):
        erros.append(("miscoding", f"Inconsistência de capitalização em '{col}'."))

# 7. Outliers
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

# ---------- CÁLCULO DE PORCENTAGEM ----------
percentual_erros = (len(erros) / total_verificacoes) * 100 if total_verificacoes else 0
percentual_corretos = 100 - percentual_erros

# ---------- VISUALIZAÇÃO NO TERMINAL ----------
if erros:
    print("⚠️  Problemas encontrados:")
    for categoria, mensagem in erros:
        print(f"  • [{categoria.upper()}] {mensagem}")
    print()
else:
    print("✅ Nenhum erro identificado com as heurísticas aplicadas.\n")

print(f"Total de verificações: {total_verificacoes}")
print(f"Lints detectados: {len(erros)}")
print(f"Porcentagem de lints encontrados: {percentual_erros:.2f}%")
print(f"Porcentagem de dados considerados corretos: {percentual_corretos:.2f}%")

# ---------- GERAR RELATÓRIO EM TXT ----------
try:
    with open(relatorio_path, "w", encoding="utf-8") as f:
        f.write(f"Relatório de Verificação - Data Linter\n")
        f.write(f"Arquivo: {arquivo}\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de verificações: {total_verificacoes}\n")
        f.write(f"Lints encontrados: {len(erros)}\n")
        f.write(f"Porcentagem com erro: {percentual_erros:.2f}%\n")
        f.write(f"Porcentagem correta: {percentual_corretos:.2f}%\n\n")
        if erros:
            f.write("Erros encontrados:\n")
            for categoria, mensagem in erros:
                f.write(f" - [{categoria}] {message}\n")
        else:
            f.write("Nenhum erro foi encontrado.\n")
    print(f"\n📝 Relatório salvo em: {relatorio_path}")
except Exception as e:
    print(f"Erro ao salvar o relatório: {e}")
