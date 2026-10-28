from flask import Blueprint, current_app, jsonify, render_template, request, url_for

from agendamento_cliente.forms import (
    cancelar_do_cliente,
    buscar_tatuador,
    criar_agendamento,
    enviar_referencias,
    listar_do_cliente,
    listar_tatuadores,
    validar_agendamento,
)
from shared.auth import cliente_logado, cliente_required

# Blueprint do módulo. O static_url_path próprio evita conflito com os outros módulos.
bp = Blueprint(
    "agendamento_cliente",
    __name__,
    static_folder="static",
    static_url_path="/static/agendamento_cliente",
)


@bp.route("/cliente/agendar")
@cliente_required
def agendar_sessao():
    """Tela de agendamento de sessão do cliente."""
    try:
        tatuadores = listar_tatuadores()
    except Exception as exc:
        print(">>> ERRO AO LISTAR TATUADORES:", exc)
        tatuadores = []
    return render_template("agendamento_cliente/agendar.html", tatuadores=tatuadores)


# ==========================================
# ROTAS DA API
# ==========================================

@bp.route("/api/agendamentos", methods=["POST"])
@cliente_required
def api_criar_agendamento():
    """Recebe o pedido de agendamento (multipart, por causa das imagens), valida e salva."""
    cliente = cliente_logado()
    form = request.form

    id_tatuador = (form.get("tatuador") or "").strip()
    periodo = (form.get("periodo") or "").strip()
    cor_pele = (form.get("pele") or "").strip()
    descricao = (form.get("descricao") or "").strip()
    anamnese_ciente = form.get("anamnese") == "on"
    arquivos = [a for a in request.files.getlist("imagens") if a and a.filename]

    # --- 1. Validação de dados ---
    errors, dia = validar_agendamento(
        id_tatuador, form.get("data"), periodo, cor_pele, descricao, anamnese_ciente, arquivos
    )
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # --- 2. O tatuador precisa existir ---
    try:
        tatuador = buscar_tatuador(id_tatuador)
    except Exception as exc:
        print(">>> ERRO AO BUSCAR TATUADOR:", exc)
        return jsonify({"success": False, "errors": {"geral": "Não foi possível concluir o agendamento."}}), 500
    if not tatuador:
        return jsonify({"success": False, "errors": {"tatuador": "Tatuador não encontrado."}}), 400

    # --- 3. Salva o agendamento e as referências ---
    try:
        agendamento = criar_agendamento(cliente["id"], tatuador, dia, periodo, cor_pele, descricao)
    except ValueError as exc:
        return jsonify({"success": False, "errors": {"data": str(exc)}}), 409
    except Exception as exc:
        print(">>> ERRO AO CRIAR AGENDAMENTO:", exc)
        return jsonify({"success": False, "errors": {"geral": "Não foi possível concluir o agendamento."}}), 500

    aviso = None
    try:
        enviar_referencias(agendamento["id"], cliente["id"], arquivos)
    except Exception as exc:
        print(">>> ERRO AO ENVIAR REFERÊNCIAS:", exc)
        aviso = "O agendamento foi feito, mas as imagens de referência não puderam ser enviadas."

    return jsonify({
        "success": True,
        "mensagem": "Pedido enviado! O tatuador vai avaliar e definir o horário da sua sessão.",
        "aviso": aviso,
        # Sem o módulo de anamnese, volta para a home do cliente.
        "anamnese_url": (
            url_for("gestao_anamnese.ficha_cliente", agendamento=agendamento["id"])
            if "gestao_anamnese.ficha_cliente" in current_app.view_functions
            else url_for("login_cliente.home_cliente")
        ),
    }), 201


@bp.route("/api/cliente/agendamentos", methods=["GET"])
@cliente_required
def api_agendamentos_cliente():
    """Agendamentos do cliente logado (nunca de outro cliente)."""
    try:
        return jsonify({"success": True, "agendamentos": listar_do_cliente(cliente_logado()["id"])}), 200
    except Exception as exc:
        print(">>> ERRO AO LISTAR AGENDAMENTOS DO CLIENTE:", exc)
        return jsonify({"success": False, "errors": {"geral": "Não foi possível carregar seus agendamentos."}}), 500


@bp.route("/api/agendamentos/<int:id_agendamento>/cancelar", methods=["PATCH"])
@cliente_required
def api_cancelar_agendamento(id_agendamento):
    try:
        ok, mensagem = cancelar_do_cliente(cliente_logado()["id"], id_agendamento)
    except Exception as exc:
        print(">>> ERRO AO CANCELAR AGENDAMENTO:", exc)
        return jsonify({"success": False, "errors": {"geral": "Erro ao cancelar o agendamento."}}), 500

    if not ok:
        return jsonify({"success": False, "errors": {"geral": mensagem}}), 400
    return jsonify({"success": True, "mensagem": mensagem}), 200
