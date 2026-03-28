import os
import sys
import json
import time
import importlib

from pyspark.sql import SparkSession

python_exec = f'"{sys.executable}"'
os.environ["PYSPARK_PYTHON"] = python_exec
os.environ["PYSPARK_DRIVER_PYTHON"] = python_exec


# ------------------------------------------------
# Carregar heurísticas dinamicamente
# ------------------------------------------------

def carregar_heuristicas():
    heuristicas = {}

    pasta = "heuristicas"

    if not os.path.exists(pasta):
        return heuristicas

    for arquivo in os.listdir(pasta):

        if arquivo.endswith(".py") and not arquivo.startswith("__"):

            nome = arquivo[:-3]

            try:
                modulo = importlib.import_module(f"heuristicas.{nome}")

                if hasattr(modulo, "executar"):
                    heuristicas[nome] = modulo.executar

            except Exception as e:
                print(f"Erro ao carregar heurística {nome}: {e}")

    return heuristicas


# ------------------------------------------------
# Resetar configuração
# ------------------------------------------------

def resetar_config():

    estado_inicial = {
        "heuristicas": [],
        "arquivo_csv": None
    }

    with open("heuristicas.config.json", "w", encoding="utf-8") as f:
        json.dump(estado_inicial, f, indent=4, ensure_ascii=False)

    print("Arquivo 'heuristicas.config.json' foi resetado para o estado inicial.\n")


# ------------------------------------------------
# Main
# ------------------------------------------------

def main():

    inicio = time.time()

    # Carrega heurísticas disponíveis
    HEURISTICAS = carregar_heuristicas()

    if not HEURISTICAS:
        print("Nenhuma heurística encontrada na pasta 'heuristicas'.")
        sys.exit(1)

    # ------------------------------------------------
    # Lê configuração
    # ------------------------------------------------

    try:
        with open("heuristicas.config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

    except FileNotFoundError:

        print("Arquivo 'heuristicas.config.json' não encontrado.")
        sys.exit(1)

    heuristicas_escolhidas = config.get("heuristicas", [])
    arquivo_csv = config.get("arquivo_csv", None)

    if not arquivo_csv:
        print("Nenhum arquivo CSV definido.")
        sys.exit(1)

    if not heuristicas_escolhidas:
        print("Nenhuma heurística configurada.")
        sys.exit(1)

    print(f"Arquivo selecionado: {arquivo_csv}")
    print(f"Heurísticas que serão aplicadas: {', '.join(heuristicas_escolhidas)}\n")

    # ------------------------------------------------
    # Criar Spark
    # ------------------------------------------------

    spark = (
        SparkSession.builder
        .appName("linter_equidade_dados_spark")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    # ------------------------------------------------
    # Ler CSV
    # ------------------------------------------------

    try:

        df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(arquivo_csv)
        )

    except Exception as e:

        print(f"Erro ao abrir '{arquivo_csv}': {e}")
        spark.stop()
        sys.exit(1)

    # ------------------------------------------------
    # Executar heurísticas
    # ------------------------------------------------

    total_verificacoes = len(heuristicas_escolhidas)
    erros = []

    for nome in heuristicas_escolhidas:

        func = HEURISTICAS.get(nome)

        if not func:
            print(f"Heurística '{nome}' não encontrada.")
            continue

        print(f"Executando heurística: {nome} ...")

        try:

            resultado = func(df)

            if resultado:
                erros.append((nome, resultado))

        except Exception as e:

            erros.append((nome, f"Erro ao executar heurística: {e}"))

    # ------------------------------------------------
    # Estatísticas
    # ------------------------------------------------

    percentual_erros = (len(erros) / total_verificacoes) * 100 if total_verificacoes else 0
    percentual_corretos = 100 - percentual_erros

    print(f"\nTotal de verificações: {total_verificacoes}")
    print(f"Lints detectados: {len(erros)}")
    print(f"Porcentagem de lints encontrados: {percentual_erros:.2f}%")
    print(f"Porcentagem de dados corretos: {percentual_corretos:.2f}%\n")

    # ------------------------------------------------
    # Mostrar erros
    # ------------------------------------------------

    if erros:

        print("Heurísticas (Lints) encontradas:")

        for categoria, erro in erros:
            print(f"  * [{categoria.upper()}] {erro}")

        print()

    # ------------------------------------------------
    # Tempo
    # ------------------------------------------------

    fim = time.time()
    duracao = fim - inicio

    print(f"Tempo total de execução: {duracao:.2f} segundos\n")

    resetar_config()

    spark.stop()

    if erros:
        sys.exit(1)
    else:
        print("Nenhum erro identificado com as heurísticas aplicadas.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()