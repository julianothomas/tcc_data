import os
import json
import sys

# === Heurísticas disponíveis ===
HEURISTICAS = {
    "1": "colunas_sem_nome",
    "2": "colunas_vazias",
    "3": "linhas_duplicadas",
    "4": "desequilibrio_categorias",
    "5": "miscoding_numerico",
    "6": "miscoding_caps",
    "7": "outliers"
}


def escolher_arquivo(arquivos):
    """Exibe os arquivos CSV disponíveis e retorna o escolhido pelo usuário."""
    for i, nome in enumerate(arquivos, start=1):
        print(f"{i}. {nome}")
    escolha = input("\nDigite o número do arquivo CSV que deseja validar: ").strip()
    try:
        idx = int(escolha) - 1
        return arquivos[idx]
    except Exception:
        return None


def escolher_heuristicas():
    """Exibe as heurísticas e retorna as selecionadas."""
    print("\nSELECIONE AS HEURÍSTICAS QUE DESEJA APLICAR:")
    for num, nome in HEURISTICAS.items():
        print(f"{num}. {nome}")
    entrada = input("\nDigite os números separados por vírgula (ex: 1,3,5): ").strip()
    selecionadas = [HEURISTICAS.get(n.strip()) for n in entrada.split(",") if n.strip() in HEURISTICAS]
    return [h for h in selecionadas if h]


def main():
    print("CONFIGURAÇÃO DE HEURÍSTICAS\n")

    # Caminho fixo da pasta onde estão os CSVs
    # (ajuste este caminho se o seu projeto estiver em outro local)
    pasta_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

    print(f"Pasta de dados configurada: {pasta_csv}\n")

    # Verifica se a pasta existe
    if not os.path.isdir(pasta_csv):
        print(f"❌ Pasta '{pasta_csv}' não encontrada. Crie-a e adicione arquivos CSV.")
        sys.exit(1)

    # Lista todos os arquivos CSV
    arquivos_csv = [f for f in os.listdir(pasta_csv) if f.lower().endswith(".csv")]

    if not arquivos_csv:
        print("⚠ Nenhum arquivo CSV encontrado na pasta 'data/'. Adicione e tente novamente.")
        sys.exit(1)

    # Exibe os arquivos disponíveis
    print("ARQUIVOS DISPONÍVEIS:")
    arquivo_escolhido = escolher_arquivo(arquivos_csv)

    if not arquivo_escolhido:
        print("Seleção inválida. Encerrando.")
        sys.exit(1)

    # Escolhe as heurísticas
    heuristicas_escolhidas = escolher_heuristicas()
    if not heuristicas_escolhidas:
        print("Nenhuma heurística válida selecionada. Encerrando.")
        sys.exit(1)

    # Monta o caminho completo do CSV
    caminho_arquivo = os.path.join(pasta_csv, arquivo_escolhido)

    # Monta o dicionário de configuração
    configuracao = {
        "arquivo_csv": caminho_arquivo,
        "heuristicas": heuristicas_escolhidas
    }

    # Caminho para salvar o arquivo de configuração
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../heuristicas.config.json"))

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(configuracao, f, indent=2, ensure_ascii=False)

    print("\n✅ Preferências salvas em 'heuristicas.config.json':")
    print(f"Arquivo selecionado: {arquivo_escolhido}")
    print(f"Heurísticas: {', '.join(heuristicas_escolhidas)}")
    print("\nConfiguração concluída com sucesso!")


if __name__ == "__main__":
    main()
