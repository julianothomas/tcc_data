import os
import sys
import json
import time
import importlib

from pyspark.sql import SparkSession

# ------------------------------------------------
# CONFIGURAÇÕES GERAIS
# ------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PASTA_HEURISTICAS = os.path.join(BASE_DIR, "heuristicas")

CONFIG_PATH = os.path.join(
    BASE_DIR,
    "heuristicas.config.json"
)

FORMATOS_SUPORTADOS = [".csv", ".parquet"]

LIMITE_REGISTROS = 50000

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


# ------------------------------------------------
# CARREGAR HEURÍSTICAS DINAMICAMENTE
# ------------------------------------------------

def carregar_heuristicas():

    heuristicas = {}

    if not os.path.exists(PASTA_HEURISTICAS):
        return heuristicas

    for arquivo in os.listdir(PASTA_HEURISTICAS):

        if arquivo.endswith(".py") and not arquivo.startswith("__"):

            nome = arquivo[:-3]

            try:

                modulo = importlib.import_module(
                    f"heuristicas.{nome}"
                )

                if hasattr(modulo, "executar"):

                    heuristicas[nome] = modulo.executar

                else:

                    print(
                        f"A heurística '{nome}' "
                        f"não possui a função executar(df)."
                    )

            except Exception as e:

                print(
                    f"Erro ao carregar heurística "
                    f"'{nome}': {e}"
                )

    return heuristicas


# ------------------------------------------------
# RESETAR CONFIGURAÇÃO
# ------------------------------------------------

