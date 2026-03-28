from pyspark.sql import functions as F

def executar(df):

    problemas = {}

    for col, dtype in df.dtypes:

        if dtype not in (
            "int",
            "bigint",
            "double",
            "float",
            "long",
            "decimal"
        ):
            continue

        q1, q3 = df.approxQuantile(col, [0.25, 0.75], 0.01)

        iqr = q3 - q1

        limite_inf = q1 - 1.5 * iqr
        limite_sup = q3 + 1.5 * iqr

        qtd_outliers = df.filter(
            (F.col(col) < limite_inf) |
            (F.col(col) > limite_sup)
        ).count()

        if qtd_outliers > 0:

            problemas[col] = {
                "limite_inferior": float(limite_inf),
                "limite_superior": float(limite_sup),
                "quantidade_outliers": int(qtd_outliers),
            }

    return problemas