import os
import uuid
from flask import Blueprint, jsonify, render_template, request, session
from werkzeug.utils import secure_filename

from perfil_tatuador.forms import (
    atualizar_perfil,
    buscar_perfil,
    estatisticas,
    formatar_telefone,
    iniciais,
    validar_perfil,
)
from shared.auth import tatuador_logado, tatuador_required
from Cadastro_tatuador.db import supabase  # Importação do supabase para o Storage, se necessário

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
            "endereco": "",
            "avatar_url": tatuador.get("avatar_url") or "",
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

@bp.route("/api/tatuador/perfil", methods=["PATCH", "POST"])
@tatuador_required
def api_atualizar_perfil():
    """Atualiza nome, telefone, endereço e foto de perfil do tatuador logado."""
    
    # Como podemos receber arquivos de imagem junto com texto, usamos request.form e request.files
    nome = " ".join(str(request.form.get("nome") or "").split())
    telefone = str(request.form.get("telefone") or "").strip()
    endereco = str(request.form.get("endereco") or "").strip()

    # --- 1. Validação de dados ---
    errors, tel_digits = validar_perfil(nome, telefone)
    if errors:
        print(">>> ERROS DE VALIDAÇÃO DO PERFIL:", errors)
        return jsonify({"success": False, "errors": errors}), 400

    tatuador = tatuador_logado()
    id_tatuador = tatuador["id"]

    try:
        # --- 2. Trata o upload da nova foto de perfil (se houver) ---
        avatar_url = None
        foto = request.files.get("foto_perfil")
        
        if foto and foto.filename != '':
            extensao = os.path.splitext(secure_filename(foto.filename))[1]
            nome_arquivo = f"{id_tatuador}_{uuid.uuid4().hex[:8]}{extensao}"
            file_bytes = foto.read()
            
            # Envia para o bucket 'avatars' no Supabase
            supabase.storage.from_('avatars').upload(
                path=nome_arquivo,
                file=file_bytes,
                file_options={"content-type": foto.content_type, "upsert": "true"}
            )
            
            # Pega a URL pública gerada
            avatar_url = supabase.storage.from_('avatars').get_public_url(nome_arquivo)

        # --- 3. Salva na tabela 'tatuador' ---
        dados_atualizacao = {
            "nome": nome,
            "tel": tel_digits,
            "endereco": endereco
        }
        
        # Se uma nova foto foi enviada, atualiza a coluna. Se não, preserva a que já estava no banco/sessão.
        if avatar_url:
            dados_atualizacao["avatar_url"] = avatar_url
        else:
            avatar_url = tatuador.get("avatar_url") or ""

        supabase.table("tatuador").update(dados_atualizacao).eq("id_tatuador", id_tatuador).execute()

    except Exception as exc:
        print(">>> ERRO AO ATUALIZAR O PERFIL DO TATUADOR:", exc)
        return jsonify({"success": False, "errors": {"geral": "Não foi possível salvar as alterações."}}), 500

    # Atualiza a sessão para refletir as alterações imediatamente
    session["tatuador"] = {
        **tatuador, 
        "nome": nome, 
        "avatar_url": avatar_url,
        "endereco": endereco
    }

    return jsonify({
        "success": True,
        "message": "Perfil atualizado com sucesso!",
        "perfil": {
            "nome": nome,
            "telefone": formatar_telefone(tel_digits),
            "endereco": endereco,
            "avatar_url": avatar_url,
            "iniciais": iniciais(nome),
        },
    }), 200