from pyspark.sql import functions as F
from utils.resultado_lint import criar_resultado

def executar(df):

    resultados = []
    total = df.count()

    if total == 0:
        return [
            criar_resultado(
                codigo="DL002",
                heuristica="colunas_vazias",
                status="OK",
                mensagem="Dataset vazio. Nenhuma coluna analisada."
            )
        ]

    agg_exprs = [
        F.sum(F.when(F.col(f"`{c}`").isNull(), 1).otherwise(0)).alias(c)
        for c in df.columns
    ]

    null_counts = df.agg(*agg_exprs).collect()[0].asDict()

    for coluna, nulos in null_counts.items():

        if nulos == total:
            resultados.append(
                criar_resultado(
                    codigo="DL002",
                    heuristica="colunas_vazias",
                    status="LINT",
                    coluna=coluna,
                    ocorrencias=int(nulos),
                    amostra=[None],
                    mensagem="Coluna totalmente vazia."
                )
            )

    if not resultados:
        resultados.append(
            criar_resultado(
                codigo="DL002",
                heuristica="colunas_vazias",
                status="OK",
                mensagem="Nenhuma coluna totalmente vazia encontrada."
            )
        )

    return resultados