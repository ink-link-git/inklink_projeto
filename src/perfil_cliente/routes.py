from flask import Blueprint, jsonify, render_template, request, session

from perfil_cliente.forms import (
    atualizar_perfil,
    buscar_perfil,
    estatisticas,
    formatar_telefone,
    iniciais,
    validar_perfil,
)
from shared.auth import cliente_logado, cliente_required

# Tela "Meu Perfil" do cliente. O static_url_path próprio evita conflito com os outros módulos.
bp = Blueprint(
    "perfil_cliente",
    __name__,
    static_folder="static",
    static_url_path="/static/perfil_cliente",
)


@bp.route("/cliente/perfil")
@cliente_required
def perfil():
    """Dados da conta e resumo do cliente logado."""
    cliente = cliente_logado()
    erro = None

    try:
        dados = buscar_perfil(cliente["id"])
    except Exception as exc:
        print(">>> ERRO AO BUSCAR O PERFIL DO CLIENTE:", exc)
        dados = None

    if dados is None:
        # Sem acesso à tabela: mostra o que a sessão já sabe e avisa.
        nome = cliente.get("nome") or ""
        dados = {"nome": nome, "email": cliente.get("email") or "", "telefone": "",
                 "iniciais": iniciais(nome), "desde": None}
        erro = "Não foi possível carregar todos os dados do perfil agora."

    try:
        resumo = estatisticas(cliente["id"])
    except Exception as exc:
        print(">>> ERRO AO BUSCAR O RESUMO DO CLIENTE:", exc)
        resumo = None

    return render_template(
        "perfil_cliente/perfil.html",
        perfil=dados,
        resumo=resumo,
        erro=erro,
        ativo="perfil",
    )


# ==========================================
# ROTAS DA API
# ==========================================

@bp.route("/api/cliente/perfil", methods=["PATCH"])
@cliente_required
def api_atualizar_perfil():
    """Atualiza nome e telefone do cliente logado (nunca de outro cliente)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "errors": {"geral": "Requisição inválida."}}), 400

    nome = " ".join(str(data.get("nome") or "").split())  # tira espaços repetidos
    telefone = str(data.get("telefone") or "").strip()

    # --- 1. Validação de dados ---
    errors, tel_digits = validar_perfil(nome, telefone)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # --- 2. Salva na tabela 'cliente' ---
    cliente = cliente_logado()
    try:
        atualizar_perfil(cliente["id"], nome, tel_digits)
    except Exception as exc:
        print(">>> ERRO AO ATUALIZAR O PERFIL DO CLIENTE:", exc)
        return jsonify({"success": False, "errors": {"geral": "Não foi possível salvar as alterações."}}), 500

    # A barra lateral lê o nome da sessão, então ela também precisa ser atualizada.
    session["cliente"] = {**cliente, "nome": nome}

    return jsonify({
        "success": True,
        "message": "Perfil atualizado.",
        "perfil": {"nome": nome, "telefone": formatar_telefone(tel_digits), "iniciais": iniciais(nome)},
    }), 200
