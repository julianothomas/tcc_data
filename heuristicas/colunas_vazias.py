from pyspark.sql import functions as F

def executar(df):

    total = df.count()

    if total == 0:
        return []

    agg_exprs = [
        F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c)
        for c in df.columns
    ]

    null_counts = df.agg(*agg_exprs).collect()[0].asDict()

    return [c for c, n in null_counts.items() if n == total]