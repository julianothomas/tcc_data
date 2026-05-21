from utils.resultado_lint import criar_resultado

def executar(df):

    resultados = []

    colunas = [col for col in df.columns if "Unnamed" in col]

    for coluna in colunas:
        resultados.append(
            criar_resultado(
                codigo="DL001",
                heuristica="colunas_sem_nome",
                status="LINT",
                coluna=coluna,
                ocorrencias=1,
                amostra=[coluna],
                mensagem="Coluna sem nome identificada."
            )
        )

    if not resultados:
        resultados.append(
            criar_resultado(
                codigo="DL001",
                heuristica="colunas_sem_nome",
                status="OK",
                mensagem="Nenhuma coluna sem nome encontrada."
            )
        )

    return resultados