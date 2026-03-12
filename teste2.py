import os
import sys
import json
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

python_exec = f'"{sys.executable}"'
os.environ["PYSPARK_PYTHON"] = python_exec
os.environ["PYSPARK_DRIVER_PYTHON"] = python_exec


# --- Heurísticas implementadas em PySpark ---

def colunas_sem_nome(df):
    return [col for col in df.columns if "Unnamed" in col]


def colunas_vazias(df):
    """Colunas em que todas as linhas são nulas."""
    total = df.count()
    if total == 0:
        return []

    # conta nulos por coluna em uma única varrida
    agg_exprs = [
        F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c)
        for c in df.columns
    ]
    null_counts = df.agg(*agg_exprs).collect()[0].asDict()

    return [c for c, n in null_counts.items() if n == total]


def linhas_duplicadas(df):
    """Retorna a quantidade de linhas duplicadas."""
    total = df.count()
    distinct = df.distinct().count()
    duplicadas = total - distinct
    if duplicadas > 0:
        return {"quantidade_linhas_duplicadas": int(duplicadas)}
    return {}


def desequilibrio_categorias(df):
    """Colunas categóricas onde alguma categoria domina > 90%."""
    problemas = {}
    total = df.count()
    if total == 0:
        return problemas

    for col, dtype in df.dtypes:
        # Considera strings como categóricas
        if dtype not in ("string", "boolean"):
            continue

        freq_df = (
            df.groupBy(col)
              .count()
              .withColumn("freq", F.col("count") / F.lit(total))
        )

        # pega categorias com freq > 0.9
        dominantes = freq_df.filter(F.col("freq") > 0.9)

        if dominantes.count() > 0:
            # transforma em dict: categoria -> freq
            freq_dict = {
                row[col]: float(row["freq"])
                for row in freq_df.collect()
            }
            problemas[col] = freq_dict

    return problemas


def miscoding_numerico(df):
    problemas = {}

    for col, dtype in df.dtypes:
        if dtype != "string":
            continue

        convertido = df.withColumn("temp_num", F.expr(f"try_cast({col} AS DOUBLE)"))

        erros = convertido.filter(
            (F.col(col).isNotNull()) &
            (F.col(col) != "") &
            F.col("temp_num").isNull()
        )

        if erros.limit(1).count() > 0:
            problemas[col] = "valores não numéricos detectados"

    return problemas



def miscoding_caps(df):
    """
    Colunas string onde existem valores iguais ignorando maiúsculas/minúsculas
    mas escritos de formas diferentes: 'Sim' vs 'sim' vs 'SIM'.
    """
    problemas = {}

    for col, dtype in df.dtypes:
        if dtype != "string":
            continue

        valores = df.select(col).dropna().distinct()
        valores_list = [r[col] for r in valores.collect()]

        # normaliza pra minúsculo
        lower_list = [str(v).lower() for v in valores_list]
        # se ao baixar pra minúsculo diminuir a quantidade de distintos,
        # é porque havia diferenças só de maiúscula/minúscula
        if len(set(lower_list)) < len(valores_list) and len(valores_list) > 0:
            problemas[col] = "valores inconsistentes em maiúsculas/minúsculas"

    return problemas


def outliers(df):
    """
    Usa IQR (Q1, Q3) para detectar outliers em colunas numéricas.
    """
    problemas = {}

    for col, dtype in df.dtypes:
        if dtype not in ("int", "bigint", "double", "float", "long", "decimal"):
            continue

        # approxQuantile é eficiente em grandes volumes
        q1, q3 = df.approxQuantile(col, [0.25, 0.75], 0.01)
        iqr = q3 - q1
        limite_inf = q1 - 1.5 * iqr
        limite_sup = q3 + 1.5 * iqr

        qtd_outliers = df.filter(
            (F.col(col) < limite_inf) | (F.col(col) > limite_sup)
        ).count()

        if qtd_outliers > 0:
            problemas[col] = {
                "limite_inferior": float(limite_inf),
                "limite_superior": float(limite_sup),
                "quantidade_outliers": int(qtd_outliers),
            }

    return problemas


# --- Mapeamento de heurísticas ---
HEURISTICAS = {
    "colunas_sem_nome": colunas_sem_nome,
    "colunas_vazias": colunas_vazias,
    "linhas_duplicadas": linhas_duplicadas,
    "desequilibrio_categorias": desequilibrio_categorias,
    "miscoding_numerico": miscoding_numerico,
    "miscoding_caps": miscoding_caps,
    "outliers": outliers,
}


def resetar_config():
    """Restaura o arquivo heuristicas.config.json para o estado padrão."""
    estado_inicial = {
        "heuristicas": [],
        "arquivo_csv": None
    }
    with open("heuristicas.config.json", "w", encoding="utf-8") as f:
        json.dump(estado_inicial, f, indent=4, ensure_ascii=False)
    print("Arquivo 'heuristicas.config.json' foi resetado para o estado inicial.\n")


def main():
    inicio = time.time()

    # --- Lê arquivo de configuração ---
    try:
        with open("heuristicas.config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Arquivo 'heuristicas.config.json' não encontrado. Rode `node preinit.js` antes.")
        sys.exit(1)

    heuristicas_escolhidas = config.get("heuristicas", [])
    arquivo_csv = config.get("arquivo_csv", None)

    if not arquivo_csv:
        print("Nenhum arquivo CSV definido em heuristicas.config.json.")
        sys.exit(1)

    if not heuristicas_escolhidas:
        print("Nenhuma heurística configurada.")
        sys.exit(1)

    print(f"Arquivo selecionado: {arquivo_csv}")
    print(f"Heurísticas que serão aplicadas: {', '.join(heuristicas_escolhidas)}\n")

    # --- Cria SparkSession ---
    spark = (
        SparkSession.builder
        .appName("linter_equidade_dados_spark")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    # --- Lê o CSV com Spark ---
    try:
        df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(arquivo_csv)
        )
    except Exception as e:
        print(f"Erro ao abrir '{arquivo_csv}' com Spark: {e}")
        spark.stop()
        sys.exit(1)

    # --- Executa as heurísticas ---
    total_verificacoes = len(heuristicas_escolhidas)
    erros = []

    for nome in heuristicas_escolhidas:
        func = HEURISTICAS.get(nome)
        if func:
            print(f"Executando heurística: {nome} ...")
            resultado = func(df)
            if resultado:  # se não estiver vazio
                erros.append((nome, resultado))

    # --- Calcula estatísticas ---
    percentual_erros = (len(erros) / total_verificacoes) * 100 if total_verificacoes else 0
    percentual_corretos = 100 - percentual_erros

    print(f"\nTotal de verificações: {total_verificacoes}")
    print(f"Lints detectados: {len(erros)}")
    print(f"Porcentagem de lints encontrados: {percentual_erros:.2f}%")
    print(f"Porcentagem de dados corretos: {percentual_corretos:.2f}%\n")

    # --- Exibe resultados ---
    if erros:
        print("Heurísticas (Lints) encontradas:")
        for categoria, erro in erros:
            print(f"  * [{categoria.upper()}] {erro}")
        print()

    # --- Mostra tempo total de execução ---
    fim = time.time()
    duracao = fim - inicio
    print(f"Tempo total de execução: {duracao:.2f} segundos\n")

    # --- Resetar configuração antes de sair ---
    resetar_config()

    # --- Encerra Spark ---
    spark.stop()

    # --- Sair com código apropriado ---
    if erros:
        sys.exit(1)
    else:
        print("Nenhum erro identificado com as heurísticas aplicadas.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
