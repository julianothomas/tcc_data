from pyspark.sql import functions as F
from utils.resultado_lint import criar_resultado

def executar(df):

    resultados = []
    COL_TEMP = "__valor_coluna__"

    for coluna, dtype in df.dtypes:

        if dtype != "string":
            continue

        base = df.select(
            F.col(f"`{coluna}`").alias(COL_TEMP)
        )

        convertido = base.withColumn(
            "temp_num",
            F.expr(f"try_cast(`{COL_TEMP}` AS DOUBLE)")
        )

        total_validos = convertido.filter(
            (F.col(COL_TEMP).isNotNull()) &
            (F.col(COL_TEMP) != "")
        ).count()

        if total_validos == 0:
            continue

        numericos = convertido.filter(
            (F.col(COL_TEMP).isNotNull()) &
            (F.col(COL_TEMP) != "") &
            (F.col("temp_num").isNotNull())
        ).count()

        proporcao_numerica = numericos / total_validos

        if proporcao_numerica > 0.8 and proporcao_numerica < 1.0:

            amostra = [
                r[COL_TEMP]
                for r in convertido.filter(
                    (F.col(COL_TEMP).isNotNull()) &
                    (F.col(COL_TEMP) != "") &
                    (F.col("temp_num").isNull())
                ).select(COL_TEMP).limit(5).collect()
            ]

            resultados.append(
                criar_resultado(
                    codigo="DL006",
                    heuristica="miscoding_numerico",
                    status="LINT",
                    coluna=coluna,
                    ocorrencias=int(total_validos - numericos),
                    amostra=amostra,
                    mensagem=(
                        "Coluna textual com maioria de valores numéricos, "
                        "mas contendo valores não numéricos."
                    )
                )
            )

    if not resultados:
        resultados.append(
            criar_resultado(
                codigo="DL006",
                heuristica="miscoding_numerico",
                status="OK",
                mensagem="Nenhum problema de codificação numérica encontrado."
            )
        )

    return resultados