from pyspark.sql import functions as F
from utils.resultado_lint import criar_resultado

def executar(df):

    resultados = []
    COL_TEMP = "__valor_coluna__"

    for coluna, dtype in df.dtypes:

        if dtype != "string":
            continue

        valores = (
            df.select(F.col(f"`{coluna}`").alias(COL_TEMP))
            .dropna()
            .distinct()
            .limit(1000)
        )

        valores_list = [r[COL_TEMP] for r in valores.collect()]
        lower_list = [str(v).lower() for v in valores_list]

        if len(set(lower_list)) < len(valores_list) and len(valores_list) > 0:

            resultados.append(
                criar_resultado(
                    codigo="DL005",
                    heuristica="miscoding_caps",
                    status="LINT",
                    coluna=coluna,
                    ocorrencias=len(valores_list) - len(set(lower_list)),
                    amostra=valores_list[:5],
                    mensagem="Possível inconsistência de maiúsculas/minúsculas."
                )
            )

    if not resultados:
        resultados.append(
            criar_resultado(
                codigo="DL005",
                heuristica="miscoding_caps",
                status="OK",
                mensagem="Nenhuma inconsistência de maiúsculas/minúsculas encontrada."
            )
        )

    return resultados