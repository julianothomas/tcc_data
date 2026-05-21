from utils.resultado_lint import criar_resultado

def executar(df):

    total = df.count()
    distintos = df.distinct().count()
    duplicadas = total - distintos

    if duplicadas > 0:
        amostra = [
            row.asDict()
            for row in df.groupBy(df.columns)
            .count()
            .filter("count > 1")
            .limit(3)
            .collect()
        ]

        return [
            criar_resultado(
                codigo="DL004",
                heuristica="linhas_duplicadas",
                status="LINT",
                ocorrencias=int(duplicadas),
                amostra=amostra,
                mensagem="Linhas duplicadas detectadas no dataset."
            )
        ]

    return [
        criar_resultado(
            codigo="DL004",
            heuristica="linhas_duplicadas",
            status="OK",
            mensagem="Nenhuma linha duplicada encontrada."
        )
    ]