import os
import uuid

from flask import Blueprint, jsonify, render_template, request, session
from werkzeug.utils import secure_filename

from login_cliente.db import supabase  # usado para enviar a foto ao Storage
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
                 "avatar_url": cliente.get("avatar_url") or "",
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

@bp.route("/api/cliente/perfil", methods=["PATCH", "POST"])
@cliente_required
def api_atualizar_perfil():
    """Atualiza nome, telefone e foto de perfil do cliente logado (nunca de outro cliente)."""
    # Como podemos receber um arquivo de imagem junto com o texto, usamos request.form e request.files
    nome = " ".join(str(request.form.get("nome") or "").split())  # tira espaços repetidos
    telefone = str(request.form.get("telefone") or "").strip()

    # --- 1. Validação de dados ---
    errors, tel_digits = validar_perfil(nome, telefone)
    foto = request.files.get("foto_perfil")
    if foto and foto.filename and os.path.splitext(foto.filename)[1].lower() not in (".jpg", ".jpeg", ".png"):
        errors["foto_perfil"] = "Apenas imagens nos formatos JPG, JPEG ou PNG são permitidas."
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    cliente = cliente_logado()
    id_cliente = cliente["id"]

    try:
        # --- 2. Trata o upload da nova foto de perfil (se houver) ---
        avatar_url = None

        if foto and foto.filename != "":
            extensao = os.path.splitext(secure_filename(foto.filename))[1]
            nome_arquivo = f"{id_cliente}_{uuid.uuid4().hex[:8]}{extensao}"

            # Envia para o bucket 'avatars' no Supabase (o mesmo do tatuador)
            supabase.storage.from_("avatars").upload(
                path=nome_arquivo,
                file=foto.read(),
                file_options={"content-type": foto.content_type, "upsert": "true"},
            )

            # Pega a URL pública gerada
            avatar_url = supabase.storage.from_("avatars").get_public_url(nome_arquivo)

        # --- 3. Salva na tabela 'cliente' ---
        # Se uma nova foto foi enviada, atualiza a coluna. Se não, preserva a que já estava.
        atualizar_perfil(id_cliente, nome, tel_digits, avatar_url)

        if not avatar_url:
            avatar_url = cliente.get("avatar_url") or ""

    except Exception as exc:
        print(">>> ERRO AO ATUALIZAR O PERFIL DO CLIENTE:", exc)
        return jsonify({"success": False, "errors": {"geral": "Não foi possível salvar as alterações."}}), 500

    # A barra lateral lê nome e foto da sessão, então ela também precisa ser atualizada.
    session["cliente"] = {**cliente, "nome": nome, "avatar_url": avatar_url}

    return jsonify({
        "success": True,
        "message": "Perfil atualizado.",
        "perfil": {
            "nome": nome,
            "telefone": formatar_telefone(tel_digits),
            "avatar_url": avatar_url,
            "iniciais": iniciais(nome),
        },
    }), 200