def resetar_config():

    estado_inicial = {

        "heuristicas": [],
        "arquivos_dados": []

    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:

        json.dump(
            estado_inicial,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        "Arquivo 'heuristicas.config.json' "
        "foi resetado para o estado inicial.\n"
    )


# ------------------------------------------------
# CRIAR SESSÃO SPARK
# ------------------------------------------------

def criar_spark():

    spark = (

        SparkSession.builder

        .appName("linter_equidade_dados_spark")

        .master("local[*]")

        .config("spark.sql.shuffle.partitions", "4")

        .config("spark.driver.memory", "4g")

        .config("spark.executor.memory", "4g")

        .config(
            "spark.sql.parquet.outputTimestampType",
            "TIMESTAMP_MICROS"
        )

        .config(
            "spark.sql.legacy.parquet.nanosAsLong",
            "true"
        )

        .config(
            "spark.sql.parquet.enableVectorizedReader",
            "false"
        )

        .config(
            "spark.sql.parquet.columnarReaderBatchSize",
            "128"
        )

        .getOrCreate()

    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark


# ------------------------------------------------
# CARREGAR CONFIGURAÇÃO
# ------------------------------------------------

def carregar_config():

    try:

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:

            return json.load(f)

    except FileNotFoundError:

        print(
            "Arquivo 'heuristicas.config.json' "
            "não encontrado."
        )

        sys.exit(1)


# ------------------------------------------------
# CARREGAR DATAFRAME
# ------------------------------------------------

def carregar_dataframe(spark, arquivo_dados):

    extensao = os.path.splitext(
        arquivo_dados
    )[1].lower()

    # --------------------------------------------
    # CSV
    # --------------------------------------------

    if extensao == ".csv":

        df = (

            spark.read

            .option("header", True)

            .option("inferSchema", True)

            .csv(arquivo_dados)

        )

    # --------------------------------------------
    # PARQUET
    # --------------------------------------------

    elif extensao == ".parquet":

        df = spark.read.parquet(arquivo_dados)

    # --------------------------------------------
    # FORMATO NÃO SUPORTADO
    # --------------------------------------------

    else:

        raise ValueError(
            f"Formato não suportado: {extensao}"
        )

    # --------------------------------------------
    # LIMITAR REGISTROS
    # --------------------------------------------

    df = df.limit(LIMITE_REGISTROS)

    return df


# ------------------------------------------------
# EXECUTAR HEURÍSTICAS
# ------------------------------------------------

def executar_heuristicas(
    df,
    arquivo_dados,
    heuristicas_escolhidas,
    heuristicas_disponiveis,
    lints,
    falhas_execucao
):

    for nome in heuristicas_escolhidas:

        func = heuristicas_disponiveis.get(nome)

        if not func:

            falhas_execucao.append(

                (
                    arquivo_dados,
                    nome,
                    "Heurística não encontrada"
                )

            )

            continue

        print(f"Executando heurística: {nome} ...")

        try:

            resultado = func(df)

            if resultado:

                lints.append(

                    (
                        arquivo_dados,
                        nome,
                        resultado
                    )

                )

        except Exception as e:

            falhas_execucao.append(

                (
                    arquivo_dados,
                    nome,
                    f"Erro ao executar heurística: {e}"
                )

            )


# ------------------------------------------------
# MOSTRAR RELATÓRIO
# ------------------------------------------------

def mostrar_relatorio(
    total_verificacoes,
    arquivos_dados,
    lints,
    falhas_execucao,
    tempo_total
):

    percentual_lints = (

        (len(lints) / total_verificacoes) * 100

        if total_verificacoes else 0

    )

    percentual_corretos = 100 - percentual_lints

    print(f"\nTotal de verificações: {total_verificacoes}")

    print(
        f"Arquivos analisados: "
        f"{len(arquivos_dados)}"
    )

    print(f"Lints detectados: {len(lints)}")

    print(
        f"Falhas de execução: "
        f"{len(falhas_execucao)}"
    )

    print(
        f"Porcentagem de lints encontrados: "
        f"{percentual_lints:.2f}%"
    )

    print(
        f"Porcentagem de dados corretos: "
        f"{percentual_corretos:.2f}%\n"
    )

    # --------------------------------------------
    # MOSTRAR LINTS
    # --------------------------------------------

    if lints:

        print("Heurísticas (Lints) encontradas:")

        for arquivo, categoria, erro in lints:

            print(
                f"  * Arquivo: "
                f"{os.path.basename(arquivo)}"
            )

            print(
                f"    [{categoria.upper()}] "
                f"{erro}"
            )

        print()

    # --------------------------------------------
    # MOSTRAR FALHAS
    # --------------------------------------------

    if falhas_execucao:

        print("Falhas de execução:")

        for arquivo, categoria, erro in falhas_execucao:

            print(
                f"  * Arquivo: "
                f"{os.path.basename(arquivo)}"
            )

            print(
                f"    [{categoria.upper()}] "
                f"{erro}"
            )

        print()

    print(
        f"Tempo total de execução: "
        f"{tempo_total:.2f} segundos\n"
    )


# ------------------------------------------------
# MAIN
# ------------------------------------------------

def main():

    inicio = time.time()

    heuristicas_disponiveis = carregar_heuristicas()

    if not heuristicas_disponiveis:

        print(
            "Nenhuma heurística encontrada "
            "na pasta 'heuristicas'."
        )

        sys.exit(1)

    config = carregar_config()

    heuristicas_escolhidas = config.get(
        "heuristicas",
        []
    )

    arquivos_dados = config.get(
        "arquivos_dados",
        []
    )

    if not arquivos_dados:

        print("Nenhum arquivo de dados definido.")

        sys.exit(1)

    if not heuristicas_escolhidas:

        print("Nenhuma heurística configurada.")

        sys.exit(1)

    print("Arquivos selecionados:")

    for arquivo in arquivos_dados:

        print(f" - {arquivo}")

    print(

        "\nHeurísticas que serão aplicadas: "

        f"{', '.join(heuristicas_escolhidas)}\n"

    )

    spark = criar_spark()

    total_verificacoes = (

        len(heuristicas_escolhidas)

        * len(arquivos_dados)

    )

    lints = []

    falhas_execucao = []

    # --------------------------------------------
    # VALIDAR ARQUIVOS
    # --------------------------------------------

    for arquivo_dados in arquivos_dados:

        print(

            f"\nValidando arquivo: "
            f"{os.path.basename(arquivo_dados)}"

        )

        try:

            df = carregar_dataframe(
                spark,
                arquivo_dados
            )

        except Exception as e:

            falhas_execucao.append(

                (
                    arquivo_dados,
                    "leitura_arquivo",
                    f"Erro ao abrir arquivo: {e}"
                )

            )

            continue

        executar_heuristicas(

            df,
            arquivo_dados,
            heuristicas_escolhidas,
            heuristicas_disponiveis,
            lints,
            falhas_execucao

        )

    # --------------------------------------------
    # RELATÓRIO FINAL
    # --------------------------------------------

    mostrar_relatorio(

        total_verificacoes,
        arquivos_dados,
        lints,
        falhas_execucao,
        time.time() - inicio

    )

    resetar_config()

    spark.stop()

    if lints or falhas_execucao:

        sys.exit(1)

    else:

        print(
            "Nenhum erro identificado "
            "com as heurísticas aplicadas.\n"
        )

        sys.exit(0)


# ------------------------------------------------
# EXECUÇÃO
# ------------------------------------------------

if __name__ == "__main__":

    main()