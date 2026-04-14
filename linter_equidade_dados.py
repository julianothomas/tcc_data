import os
import sys
import json
import time
import importlib

from pyspark.sql import SparkSession

# ------------------------------------------------
# Caminhos base
# ------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_HEURISTICAS = os.path.join(BASE_DIR, "heuristicas")
CONFIG_PATH = os.path.join(BASE_DIR, "heuristicas.config.json")

# Como agora o caminho não tem espaços, usar sys.executable puro é melhor
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


# ------------------------------------------------
# Carregar heurísticas dinamicamente
# ------------------------------------------------

def carregar_heuristicas():
    heuristicas = {}

    if not os.path.exists(PASTA_HEURISTICAS):
        return heuristicas

    for arquivo in os.listdir(PASTA_HEURISTICAS):
        if arquivo.endswith(".py") and not arquivo.startswith("__"):
            nome = arquivo[:-3]

            try:
                modulo = importlib.import_module(f"heuristicas.{nome}")

                if hasattr(modulo, "executar"):
                    heuristicas[nome] = modulo.executar
                else:
                    print(f"A heurística '{nome}' não possui a função 'executar(df)'.")

            except Exception as e:
                print(f"Erro ao carregar heurística '{nome}': {e}")

    return heuristicas


# ------------------------------------------------
# Resetar configuração
# ------------------------------------------------

def resetar_config():
    estado_inicial = {
        "heuristicas": [],
        "arquivo_csv": None
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(estado_inicial, f, indent=4, ensure_ascii=False)

    print("Arquivo 'heuristicas.config.json' foi resetado para o estado inicial.\n")


# ------------------------------------------------
# Main
# ------------------------------------------------

def main():
    inicio = time.time()

    # Carrega heurísticas disponíveis
    heuristicas_disponiveis = carregar_heuristicas()

    if not heuristicas_disponiveis:
        print("Nenhuma heurística encontrada na pasta 'heuristicas'.")
        sys.exit(1)

    # ------------------------------------------------
    # Lê configuração
    # ------------------------------------------------

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
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
    # Ler CSV e cachear
    # ------------------------------------------------

    try:
        df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(arquivo_csv)
            .cache()
        )

        # força materialização do cache
        df.count()

    except Exception as e:
        print(f"Erro ao abrir '{arquivo_csv}': {e}")
        spark.stop()
        sys.exit(1)

    # ------------------------------------------------
    # Executar heurísticas
    # ------------------------------------------------

    total_verificacoes = len(heuristicas_escolhidas)
    lints = []
    falhas_execucao = []

    for nome in heuristicas_escolhidas:
        func = heuristicas_disponiveis.get(nome)

        if not func:
            falhas_execucao.append((nome, "Heurística não encontrada"))
            continue

        print(f"Executando heurística: {nome} ...")

        try:
            resultado = func(df)

            if resultado:
                lints.append((nome, resultado))

        except Exception as e:
            falhas_execucao.append((nome, f"Erro ao executar heurística: {e}"))

    # ------------------------------------------------
    # Estatísticas
    # ------------------------------------------------

    percentual_lints = (len(lints) / total_verificacoes) * 100 if total_verificacoes else 0
    percentual_corretos = 100 - percentual_lints

    print(f"\nTotal de verificações: {total_verificacoes}")
    print(f"Lints detectados: {len(lints)}")
    print(f"Falhas de execução: {len(falhas_execucao)}")
    print(f"Porcentagem de lints encontrados: {percentual_lints:.2f}%")
    print(f"Porcentagem de dados corretos: {percentual_corretos:.2f}%\n")

    # ------------------------------------------------
    # Mostrar lints
    # ------------------------------------------------

    if lints:
        print("Heurísticas (Lints) encontradas:")

        for categoria, erro in lints:
            print(f"  * [{categoria.upper()}] {erro}")

        print()

    # ------------------------------------------------
    # Mostrar falhas de execução
    # ------------------------------------------------

    if falhas_execucao:
        print("Falhas de execução:")

        for categoria, erro in falhas_execucao:
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

    if lints or falhas_execucao:
        sys.exit(1)
    else:
        print("Nenhum erro identificado com as heurísticas aplicadas.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()