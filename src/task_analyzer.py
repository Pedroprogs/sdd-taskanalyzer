"""Módulo TaskAnalyzer.

Analisa um conjunto de tarefas e calcula métricas de produtividade:
totais, tempo médio de conclusão (geral e por prioridade) e taxa de atraso.
O módulo é puro: não persiste dados nem realiza chamadas externas.
"""

import logging
from datetime import datetime
from typing import Any, NoReturn

logger = logging.getLogger(__name__)

PRIORIDADES_VALIDAS: tuple[str, ...] = ("alta", "media", "baixa")
CAMPOS_TEXTO: tuple[str, ...] = ("id", "titulo", "prioridade")
CAMPOS_DATA_OBRIGATORIOS: tuple[str, ...] = ("data_criacao", "data_limite")
CAMPO_CONCLUSAO: str = "data_conclusao"
SEGUNDOS_POR_HORA: float = 3600.0
CASAS_DECIMAIS: int = 2


class TaskValidationError(Exception):
    """Erro disparado quando a entrada de tarefas é inválida."""


def _raise_validation_error(message: str) -> NoReturn:
    """Registra o erro em log e dispara TaskValidationError.

    Args:
        message: Mensagem descritiva do problema encontrado.

    Raises:
        TaskValidationError: Sempre.
    """
    logger.error(message)
    raise TaskValidationError(message)


def _validate_required_fields(task: dict[str, Any], index: int) -> None:
    """Verifica se todos os campos obrigatórios estão presentes.

    Args:
        task: Tarefa a ser validada.
        index: Posição da tarefa na lista de entrada.

    Raises:
        TaskValidationError: Se algum campo obrigatório estiver ausente.
    """
    campos = (*CAMPOS_TEXTO, *CAMPOS_DATA_OBRIGATORIOS, CAMPO_CONCLUSAO)
    for campo in campos:
        if campo not in task:
            _raise_validation_error(
                f"Tarefa {index}: campo obrigatório ausente: '{campo}'."
            )


def _validate_field_types(task: dict[str, Any], index: int) -> None:
    """Verifica se os campos possuem os tipos esperados.

    Args:
        task: Tarefa a ser validada.
        index: Posição da tarefa na lista de entrada.

    Raises:
        TaskValidationError: Se algum campo tiver tipo incorreto.
    """
    for campo in CAMPOS_TEXTO:
        if not isinstance(task[campo], str):
            _raise_validation_error(
                f"Tarefa {index}: o campo '{campo}' deve ser str."
            )
    for campo in CAMPOS_DATA_OBRIGATORIOS:
        if not isinstance(task[campo], datetime):
            _raise_validation_error(
                f"Tarefa {index}: o campo '{campo}' deve ser datetime."
            )
    conclusao = task[CAMPO_CONCLUSAO]
    if conclusao is not None and not isinstance(conclusao, datetime):
        _raise_validation_error(
            f"Tarefa {index}: o campo '{CAMPO_CONCLUSAO}' deve ser "
            "datetime ou None."
        )


def _validate_priority(task: dict[str, Any], index: int) -> None:
    """Verifica se a prioridade pertence ao domínio permitido.

    Args:
        task: Tarefa a ser validada.
        index: Posição da tarefa na lista de entrada.

    Raises:
        TaskValidationError: Se a prioridade estiver fora do domínio.
    """
    if task["prioridade"] not in PRIORIDADES_VALIDAS:
        _raise_validation_error(
            f"Tarefa {index}: prioridade inválida '{task['prioridade']}'. "
            f"Valores aceitos: {', '.join(PRIORIDADES_VALIDAS)}."
        )


def _validate_timezone_consistency(task: dict[str, Any], index: int) -> None:
    """Verifica se as datas da tarefa são todas com fuso ou todas sem fuso.

    Args:
        task: Tarefa a ser validada.
        index: Posição da tarefa na lista de entrada.

    Raises:
        TaskValidationError: Se houver mistura de datas com e sem fuso.
    """
    datas = [task[campo] for campo in CAMPOS_DATA_OBRIGATORIOS]
    if task[CAMPO_CONCLUSAO] is not None:
        datas.append(task[CAMPO_CONCLUSAO])
    possui_fuso = {data.utcoffset() is not None for data in datas}
    if len(possui_fuso) > 1:
        _raise_validation_error(
            f"Tarefa {index}: datas com e sem fuso horário não podem "
            "ser misturadas."
        )


