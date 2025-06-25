import sys
import pandas as pd
import numpy as np
import os


arquivo = sys.argv[1] if len(sys.argv) > 1 else "data/dados_validos.csv"

#Contador de erros
erros = []
total_verificacoes = 0  

COLUNAS_EXCECAO = {'nome', 'nome_completo', 'nome_aluno', 'first_name', 'last_name'}

# Heurísticas disponíveis
heuristicas_disponiveis = {
    '1': 'colunas_sem_nome',
    '2': 'colunas_vazias',
    '3': 'linhas_duplicadas',
    '4': 'desequilibrio_categorias',
    '5': 'miscoding_numerico',
    '6': 'miscoding_caps',
    '7': 'outliers'
}

print("SELECIONE AS HEURÍSTICAS QUE DESEJA APLICAR:")
for num, nome in heuristicas_disponiveis.items():
    print(f"{num}. {nome.replace('_', ' ').capitalize()}")

selecionadas = input("Digite os números separados por vírgula (ex: 1,3,5): ").split(',')
selecionadas = [heuristicas_disponiveis.get(op.strip()) for op in selecionadas if op.strip() in heuristicas_disponiveis]

if not selecionadas:
    print("Nenhuma heurística válida selecionada. Encerrando.")
    sys.exit(0)


try:
    df = pd.read_csv(arquivo)
except Exception as e:
    print(f"Erro ao ler o arquivo CSV: {e}")
    sys.exit(1)

print(f"Arquivo CSV '{os.path.basename(arquivo)}' carregado com {df.shape[0]} linhas e {df.shape[1]} colunas carregao com sucesso.\n")

#----Colunas sem nome----
total_verificacoes += 1
if any(col is None or str(col).startswith("Unnamed") for col in df.columns):
    erros.append(("estrutura", "Colunas sem nome ou marcadas como 'Unnamed'."))

#----Colunas completamente vazias----
total_verificacoes += 1
null_cols = df.columns[df.isnull().all()]
if len(null_cols) > 0:
    erros.append(("estrutura", f"Colunas totalmente vazias: {list(null_cols)}"))

#----Linhas duplicadas----
total_verificacoes += 1
if df.duplicated().any():
    erros.append(("estrutura", "Linhas duplicadas detectadas."))

#----Desequilíbrio de categorias----
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    if df[col].nunique() <= 10:
        proporcoes = df[col].value_counts(normalize=True)
        if proporcoes.max() > 0.7:
            erros.append(("equidade", f"Coluna '{col}' com desequilíbrio: {proporcoes.to_dict()}"))

#----Miscoding: números como texto----
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    try:
        pd.to_numeric(df[col])
        erros.append(("miscoding", f"Possível miscoding: coluna '{col}' contém números como texto."))
    except:
        pass

# ----iscoding: capitalização inconsistente----
for col in df.select_dtypes(include='object'):
    total_verificacoes += 1
    if col.lower() in COLUNAS_EXCECAO:
        continue
    unique_vals = df[col].dropna().unique()
    if any(isinstance(val, str) and val != val.lower() and val != val.upper() for val in unique_vals):
        erros.append(("miscoding", f"Inconsistência de capitalização em '{col}'."))

#----Outliers numéricos----
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

#Calcula porcentagem de erros e acertos
percentual_erros = (len(erros) / total_verificacoes) * 100 if total_verificacoes else 0
percentual_corretos = 100 - percentual_erros
print(f"\nTotal de verificações: {total_verificacoes}")
print(f"Lints detectados: {len(erros)}")
print(f"Porcentagem de lints encontrados: {percentual_erros:.2f}%")
print(f"Porcentagem de dados considerados corretos: {percentual_corretos:.2f}%")

#Imprime o resultado
if erros:
    print("Heurísticas(Lints) encontradas:")
    for categoria, erro in erros:
        print(f"  * [{categoria.upper()}] {erro}")
    print()
    sys.exit(1)
else:
    print("Nenhum erro identificado com as heurísticas aplicadas.\n")
    sys.exit(0)

