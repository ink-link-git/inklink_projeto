from flask import Blueprint, flash, redirect, render_template, request, url_for

from agendamento_tatuador.forms import (
    DURACAO_PADRAO,
    DURACOES,
    alterar_status,
    definir_horario,
    listar_agendamentos,
    sessoes_confirmadas,
)
from shared.auth import tatuador_logado, tatuador_required

# Blueprint do módulo. O static_url_path próprio evita conflito com os outros módulos.
agenda_bp = Blueprint(
    "agendamento_tatuador",
    __name__,
    static_folder="static",
    static_url_path="/static/agendamento_tatuador",
)


@agenda_bp.route("/tatuador/agenda")
@tatuador_required
def minha_agenda():
    tatuador = tatuador_logado()
    try:
        agendamentos = listar_agendamentos(tatuador["id"])
        erro = None
    except Exception as exc:
        print(">>> ERRO AO LISTAR AGENDA:", exc)
        agendamentos, erro = [], "Não foi possível carregar a agenda agora. Tente novamente."

    pedidos = [a for a in agendamentos if a["status"] == "PENDENTE"]
    marcados = [a for a in agendamentos if a["status"] != "PENDENTE"]

    return render_template(
        "agendamento_tatuador/agenda.html",
        tatuador=tatuador,
        pedidos=pedidos,
        marcados=marcados,
        confirmadas=sessoes_confirmadas(agendamentos),
        duracoes=DURACOES,
        duracao_padrao=DURACAO_PADRAO,
        erro=erro,
        ativo="agenda",
    )


def _mudar_status(id_agendamento, novo_status):
    try:
        ok, mensagem = alterar_status(tatuador_logado()["id"], id_agendamento, novo_status)
    except Exception as exc:
        print(">>> ERRO AO ALTERAR STATUS:", exc)
        ok, mensagem = False, "Erro ao atualizar o agendamento."
    flash(mensagem, "success" if ok else "danger")
    return redirect(url_for("agendamento_tatuador.minha_agenda"))


@agenda_bp.route("/tatuador/agenda/<int:id_agendamento>/cancelar", methods=["POST"])
@tatuador_required
def cancelar(id_agendamento):
    return _mudar_status(id_agendamento, "CANCELADO")


@agenda_bp.route("/tatuador/agenda/<int:id_agendamento>/realizado", methods=["POST"])
@tatuador_required
def realizado(id_agendamento):
    return _mudar_status(id_agendamento, "REALIZADO")


@agenda_bp.route("/tatuador/agenda/<int:id_agendamento>/definir-horario", methods=["POST"])
@tatuador_required
def definir_horario_sessao(id_agendamento):
    """Aceita um pedido ou reagenda uma sessão: o tatuador escolhe dia, hora e duração."""
    try:
        ok, mensagem = definir_horario(
            tatuador_logado()["id"],
            id_agendamento,
            request.form.get("dia"),
            request.form.get("hora"),
            request.form.get("duracao_min"),
        )
    except Exception as exc:
        print(">>> ERRO AO DEFINIR HORÁRIO:", exc)
        ok, mensagem = False, "Erro ao salvar o horário da sessão."
    flash(mensagem, "success" if ok else "danger")
    return redirect(url_for("agendamento_tatuador.minha_agenda"))
