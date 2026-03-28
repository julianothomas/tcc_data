def executar(df):

    total = df.count()
    distinct = df.distinct().count()

    duplicadas = total - distinct

    if duplicadas > 0:
        return {
            "quantidade_linhas_duplicadas": int(duplicadas)
        }

    return {}