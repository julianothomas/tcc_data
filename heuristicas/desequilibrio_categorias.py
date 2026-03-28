from pyspark.sql import functions as F

def executar(df):

    problemas = {}
    total = df.count()

    if total == 0:
        return problemas

    for col, dtype in df.dtypes:

        if dtype not in ("string", "boolean"):
            continue

        freq_df = (
            df.groupBy(col)
            .count()
            .withColumn("freq", F.col("count") / F.lit(total))
        )

        dominantes = freq_df.filter(F.col("freq") > 0.9)

        if dominantes.count() > 0:

            freq_dict = {
                row[col]: float(row["freq"])
                for row in freq_df.collect()
            }

            problemas[col] = freq_dict

    return problemas