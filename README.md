# sdd-taskanalyzer

![CI](https://github.com/Pedroprogs/sdd-taskanalyzer/actions/workflows/ci.yml/badge.svg?branch=main)

Módulo **TaskAnalyzer**: análise de tarefas e produtividade (totais, tempo médio de conclusão geral e por prioridade, e taxa de atraso), desenvolvido com **Spec-Driven Development (SDD)**, código gerado por IA e homologação humana.

## Estrutura do repositório

```
sdd-taskanalyzer/
|-- .github/workflows/ci.yml        # Pipeline de CI (GitHub Actions)
|-- Dockerfile                      # Imagem python:3.11-slim
|-- docker-compose.yml              # Orquestração da suíte de testes
|-- .dockerignore
|-- CONTEXT_RULES.md                # Regras de governança para a IA
|-- specs/
|   |-- system_design_document.pdf  # Especificação original (Fase 1)
|   |-- task_analyzer_spec.md       # Contrato SDD atualizado (Fase 2)
|   `-- requirements.yaml           # Requisitos estruturados
|-- tests/test_harness.py           # Test harness (pytest)
|-- src/task_analyzer.py            # Código gerado via IA e homologado
|-- requirements.txt
`-- README.md
```

Nota: o PDF da Fase 1 usa nomes provisórios de campos. O contrato vigente, com os nomes usados no código e nos testes (`data_criacao`, `data_conclusao`, `TaskValidationError`), está em `specs/task_analyzer_spec.md`.

## Como executar

### Localmente (Python 3.11+)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest tests/test_harness.py -v
```

### Com Docker

```bash
docker compose run --rm tests
```

Ou, passo a passo:

```bash
docker build -t sdd-taskanalyzer .
docker run --rm sdd-taskanalyzer
```

## Integração contínua (CI/CD)

O workflow `.github/workflows/ci.yml` roda a cada push e Pull Request nas branches `main` e `develop`, em `ubuntu-latest` com Python 3.11: instala as dependências do `requirements.txt` e executa `pytest tests/test_harness.py -v`. O selo no topo mostra o status do build na `main`.

## Governança de IA

- `CONTEXT_RULES.md` define as diretrizes e proibições que a IA deve seguir.
- `specs/task_analyzer_spec.md` é o contrato de negócio executável.
- Todo código gerado por IA passa por Pull Request e revisão humana antes do merge (Critical-in-the-Loop).

## Fluxo de trabalho Git

Branches `main` e `develop`, com branches de funcionalidade (`feature/*`) integradas por Pull Request e commits atômicos com mensagens descritivas.

## Status

Fase 3: CI/CD, containerização e governança.
