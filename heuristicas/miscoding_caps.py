def executar(df):

    problemas = {}

    for col, dtype in df.dtypes:

        if dtype != "string":
            continue

        valores = df.select(col).dropna().distinct()
        valores_list = [r[col] for r in valores.collect()]

        lower_list = [str(v).lower() for v in valores_list]

        if len(set(lower_list)) < len(valores_list) and len(valores_list) > 0:

            problemas[col] = "valores inconsistentes em maiúsculas/minúsculas"

    return problemas