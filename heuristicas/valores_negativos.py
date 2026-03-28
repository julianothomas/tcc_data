from pyspark.sql import functions as F

def executar(df):

    problemas = {}

    for col, dtype in df.dtypes:

        if dtype in ("int", "double", "float"):

            negativos = df.filter(F.col(col) < 0).count()

            if negativos > 0:
                problemas[col] = f"{negativos} valores negativos"

    return problemas