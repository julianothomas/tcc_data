# Data Linter para Qualidade de Dados

Uma proposta de **Data Linter** para verificação automatizada da qualidade de dados, desenvolvida como Trabalho de Conclusão de Curso (TCC) do curso de Engenharia da Computação da Universidade Federal de Mato Grosso do Sul (UFMS).

A ferramenta realiza verificações automáticas em datasets por meio de heurísticas inspiradas no artigo *The Data Linter: Lightweight, Automated Sanity Checking for ML Data Sets* (Hynes, Sculley e Terry, 2017), integradas a um fluxo automatizado baseado em **Git Hooks**, **Husky**, **Python** e **PySpark**.

## Objetivo

O objetivo do projeto é apoiar a identificação precoce de problemas de qualidade em datasets antes de sua utilização em pipelines de análise de dados, engenharia de dados ou aprendizado de máquina.

A ferramenta busca detectar automaticamente inconsistências que podem comprometer a confiabilidade dos dados, reduzindo a propagação de problemas para etapas posteriores do fluxo de desenvolvimento.

## Principais Funcionalidades

* Validação automática durante o processo de commit.
* Suporte a arquivos CSV e Parquet.
* Processamento distribuído utilizando PySpark.
* Arquitetura modular baseada em heurísticas.
* Carregamento dinâmico de novas validações.
* Integração com Git através do Husky.
* Retorno padronizado dos resultados das verificações.

## Heurísticas Implementadas

Atualmente a ferramenta possui as seguintes validações:

* Colunas sem nome.
* Colunas vazias.
* Linhas duplicadas.
* Desequilíbrio de categorias.
* Miscoding numérico.
* Miscoding de capitalização.
* Detecção de outliers (IQR).
* Valores negativos.

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
linter_dados.py
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
├── linter_dados.py
├── heuristicas.config.json
└── README.md
```

## Tecnologias Utilizadas

| Tecnologia         | Versão  |
| ------------------ | ------- |
| Python             | 3.11.9  |
| PySpark            | 4.1.1   |
| OpenJDK            | 17.0.18 |
| Node.js            | 24.14.0 |
| Husky              | 9.1.7   |
| Git                | Atual   |
| Visual Studio Code | Atual   |

## Fluxo de Execução

1. O usuário executa o arquivo `preinit.js`.
2. São selecionados os datasets e heurísticas desejados.
3. As configurações são armazenadas em `heuristicas.config.json`.
4. Durante um commit, o Husky executa automaticamente o hook de pré-commit.
5. O script principal é iniciado.
6. O PySpark realiza a leitura dos datasets.
7. As heurísticas são carregadas dinamicamente.
8. As verificações são executadas.
9. Os resultados são apresentados ao usuário.
10. Caso ocorrências sejam identificadas, o commit pode ser interrompido.

## Resultados Experimentais

A ferramenta foi avaliada utilizando:

* 27 datasets públicos do benchmark MLE-Bench;
* Dataset HackRep em formato Parquet para validação da compatibilidade com PySpark.

Durante os experimentos foram realizadas:

* 1477 validações;
* 861 alertas de qualidade identificados;
* 0 erros de execução.

Os resultados demonstraram a capacidade da ferramenta em identificar automaticamente diferentes tipos de problemas de qualidade em datasets de aprendizado de máquina.

## Diferenciais da Solução

* Inspirada no conceito de Data Linter para Machine Learning.
* Integração direta ao fluxo de desenvolvimento.
* Arquitetura modular e extensível.
* Compatibilidade com ambientes de Big Data.
* Suporte a processamento distribuído.
* Utilização de PySpark.
* Suporte aos formatos CSV e Parquet.

## Trabalhos Relacionados

A proposta foi inspirada principalmente por:

* Hynes, N.; Sculley, D.; Terry, M. (2017). *The Data Linter: Lightweight, Automated Sanity Checking for ML Data Sets*.

Além disso, utiliza conceitos de:

* Breck et al. (2019) – Data Validation for Machine Learning.
* Zaharia et al. (2016) – Apache Spark.
* Foidl, Felderer e Ramler (2022) – Data Smells.

## Status do Projeto

✅ Implementação concluída

✅ Avaliação experimental concluída

✅ Suporte a CSV e Parquet

✅ Integração com Husky

✅ Migração para PySpark

🔄 Evoluções futuras:

* Inclusão de novas heurísticas;
* Geração automática de relatórios;
* Integração com plataformas de CI/CD;
* Avaliação em datasets de maior escala.

## Autor

**Juliano Abi Thomas**

Trabalho de Conclusão de Curso – Engenharia da Computação

Universidade Federal de Mato Grosso do Sul (UFMS)

2026

## Artigo de Referência

HYNES, N.; SCULLEY, D.; TERRY, M.

*The Data Linter: Lightweight, Automated Sanity Checking for ML Data Sets.*

Machine Learning Systems Workshop (MLSys), 2017.

http://learningsys.org/nips17/assets/papers/paper_19.pdf

## Licença

Projeto desenvolvido para fins acadêmicos como Trabalho de Conclusão de Curso da Universidade Federal de Mato Grosso do Sul (UFMS).
