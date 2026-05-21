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

        quantis = df.approxQuantile(
            coluna,
            [0.25, 0.75],
            0.01
        )

        if len(quantis) < 2:
            continue

        q1, q3 = quantis
        iqr = q3 - q1

        if iqr == 0:
            continue

        limite_inf = q1 - 1.5 * iqr
        limite_sup = q3 + 1.5 * iqr

        filtro_outliers = (
            (F.col(f"`{coluna}`") < limite_inf) |
            (F.col(f"`{coluna}`") > limite_sup)
        )

        qtd_outliers = df.filter(filtro_outliers).count()

        if qtd_outliers > 0:

            amostra = [
                r[coluna]
                for r in df.filter(filtro_outliers)
                .select(F.col(f"`{coluna}`"))
                .limit(5)
                .collect()
            ]

            resultados.append(
                criar_resultado(
                    codigo="DL007",
                    heuristica="outliers",
                    status="LINT",
                    coluna=coluna,
                    ocorrencias=int(qtd_outliers),
                    amostra=amostra,
                    mensagem=(
                        f"Outliers detectados pelo método IQR. "
                        f"Limites: [{limite_inf:.2f}, {limite_sup:.2f}]."
                    )
                )
            )

    if not resultados:
        resultados.append(
            criar_resultado(
                codigo="DL007",
                heuristica="outliers",
                status="OK",
                mensagem="Nenhum outlier encontrado nas colunas numéricas."
            )
        )

    return resultados