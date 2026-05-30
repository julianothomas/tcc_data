# Data Linter para Equidade de Dados

Uma proposta de **Data Linter** para validação automatizada de datasets, desenvolvida como Trabalho de Conclusão de Curso (TCC). A ferramenta realiza verificações de qualidade e equidade de dados utilizando heurísticas inspiradas no artigo *The Data Linter* (Hynes et al., 2017), integradas a um fluxo automatizado baseado em **Git Hooks**, **Husky**, **Python** e **PySpark**.

## Objetivo

O objetivo do projeto é identificar automaticamente inconsistências em datasets antes que eles sejam incorporados a pipelines de análise de dados ou aprendizado de máquina.

A ferramenta busca auxiliar na detecção precoce de problemas que podem comprometer a qualidade dos dados, como registros duplicados, valores inconsistentes, desequilíbrio de categorias e outros padrões suspeitos.

## Principais Funcionalidades

* Validação automática durante o processo de commit.
* Suporte a arquivos CSV e Parquet.
* Processamento distribuído utilizando PySpark.
* Arquitetura modular baseada em heurísticas.
* Carregamento dinâmico de novas validações.
* Integração com Git através do Husky.
* Retornos padronizados das inconsistências encontradas.

## Heurísticas Implementadas

Atualmente a ferramenta possui as seguintes validações:

* Colunas sem nome
* Colunas vazias
* Linhas duplicadas
* Desequilíbrio de categorias
* Miscoding numérico
* Miscoding de capitalização
* Detecção de outliers (IQR)
* Valores negativos

## Arquitetura

```text
Usuário
   │
   ▼
preinit.js
   │
   ▼
heuristicas.config.json
   │
   ▼
Git Commit
   │
   ▼
Husky (pre-commit)
   │
   ▼
linter_equidade_dados.py
   │
   ▼
PySpark
   │
   ▼
Heurísticas
   │
   ▼
Relatório de inconsistências
```

## Estrutura do Projeto

```text
├── data/
│   ├── datasets CSV e Parquet
│
├── heuristicas/
│   ├── colunas_sem_nome.py
│   ├── colunas_vazias.py
│   ├── linhas_duplicadas.py
│   ├── desequilibrio_categorias.py
│   ├── miscoding_numerico.py
│   ├── miscoding_caps.py
│   ├── outliers.py
│   └── valores_negativos.py
│
├── utils/
│   └── resultado_lint.py
│
├── preinit.js
├── linter_equidade_dados.py
├── heuristicas.config.json
└── README.md
```

## Tecnologias Utilizadas

| Tecnologia | Versão  |
| ---------- | ------- |
| Python     | 3.11.9  |
| PySpark    | 4.1.1   |
| OpenJDK    | 17.0.18 |
| Node.js    | 24.14.0 |
| Husky      | 9.1.7   |
| Git        | Atual   |
| VS Code    | Atual   |

## Fluxo de Execução

1. O usuário executa o arquivo `preinit.js`.
2. São selecionados os datasets e heurísticas desejados.
3. As configurações são armazenadas em `heuristicas.config.json`.
4. Durante um commit, o Husky executa automaticamente o hook de pré-commit.
5. O script `linter_equidade_dados.py` é iniciado.
6. O PySpark realiza a leitura dos datasets.
7. As heurísticas são carregadas dinamicamente.
8. As inconsistências encontradas são exibidas ao usuário.
9. Caso sejam detectados problemas, o commit pode ser interrompido.

## Diferenciais da Solução

* Inspirada no conceito de Data Linter para Machine Learning.
* Integração direta ao fluxo de desenvolvimento.
* Arquitetura extensível semelhante a plugins.
* Compatibilidade com ambientes de Big Data.
* Suporte a processamento distribuído.
* Foco em qualidade e equidade dos dados.

## Trabalhos Relacionados

A ferramenta foi inspirada principalmente pelo artigo:

> HYNES, N.; SCULLEY, D.; TERRY, M. *The Data Linter: Lightweight, Automated Sanity Checking for ML Data Sets*. NeurIPS, 2017.

Além disso, utiliza conceitos de:

* Data Validation for Machine Learning (Breck et al., 2019)
* Apache Spark (Zaharia et al., 2016)
* Data Smells (Foidl, Felderer e Ramler, 2022)

## Status do Projeto

🚧 Em desenvolvimento (TCC)

Etapas concluídas:

* Arquitetura da ferramenta
* Implementação das heurísticas
* Integração com Husky
* Migração de Pandas para PySpark
* Suporte a CSV e Parquet
* Testes iniciais com datasets públicos

Etapas em andamento:

* Consolidação dos resultados experimentais
* Avaliação em datasets de larga escala
* Discussão dos resultados
* Finalização da documentação acadêmica

## Autor

**Juliano Abi Thomas**

Trabalho de Conclusão de Curso – Engenharia da Computação
Universidade Federal de Mato Grosso do Sul (UFMS)
2026

## Artigo de Referência

Este trabalho foi inspirado no artigo:

HYNES, N.; SCULLEY, D.; TERRY, M.
The Data Linter: Lightweight, Automated Sanity Checking for ML Data Sets.
NeurIPS, 2017.

## Licença

Projeto desenvolvido para fins acadêmicos como Trabalho de Conclusão de Curso (TCC) da Universidade Federal de Mato Grosso do Sul (UFMS).