import time

from werkzeug.utils import secure_filename

from portfolio_tatuador.db import supabase

BUCKET = "portfolio_images"
TIPOS_IMAGEM = {"image/jpeg", "image/png", "image/webp", "image/gif"}
TAMANHO_MAXIMO = 5 * 1024 * 1024  # 5 MB


def validar_trabalho(titulo, estilo, descricao, arquivo):
    """Valida os campos do formulário e retorna um dicionário de erros, se houver."""
    errors = {}

    if not titulo or len(titulo) > 100:
        errors["titulo"] = "Informe um título de até 100 caracteres."

    if not estilo or len(estilo) > 50:
        errors["estilo"] = "Informe o estilo (até 50 caracteres)."

    if descricao and len(descricao) > 1000:
        errors["descricao"] = "A descrição pode ter no máximo 1000 caracteres."

    if not arquivo or not arquivo.filename:
        errors["imagem"] = "Escolha uma imagem do trabalho."
    elif arquivo.mimetype not in TIPOS_IMAGEM:
        errors["imagem"] = "Envie uma imagem JPG, PNG, WEBP ou GIF."

    return errors


def enviar_imagem(arquivo, id_tatuador):
    """Sobe a imagem para o bucket e devolve a URL pública."""
    conteudo = arquivo.read()
    if len(conteudo) > TAMANHO_MAXIMO:
        raise ValueError("A imagem deve ter no máximo 5 MB.")

    nome_arquivo = f"{id_tatuador}/{int(time.time())}_{secure_filename(arquivo.filename) or 'imagem'}"
    supabase.storage.from_(BUCKET).upload(
        path=nome_arquivo,
        file=conteudo,
        file_options={"content-type": arquivo.mimetype, "upsert": "true"},
    )

    url = supabase.storage.from_(BUCKET).get_public_url(nome_arquivo)
    if isinstance(url, dict):
        url = url.get("publicUrl") or url.get("publicURL")
    return str(url)


def listar_trabalhos(id_tatuador):
    resposta = (
        supabase.table("portfolio")
        .select("*")
        .eq("id_tatuador", id_tatuador)
        .order("data_upload", desc=True)
        .execute()
    )
    return resposta.data or []


def criar_trabalho(id_tatuador, titulo, estilo, descricao, url_imagem):
    supabase.table("portfolio").insert({
        "id_tatuador": id_tatuador,
        "titulo": titulo,
        "estilo": estilo,
        "descricao": descricao or None,
        "caminho_imagem": url_imagem,
    }).execute()


def deletar_trabalho(id_tatuador, id_portfolio):
    """Só apaga se o trabalho for do tatuador logado."""
    supabase.table("portfolio").delete().eq("id_portfolio", id_portfolio).eq("id_tatuador", id_tatuador).execute()


def buscar_tatuador(id_tatuador):
    resposta = (
        supabase.table("tatuador")
        .select("id_tatuador, nome, especialidade")
        .eq("id_tatuador", id_tatuador)
        .limit(1)
        .execute()
    )
    return resposta.data[0] if resposta.data else None
