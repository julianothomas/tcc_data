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

        if (arquivo.endswith(".py") and not arquivo.startswith("__") and not arquivo.startswith("utils_")):

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
    resultados_lint
):

    for nome in heuristicas_escolhidas:

        func = heuristicas_disponiveis.get(nome)

        if not func:

            resultados_lint.append({
                "arquivo": arquivo_dados,
                "codigo": "DL000",
                "heuristica": nome,
                "status": "ERRO",
                "coluna": None,
                "ocorrencias": 0,
                "amostra": [],
                "mensagem": "Heurística não encontrada."
            })

            continue

        print(f"Executando heurística: {nome} ...")

        try:

            resultados = func(df)

            for resultado in resultados:

                resultado["arquivo"] = arquivo_dados
                resultados_lint.append(resultado)

        except Exception as e:

            resultados_lint.append({
                "arquivo": arquivo_dados,
                "codigo": "DL000",
                "heuristica": nome,
                "status": "ERRO",
                "coluna": None,
                "ocorrencias": 0,
                "amostra": [],
                "mensagem": f"Erro ao executar heurística: {e}"
            })


# ------------------------------------------------
# MOSTRAR RELATÓRIO
# ------------------------------------------------

def salvar_relatorio_json(resultados_lint, tempo_total):

    relatorio = {
        "tempo_total_segundos": round(tempo_total, 2),
        "total_resultados": len(resultados_lint),
        "total_ok": len([r for r in resultados_lint if r.get("status") == "OK"]),
        "total_lints": len([r for r in resultados_lint if r.get("status") == "LINT"]),
        "total_erros": len([r for r in resultados_lint if r.get("status") == "ERRO"]),
        "resultados": resultados_lint
    }

    caminho_relatorio = os.path.join(
        BASE_DIR,
        "relatorio_lints.json"
    )

    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=4, ensure_ascii=False, default=str)

    print(f"\nRelatório completo salvo em: {caminho_relatorio}")


def mostrar_relatorio(resultados_lint, tempo_total):

    lints = [r for r in resultados_lint if r.get("status") == "LINT"]
    erros = [r for r in resultados_lint if r.get("status") == "ERRO"]
    oks = [r for r in resultados_lint if r.get("status") == "OK"]

    print("\n" + "=" * 70)
    print("RELATÓRIO DO DATA LINTER")
    print("=" * 70)

    print(f"OK: {len(oks)} | LINTS: {len(lints)} | ERROS: {len(erros)}")
    print(f"Tempo total: {tempo_total:.2f} segundos\n")

    print("ARQUIVO | CÓDIGO | STATUS | DESCRIÇÃO")
    print("-" * 70)

    for r in resultados_lint:

        arquivo = os.path.basename(
            r.get("arquivo", "arquivo_desconhecido")
        )

        codigo = r.get("codigo", "DL???")
        status = r.get("status", "INDEFINIDO")

        coluna = r.get("coluna")
        mensagem = r.get("mensagem", "")

        # ----------------------------------------
        # Compactar mensagens
        # ----------------------------------------

        mensagem = mensagem.replace(
            "Categoria dominante detectada: ",
            ""
        )

        mensagem = mensagem.replace(
            "representa",
            "="
        )

        mensagem = mensagem.replace(
            "dos registros.",
            ""
        )

        mensagem = mensagem.replace(
            "Coluna totalmente vazia.",
            "coluna totalmente vazia"
        )

        # ----------------------------------------
        # Mensagem final
        # ----------------------------------------

        if coluna:
            descricao = f"{coluna} {mensagem}"
        else:
            descricao = mensagem

        print(
            f"{arquivo} | "
            f"{codigo} | "
            f"{status} | "
            f"{descricao}"
        )

    print("=" * 70)

    salvar_relatorio_json(resultados_lint, tempo_total)


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

    resultados_lint = []

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

            resultados_lint.append({
                "arquivo": arquivo_dados,
                "codigo": "DL000",
                "heuristica": "leitura_arquivo",
                "status": "ERRO",
                "coluna": None,
                "ocorrencias": 0,
                "amostra": [],
                "mensagem": f"Erro ao abrir arquivo: {e}"
            })

            continue

        executar_heuristicas(
            df,
            arquivo_dados,
            heuristicas_escolhidas,
            heuristicas_disponiveis,
            resultados_lint
        )

    # --------------------------------------------
    # RELATÓRIO FINAL
    # --------------------------------------------

    mostrar_relatorio(
        resultados_lint,
        time.time() - inicio
    )

    resetar_config()

    spark.stop()

    if any(r["status"] in ("LINT", "ERRO") for r in resultados_lint):
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