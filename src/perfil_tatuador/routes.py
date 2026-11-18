from flask import Blueprint, jsonify, render_template, request, session

from perfil_tatuador.forms import (
    atualizar_perfil,
    buscar_perfil,
    estatisticas,
    formatar_telefone,
    iniciais,
    validar_perfil,
)
from shared.auth import tatuador_logado, tatuador_required

# Tela "Meu Perfil" do tatuador. O static_url_path próprio evita conflito com os outros módulos.
bp = Blueprint(
    "perfil_tatuador",
    __name__,
    static_folder="static",
    static_url_path="/static/perfil_tatuador",
)


@bp.route("/tatuador/perfil")
@tatuador_required
def perfil():
    """Dados da conta e resumo do tatuador logado."""
    tatuador = tatuador_logado()
    erro = None

    try:
        dados = buscar_perfil(tatuador["id"])
    except Exception as exc:
        print(">>> ERRO AO BUSCAR O PERFIL DO TATUADOR:", exc)
        dados = None

    if dados is None:
        # Sem acesso à tabela: mostra o que a sessão já sabe e avisa.
        nome = tatuador.get("nome") or ""
        dados = {
            "nome": nome,
            "email": tatuador.get("email") or "",
            "telefone": "",
            "iniciais": iniciais(nome),
            "desde": None,
        }
        erro = "Não foi possível carregar todos os dados do perfil agora."

    try:
        resumo = estatisticas(tatuador["id"])
    except Exception as exc:
        print(">>> ERRO AO BUSCAR O RESUMO DO TATUADOR:", exc)
        resumo = None

    return render_template(
        "perfil_tatuador/perfil.html",
        perfil=dados,
        resumo=resumo,
        erro=erro,
        ativo="perfil",
    )


# ==========================================
# ROTAS DA API
# ==========================================

@bp.route("/api/tatuador/perfil", methods=["PATCH"])
@tatuador_required
def api_atualizar_perfil():
    """Atualiza nome e telefone (coluna 'tel') do tatuador logado."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "errors": {"geral": "Requisição inválida."}}), 400

    nome = " ".join(str(data.get("nome") or "").split())  # tira espaços repetidos
    telefone = str(data.get("telefone") or "").strip()

    # --- 1. Validação de dados ---
    errors, tel_digits = validar_perfil(nome, telefone)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # --- 2. Salva na tabela 'tatuador' ---
    tatuador = tatuador_logado()
    try:
        atualizar_perfil(tatuador["id"], nome, tel_digits)
    except Exception as exc:
        print(">>> ERRO AO ATUALIZAR O PERFIL DO TATUADOR:", exc)
        return jsonify({"success": False, "errors": {"geral": "Não foi possível salvar as alterações."}}), 500

    # A barra lateral lê o nome da sessão, então ela também precisa ser atualizada.
    session["tatuador"] = {**tatuador, "nome": nome}

    return jsonify({
        "success": True,
        "message": "Perfil atualizado.",
        "perfil": {
            "nome": nome,
            "telefone": formatar_telefone(tel_digits),
            "iniciais": iniciais(nome),
        },
    }), 200