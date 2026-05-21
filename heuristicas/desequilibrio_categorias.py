from pyspark.sql import functions as F
from utils.resultado_lint import criar_resultado

def executar(df):

    resultados = []
    total = df.count()
    LIMIAR = 0.90

    if total == 0:
        return [
            criar_resultado(
                codigo="DL003",
                heuristica="desequilibrio_categorias",
                status="OK",
                mensagem="Dataset vazio. Nenhuma coluna analisada."
            )
        ]

    for coluna, dtype in df.dtypes:

        if dtype not in ("string", "boolean"):
            continue

        freq_df = (
            df.groupBy(F.col(f"`{coluna}`"))
            .count()
            .withColumn("freq", F.col("count") / F.lit(total))
        )

        dominantes = freq_df.filter(F.col("freq") > LIMIAR).collect()

        for row in dominantes:

            valor = row[coluna]
            ocorrencias = int(row["count"])
            freq = float(row["freq"])

            resultados.append(
                criar_resultado(
                    codigo="DL003",
                    heuristica="desequilibrio_categorias",
                    status="LINT",
                    coluna=coluna,
                    ocorrencias=ocorrencias,
                    amostra=[valor],
                    mensagem=(
                        f"Categoria dominante detectada: '{valor}' "
                        f"representa {freq:.2%} dos registros."
                    )
                )
            )

    if not resultados:
        resultados.append(
            criar_resultado(
                codigo="DL003",
                heuristica="desequilibrio_categorias",
                status="OK",
                mensagem="Nenhuma categoria dominante encontrada."
            )
        )

    return resultados