def _validate_date_order(task: dict[str, Any], index: int) -> None:
    """Verifica se a conclusão não é anterior à criação.

    Args:
        task: Tarefa a ser validada.
        index: Posição da tarefa na lista de entrada.

    Raises:
        TaskValidationError: Se data_conclusao < data_criacao.
    """
    conclusao = task[CAMPO_CONCLUSAO]
    if conclusao is not None and conclusao < task["data_criacao"]:
        _raise_validation_error(
            f"Tarefa {index}: data_conclusao anterior a data_criacao."
        )


def _validate_task(task: Any, index: int) -> None:
    """Executa todas as validações de uma tarefa.

    Args:
        task: Tarefa a ser validada.
        index: Posição da tarefa na lista de entrada.

    Raises:
        TaskValidationError: Se a tarefa for inválida.
    """
    if not isinstance(task, dict):
        _raise_validation_error(f"Tarefa {index}: deve ser um dict.")
    _validate_required_fields(task, index)
    _validate_field_types(task, index)
    _validate_priority(task, index)
    _validate_timezone_consistency(task, index)
    _validate_date_order(task, index)


def _completion_hours(task: dict[str, Any]) -> float:
    """Calcula o tempo de conclusão de uma tarefa concluída, em horas.

    Args:
        task: Tarefa concluída e válida.

    Returns:
        Tempo entre criação e conclusão, em horas.
    """
    delta = task[CAMPO_CONCLUSAO] - task["data_criacao"]
    return delta.total_seconds() / SEGUNDOS_POR_HORA


def _is_late(task: dict[str, Any]) -> bool:
    """Indica se uma tarefa concluída foi entregue após o prazo.

    Args:
        task: Tarefa concluída e válida.

    Returns:
        True se data_conclusao for posterior a data_limite.
    """
    return task[CAMPO_CONCLUSAO] > task["data_limite"]


def _average(values: list[float]) -> float:
    """Calcula a média arredondada, retornando 0.0 para lista vazia.

    Args:
        values: Valores numéricos a serem usados no calculo da media.

    Returns:
        Média arredondada em duas casas decimais, ou 0.0 sem valores.
    """
    if not values:
        return 0.0
    return round(sum(values) / len(values), CASAS_DECIMAIS)


def _late_rate_percent(completed: list[dict[str, Any]]) -> float:
    """Calcula o percentual de tarefas concluídas com atraso.

    Args:
        completed: Tarefas concluídas e válidas.

    Returns:
        Percentual de 0 a 100 arredondado em duas casas, ou 0.0 sem
        tarefas concluídas.
    """
    if not completed:
        return 0.0
    atrasadas = sum(1 for task in completed if _is_late(task))
    return round(atrasadas / len(completed) * 100, CASAS_DECIMAIS)


def _average_hours_by_priority(
    completed: list[dict[str, Any]],
) -> dict[str, float]:
    """Calcula o tempo médio de conclusão para cada prioridade.

    Args:
        completed: Tarefas concluídas e válidas.

    Returns:
        Dicionário com a média em horas de cada prioridade válida.
    """
    return {
        prioridade: _average(
            [
                _completion_hours(task)
                for task in completed
                if task["prioridade"] == prioridade
            ]
        )
        for prioridade in PRIORIDADES_VALIDAS
    }


def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Analisa tarefas e retorna métricas de produtividade.

    Args:
        tasks: Lista de tarefas. Cada tarefa é um dict com os campos
            id, titulo, prioridade, data_criacao, data_conclusao e
            data_limite.

    Returns:
        Dicionário com total_tarefas, total_concluidas, total_pendentes,
        tempo_medio_conclusao_horas (geral e por prioridade) e
        taxa_atraso_percentual.

    Raises:
        TaskValidationError: Se a entrada ou alguma tarefa for inválida.
    """
    if not isinstance(tasks, list):
        _raise_validation_error("A entrada deve ser uma lista de tarefas.")

    logger.info("Iniciando análise de %d tarefa(s).", len(tasks))
    for index, task in enumerate(tasks):
        _validate_task(task, index)

    completed = [task for task in tasks if task[CAMPO_CONCLUSAO] is not None]
    horas = [_completion_hours(task) for task in completed]

    resultado: dict[str, Any] = {
        "total_tarefas": len(tasks),
        "total_concluidas": len(completed),
        "total_pendentes": len(tasks) - len(completed),
        "tempo_medio_conclusao_horas": {
            "geral": _average(horas),
            "por_prioridade": _average_hours_by_priority(completed),
        },
        "taxa_atraso_percentual": _late_rate_percent(completed),
    }
    logger.info("Análise concluída: %s", resultado)
    return resultado