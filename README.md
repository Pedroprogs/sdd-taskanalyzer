# sdd-taskanalyzer

Módulo **TaskAnalyzer**: análise de tarefas e produtividade (tempo médio de conclusão, taxa de atraso e indicadores por prioridade), desenvolvido com **Spec-Driven Development (SDD)** e código gerado por IA, com homologação humana.

## Estrutura

- `CONTEXT_RULES.md`: regras de governança fornecidas à IA
- `specs/task_analyzer_spec.md`: contrato de negócio (SDD)
- `src/task_analyzer.py`: código-fonte (gerado via IA e homologado)
- `tests/test_harness.py`: testes automatizados (pytest)

## Como executar

Requisito: Python 3.11+

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

## Status

Fase 2: implementação com IA, test harness e versionamento no GitHub.