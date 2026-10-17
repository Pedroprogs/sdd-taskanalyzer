# Especificação SDD: TaskAnalyzer

## 1. Propósito

O módulo analisa um conjunto de tarefas e retorna métricas de produtividade: totais, tempo médio de conclusão (geral e por prioridade) e taxa de atraso. É um módulo puro: sem persistência, sem interface gráfica e sem chamadas externas.

## 2. Contrato Executável de Interface

### Função pública

```python
def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]
```

### Exceção pública

`TaskValidationError(Exception)`: disparada para qualquer entrada inválida.

### Entrada: cada tarefa é um `dict` com os campos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | `str` | Sim | Identificador único da tarefa |
| `titulo` | `str` | Sim | Nome da tarefa |
| `prioridade` | `str` ("alta", "media", "baixa") | Sim | Prioridade da tarefa |
| `data_criacao` | `datetime` | Sim | Data/hora de criação |
| `data_conclusao` | `datetime \| None` | Sim | Data/hora de conclusão (`None` = pendente) |
| `data_limite` | `datetime` | Sim | Prazo da tarefa |

### Saída: `dict` com as chaves

| Chave | Tipo | Descrição |
|---|---|---|
| `total_tarefas` | `int` | Quantidade total de tarefas recebidas |
| `total_concluidas` | `int` | Tarefas com `data_conclusao` preenchida |
| `total_pendentes` | `int` | Tarefas com `data_conclusao` igual a `None` |
| `tempo_medio_conclusao_horas` | `dict` | `{"geral": float, "por_prioridade": {"alta": float, "media": float, "baixa": float}}` |
| `taxa_atraso_percentual` | `float` | Percentual (0 a 100) de tarefas concluídas após `data_limite` |

### Regras de negócio

- Tempo de conclusão = `data_conclusao - data_criacao`, em horas.
- Apenas tarefas concluídas entram nas médias e na taxa de atraso.
- Tarefa atrasada = concluída com `data_conclusao > data_limite`.
- `taxa_atraso_percentual` = atrasadas / concluídas x 100.
- Valores numéricos são arredondados em 2 casas decimais.
- Lista vazia ou sem tarefas concluídas: médias e taxa retornam `0.0`, sem exceção.
- Prioridade sem tarefas concluídas retorna `0.0`.
- `data_conclusao < data_criacao` dispara `TaskValidationError`.
- Prioridade fora do domínio, campo ausente ou tipo incorreto dispara `TaskValidationError`.

## 3. Cenários de Aceite (Dado-Quando-Então)

**Cenário 1 (Sucesso):** Dado um conjunto de tarefas válidas, quando `analyze_tasks` for executada, então deve retornar corretamente `total_tarefas`, `total_concluidas`, `total_pendentes`, `tempo_medio_conclusao_horas` (geral e por prioridade) e `taxa_atraso_percentual`.

**Cenário 2 (Exceção/Erro):** Dado uma entrada com `data_conclusao < data_criacao`, quando `analyze_tasks` for executada, então deve disparar `TaskValidationError`.

**Caso de borda:** Dado uma lista vazia ou apenas tarefas pendentes, quando `analyze_tasks` for executada, então deve retornar `0.0` nas médias e na taxa de atraso, sem lançar exceções.

## 4. Planejamento do Test Harness

Os cenários acima são traduzidos em testes `pytest` em `tests/test_harness.py`. O código gerado por IA só é aceito se todos os testes passarem e após revisão humana contra o `CONTEXT_RULES.md`.
