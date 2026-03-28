from pyspark.sql import functions as F

def executar(df):

    problemas = {}

    for col, dtype in df.dtypes:

        if dtype != "string":
            continue

        convertido = df.withColumn(
            "temp_num",
            F.expr(f"try_cast(`{col}` AS DOUBLE)")
        )

        erros = convertido.filter(
            (F.col(col).isNotNull()) &
            (F.col(col) != "") &
            F.col("temp_num").isNull()
        )

        if erros.limit(1).count() > 0:
            problemas[col] = "valores não numéricos detectados"

    return problemas