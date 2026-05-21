from pyspark.sql import functions as F
from utils.resultado_lint import criar_resultado

def executar(df):

    resultados = []

    tipos_numericos = (
        "int",
        "bigint",
        "double",
        "float",
        "long",
        "decimal",
        "smallint",
        "tinyint"
    )

    for coluna, dtype in df.dtypes:

        if not any(dtype.startswith(t) for t in tipos_numericos):
            continue

        negativos_df = df.filter(F.col(f"`{coluna}`") < 0)
        qtd_negativos = negativos_df.count()

        if qtd_negativos > 0:

            amostra = [
                r[coluna]
                for r in negativos_df.select(F.col(f"`{coluna}`")).limit(5).collect()
            ]

            resultados.append(
                criar_resultado(
                    codigo="DL008",
                    heuristica="valores_negativos",
                    status="LINT",
                    coluna=coluna,
                    ocorrencias=int(qtd_negativos),
                    amostra=amostra,
                    mensagem="Valores negativos detectados em coluna numérica."
                )
            )

    if not resultados:
        resultados.append(
            criar_resultado(
                codigo="DL008",
                heuristica="valores_negativos",
                status="OK",
                mensagem="Nenhum valor negativo encontrado."
            )
        )

    return resultados