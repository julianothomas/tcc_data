def criar_resultado(
    codigo,
    heuristica,
    status,
    mensagem,
    coluna=None,
    ocorrencias=0,
    amostra=None
):
    return {
        "codigo": codigo,
        "heuristica": heuristica,
        "status": status,
        "coluna": coluna,
        "ocorrencias": ocorrencias,
        "amostra": amostra or [],
        "mensagem": mensagem
    }