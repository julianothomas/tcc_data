import pandas as pd
import numpy as np
import os

# Criar pasta de saída
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

# Gerar dados válidos
def gerar_dados_validos():
    data = {
        "id": range(1, 101),
        "nome": [f"Pessoa{i}" for i in range(1, 101)],
        "idade": np.random.randint(18, 60, size=100),
        "sexo": np.random.choice(["M", "F"], size=100),
        "salario": np.round(np.random.normal(4000, 500, size=100), 2)
    }
    return pd.DataFrame(data)

# Gerar dados com erros
def gerar_dados_invalidos():
    base_len = 100
    data = {
        "id": [1, 2, 3, 3, 4, 5] + list(range(6, 100)),  # id duplicado (3)
        "nome": ["Pessoa1", "pessoa2", "Pessoa3", "Pessoa3", None, "Pessoa5"] +
                [f"Pessoa{i}" for i in range(6, 100)],
        "idade": [25, 30, -5, -5, 200, None] + list(np.random.randint(18, 60, size=94)),
        "sexo": ["M", "F", "Outro", "F", None, "M"] + list(np.random.choice(["M", "F"], size=94)),
        "salario": [5000, 10000, 1000000, 1000000, -100, None] +
                   list(np.round(np.random.normal(4000, 500, size=94), 2)),
        "Unnamed: 5": [None] * base_len  # coluna "fantasma"
    }

    # Ajustar todos os campos para 100 elementos
    for key in data:
        data[key] = data[key][:base_len]

    return pd.DataFrame(data)

# Criar DataFrames
df_valido = gerar_dados_validos()
df_invalido = gerar_dados_invalidos()

# Salvar arquivos
df_valido.to_csv(os.path.join(output_dir, "dados_validos.csv"), index=False)
df_invalido.to_csv(os.path.join(output_dir, "dados_invalidos.csv"), index=False)

print("Arquivos gerados com sucesso na pasta 'data/'")
