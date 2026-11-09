from flask import Blueprint, abort, jsonify, render_template, request, url_for

from gestao_anamnese.forms import (
    PERGUNTAS,
    agendamentos_sem_ficha,
    alertas_da_ficha,
    buscar_ficha_do_tatuador,
    listar_fichas_do_tatuador,
    respostas_da_ficha,
    salvar_ficha,
    validar_ficha,
)
from shared.auth import cliente_logado, cliente_required, tatuador_logado, tatuador_required

# Blueprint do módulo. O static_url_path próprio evita conflito com os outros módulos.
bp = Blueprint(
    "gestao_anamnese",
    __name__,
    static_folder="static",
    static_url_path="/static/gestao_anamnese",
)


# ==========================================
# CLIENTE: preenche a ficha
# ==========================================

@bp.route("/cliente/anamnese")
@cliente_required
def ficha_cliente():
    """Formulário da ficha de anamnese (?agendamento=<id> já deixa a sessão escolhida)."""
    try:
        pendentes = agendamentos_sem_ficha(cliente_logado()["id"])
        erro = None
    except Exception as exc:
        print(">>> ERRO AO LISTAR AGENDAMENTOS SEM FICHA:", exc)
        pendentes, erro = [], "Não foi possível carregar seus agendamentos agora."

    escolhido = request.args.get("agendamento", type=int)
    if escolhido not in {a["id"] for a in pendentes}:
        escolhido = pendentes[0]["id"] if len(pendentes) == 1 else None

    return render_template(
        "gestao_anamnese/ficha_cliente.html",
        pendentes=pendentes,
        escolhido=escolhido,
        perguntas=PERGUNTAS,
        erro=erro,
    )


@bp.route("/api/anamnese", methods=["POST"])
@cliente_required
def api_salvar_ficha():
    data = request.get_json(silent=True) or {}

    try:
        id_agendamento = int(data.get("agendamento"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "errors": {"agendamento": "Escolha o agendamento."}}), 400

    errors, dados = validar_ficha(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        ok, mensagem, status = salvar_ficha(cliente_logado()["id"], id_agendamento, dados)
    except Exception as exc:
        print(">>> ERRO AO SALVAR FICHA:", exc)
        return jsonify({"success": False, "errors": {"geral": "Não foi possível salvar a ficha."}}), 500

    if not ok:
        return jsonify({"success": False, "errors": {"geral": mensagem}}), status
    return jsonify({
        "success": True,
        "mensagem": mensagem,
        "redirect": url_for("login_cliente.home_cliente"),
    }), status


# ==========================================
# TATUADOR: consulta as fichas
# ==========================================

@bp.route("/tatuador/anamnese")
@tatuador_required
def fichas_tatuador():
    tatuador = tatuador_logado()
    try:
        sessoes = listar_fichas_do_tatuador(tatuador["id"])
        erro = None
    except Exception as exc:
        print(">>> ERRO AO LISTAR FICHAS:", exc)
        sessoes, erro = [], "Não foi possível carregar as fichas agora."

    return render_template(
        "gestao_anamnese/fichas_tatuador.html",
        tatuador=tatuador,
        sessoes=sessoes,
        erro=erro,
        ativo="anamnese",
    )


@bp.route("/tatuador/anamnese/<int:id_agendamento>")
@tatuador_required
def ficha_do_agendamento(id_agendamento):
    tatuador = tatuador_logado()
    try:
        resultado = buscar_ficha_do_tatuador(tatuador["id"], id_agendamento)
    except Exception as exc:
        print(">>> ERRO AO BUSCAR FICHA:", exc)
        abort(500)

    # Agendamento de outro tatuador (ou inexistente) é tratado como inexistente.
    if not resultado:
        abort(404)

    agendamento, cliente, ficha = resultado
    return render_template(
        "gestao_anamnese/ficha_detalhe.html",
        tatuador=tatuador,
        agendamento=agendamento,
        cliente=cliente,
        ficha=ficha,
        respostas=respostas_da_ficha(ficha) if ficha else [],
        alertas=alertas_da_ficha(ficha) if ficha else [],
        ativo="anamnese",
    )
