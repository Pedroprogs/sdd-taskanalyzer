"""Test Harness do TaskAnalyzer (pytest).

Traduz os cenários de aceite da especificação SDD em testes automatizados:
Cenário 1 (sucesso), Cenário 2 (exceção) e casos de borda.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402

BASE: datetime = datetime(2026, 1, 1, 8, 0)


def make_task(
    task_id: str = "t1",
    prioridade: str = "alta",
    horas_ate_conclusao: float | None = 1.0,
    horas_ate_limite: float = 24.0,
) -> dict[str, Any]:
    """Cria uma tarefa válida para uso nos testes.

    Args:
        task_id: Identificador da tarefa.
        prioridade: Prioridade da tarefa ("alta", "media" ou "baixa").
        horas_ate_conclusao: Horas entre criação e conclusão, ou None
            para uma tarefa pendente.
        horas_ate_limite: Horas entre a criação e o prazo.

    Returns:
        Dicionário no formato esperado por analyze_tasks.
    """
    conclusao = (
        None
        if horas_ate_conclusao is None
        else BASE + timedelta(hours=horas_ate_conclusao)
    )
    return {
        "id": task_id,
        "titulo": f"Tarefa {task_id}",
        "prioridade": prioridade,
        "data_criacao": BASE,
        "data_conclusao": conclusao,
        "data_limite": BASE + timedelta(hours=horas_ate_limite),
    }


@pytest.fixture
def tarefas_validas() -> list[dict[str, Any]]:
    """Conjunto válido: 4 concluídas (2 atrasadas) e 2 pendentes."""
    return [
        make_task("t1", "alta", 10, 12),
        make_task("t2", "alta", 30, 24),
        make_task("t3", "media", 6, 8),
        make_task("t4", "baixa", 4, 2),
        make_task("t5", "media", None, 8),
        make_task("t6", "baixa", None, 8),
    ]


# ---------------------------------------------------------------------------
# Cenário 1: Sucesso
# ---------------------------------------------------------------------------


def test_cenario1_totais(tarefas_validas: list[dict[str, Any]]) -> None:
    """Valida total_tarefas, total_concluidas e total_pendentes."""
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["total_tarefas"] == 6
    assert resultado["total_concluidas"] == 4
    assert resultado["total_pendentes"] == 2


def test_cenario1_tempo_medio_geral(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """Valida o tempo médio geral de conclusão: (10+30+6+4)/4 = 12.5."""
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["tempo_medio_conclusao_horas"]["geral"] == 12.5


def test_cenario1_tempo_medio_por_prioridade(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """Valida o tempo médio de conclusão por prioridade."""
    resultado = analyze_tasks(tarefas_validas)
    por_prioridade = resultado["tempo_medio_conclusao_horas"]["por_prioridade"]
    assert por_prioridade == {"alta": 20.0, "media": 6.0, "baixa": 4.0}


def test_cenario1_taxa_atraso(tarefas_validas: list[dict[str, Any]]) -> None:
    """Valida a taxa de atraso: 2 atrasadas de 4 concluídas = 50%."""
    resultado = analyze_tasks(tarefas_validas)
    assert resultado["taxa_atraso_percentual"] == 50.0


def test_cenario1_estrutura_da_saida(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """Valida as chaves retornadas conforme o contrato."""
    resultado = analyze_tasks(tarefas_validas)
    assert set(resultado) == {
        "total_tarefas",
        "total_concluidas",
        "total_pendentes",
        "tempo_medio_conclusao_horas",
        "taxa_atraso_percentual",
    }
    assert set(resultado["tempo_medio_conclusao_horas"]) == {
        "geral",
        "por_prioridade",
    }


def test_conclusao_no_prazo_exato_nao_e_atraso() -> None:
    """Conclusão exatamente na data limite não conta como atraso."""
    resultado = analyze_tasks([make_task("t1", "alta", 5, 5)])
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_arredondamento_em_duas_casas() -> None:
    """Valores são arredondados em 2 casas: 10 min = 0.17 h; 1/3 = 33.33%."""
    tarefas = [
        make_task("t1", "alta", 10 / 60, 24),
        make_task("t2", "alta", 10 / 60, 24),
        make_task("t3", "alta", 10 / 60, 0),
    ]
    resultado = analyze_tasks(tarefas)
    assert resultado["tempo_medio_conclusao_horas"]["geral"] == 0.17
    assert resultado["taxa_atraso_percentual"] == 33.33


# ---------------------------------------------------------------------------
# Cenário 2: Exceção/Erro
# ---------------------------------------------------------------------------


def test_cenario2_conclusao_anterior_a_criacao() -> None:
    """data_conclusao < data_criacao dispara TaskValidationError."""
    tarefa = make_task("t1", "alta", -2, 24)
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


def test_tarefa_invalida_no_meio_da_lista_dispara_erro(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """Uma tarefa inválida em meio a tarefas válidas invalida a análise."""
    tarefas_validas.append(make_task("t7", "alta", -1, 24))
    with pytest.raises(TaskValidationError):
        analyze_tasks(tarefas_validas)


def test_prioridade_fora_do_dominio() -> None:
    """Prioridade fora de alta/media/baixa dispara TaskValidationError."""
    with pytest.raises(TaskValidationError):
        analyze_tasks([make_task("t1", "urgente", 1, 24)])


@pytest.mark.parametrize(
    "campo",
    [
        "id",
        "titulo",
        "prioridade",
        "data_criacao",
        "data_conclusao",
        "data_limite",
    ],
)
def test_campo_obrigatorio_ausente(campo: str) -> None:
    """A ausência de qualquer campo obrigatório dispara erro."""
    tarefa = make_task()
    del tarefa[campo]
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("id", 123),
        ("titulo", None),
        ("data_criacao", "2026-01-01"),
        ("data_limite", 10),
        ("data_conclusao", "2026-01-02"),
    ],
)
def test_tipo_incorreto(campo: str, valor: Any) -> None:
    """Campos com tipo incorreto disparam TaskValidationError."""
    tarefa = make_task()
    tarefa[campo] = valor
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


@pytest.mark.parametrize("entrada", [None, "tarefas", {"id": "t1"}, 42])
def test_entrada_que_nao_e_lista(entrada: Any) -> None:
    """Entrada que não seja uma lista dispara TaskValidationError."""
    with pytest.raises(TaskValidationError):
        analyze_tasks(entrada)


def test_item_que_nao_e_dict() -> None:
    """Item da lista que não seja dict dispara TaskValidationError."""
    with pytest.raises(TaskValidationError):
        analyze_tasks(["não é um dict"])


def test_mistura_de_datas_com_e_sem_fuso() -> None:
    """Datas com e sem fuso horário na mesma tarefa disparam erro."""
    tarefa = make_task()
    tarefa["data_limite"] = datetime(2026, 1, 2, tzinfo=timezone.utc)
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


# ---------------------------------------------------------------------------
# Casos de borda: sem exceções não tratadas e médias em 0.0
# ---------------------------------------------------------------------------


def _assert_metricas_zeradas(resultado: dict[str, Any]) -> None:
    """Verifica que médias e taxa de atraso retornaram 0.0."""
    medias = resultado["tempo_medio_conclusao_horas"]
    assert medias["geral"] == 0.0
    assert medias["por_prioridade"] == {"alta": 0.0, "media": 0.0, "baixa": 0.0}
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_borda_lista_vazia() -> None:
    """Lista vazia retorna totais zerados e métricas em 0.0."""
    resultado = analyze_tasks([])
    assert resultado["total_tarefas"] == 0
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 0
    _assert_metricas_zeradas(resultado)


def test_borda_apenas_tarefas_pendentes() -> None:
    """Somente tarefas pendentes: métricas em 0.0, sem exceção."""
    tarefas = [
        make_task("t1", "alta", None),
        make_task("t2", "media", None),
    ]
    resultado = analyze_tasks(tarefas)
    assert resultado["total_tarefas"] == 2
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 2
    _assert_metricas_zeradas(resultado)


def test_borda_prioridade_sem_tarefas_concluidas() -> None:
    """Prioridade sem tarefas concluídas retorna 0.0 na sua média."""
    tarefas = [make_task("t1", "alta", 8, 24), make_task("t2", "baixa", None)]
    resultado = analyze_tasks(tarefas)
    por_prioridade = resultado["tempo_medio_conclusao_horas"]["por_prioridade"]
    assert por_prioridade == {"alta": 8.0, "media": 0.0, "baixa": 0.0}