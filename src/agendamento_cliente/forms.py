import time
from datetime import date

from werkzeug.utils import secure_filename

from agendamento_cliente.db import supabase
from shared.utils import PERIODOS

BUCKET_REFERENCIAS = "referencias"
TIPOS_IMAGEM = {"image/jpeg", "image/png", "image/webp", "image/gif"}
TAMANHO_MAXIMO = 5 * 1024 * 1024  # 5 MB por imagem
MAX_IMAGENS = 4
CORES_PELE = {"muito-clara", "clara", "media", "morena", "escura", "muito-escura"}


def listar_tatuadores():
    resposta = (
        supabase.table("tatuador")
        .select("id_tatuador, nome, especialidade")
        .order("nome")
        .execute()
    )
    return resposta.data or []


def buscar_tatuador(id_tatuador):
    resposta = (
        supabase.table("tatuador")
        .select("id_tatuador, nome, especialidade")
        .eq("id_tatuador", id_tatuador)
        .limit(1)
        .execute()
    )
    return resposta.data[0] if resposta.data else None


def validar_agendamento(id_tatuador, data_texto, periodo, cor_pele, descricao, anamnese_ciente, arquivos):
    """Valida o pedido de agendamento e devolve (erros, dia)."""
    errors = {}
    dia = None

    if not id_tatuador:
        errors["tatuador"] = "Escolha o tatuador."

    try:
        dia = date.fromisoformat(data_texto or "")
    except ValueError:
        errors["data"] = "Selecione o dia desejado."

    if dia and dia < date.today():
        errors["data"] = "Escolha uma data de hoje em diante."

    if periodo not in PERIODOS:
        errors["periodo"] = "Escolha uma preferência de período."

    if cor_pele not in CORES_PELE:
        errors["pele"] = "Selecione uma opção."

    if descricao and len(descricao) > 1000:
        errors["descricao"] = "A descrição pode ter no máximo 1000 caracteres."

    if not anamnese_ciente:
        errors["anamnese"] = "Confirme que está ciente da ficha de anamnese."

    if len(arquivos) > MAX_IMAGENS:
        errors["imagens"] = f"Envie no máximo {MAX_IMAGENS} imagens."
    for arquivo in arquivos:
        if arquivo.mimetype not in TIPOS_IMAGEM:
            errors["imagens"] = "As referências precisam ser imagens JPG, PNG, WEBP ou GIF."

    return errors, dia


def criar_agendamento(cliente_id, tatuador, dia, periodo, cor_pele, descricao):
    """Registra o pedido. O horário exato (data_hora) só nasce quando o tatuador aceita."""
    # Evita pedido repetido: mesmo cliente, mesmo tatuador, mesmo dia, ainda ativo.
    existentes = (
        supabase.table("agendamento")
        .select("id, status")
        .eq("cliente_auth_id", cliente_id)
        .eq("id_tatuador", tatuador["id_tatuador"])
        .eq("data_desejada", dia.isoformat())
        .execute()
    )
    for item in existentes.data or []:
        if (item.get("status") or "").upper() in ("PENDENTE", "CONFIRMADO"):
            raise ValueError("Você já tem um pedido com esse tatuador para esse dia.")

    resposta = supabase.table("agendamento").insert({
        "cliente_auth_id": cliente_id,
        "id_tatuador": tatuador["id_tatuador"],
        "data_desejada": dia.isoformat(),
        "periodo": periodo,
        "status": "PENDENTE",
        "cor_pele": cor_pele,
        "descricao": descricao or None,
        # Colunas já existentes na tabela da agenda antiga
        "servico": "Tatuagem",
        "especialidade": tatuador.get("especialidade"),
        "profissional": tatuador.get("nome"),
    }).execute()
    return resposta.data[0]


def enviar_referencias(id_agendamento, cliente_id, arquivos):
    """Sobe as imagens de referência e registra na tabela. Retorna quantas foram salvas."""
    salvas = 0
    for arquivo in arquivos:
        conteudo = arquivo.read()
        if not conteudo or len(conteudo) > TAMANHO_MAXIMO:
            continue

        nome = f"{cliente_id}/{id_agendamento}_{int(time.time() * 1000)}_{secure_filename(arquivo.filename) or 'ref'}"
        supabase.storage.from_(BUCKET_REFERENCIAS).upload(
            path=nome,
            file=conteudo,
            file_options={"content-type": arquivo.mimetype, "upsert": "true"},
        )
        url = supabase.storage.from_(BUCKET_REFERENCIAS).get_public_url(nome)
        if isinstance(url, dict):
            url = url.get("publicUrl") or url.get("publicURL")

        supabase.table("referencia_visual").insert({
            "agendamento_id": id_agendamento,
            "caminho_imagem": str(url),
        }).execute()
        salvas += 1
    return salvas


def listar_do_cliente(cliente_id):
    resposta = (
        supabase.table("agendamento")
        .select("*")
        .eq("cliente_auth_id", cliente_id)
        .execute()
    )
    agendamentos = resposta.data or []
    if not agendamentos:
        return []

    ids_tatuadores = list({a["id_tatuador"] for a in agendamentos if a.get("id_tatuador")})
    nomes = {}
    if ids_tatuadores:
        tatuadores = (
            supabase.table("tatuador")
            .select("id_tatuador, nome")
            .in_("id_tatuador", ids_tatuadores)
            .execute()
        )
        nomes = {t["id_tatuador"]: t["nome"] for t in tatuadores.data or []}

    fichas = (
        supabase.table("anamnese")
        .select("agendamento_id")
        .in_("agendamento_id", [a["id"] for a in agendamentos])
        .execute()
    )
    com_ficha = {f["agendamento_id"] for f in fichas.data or []}

    for item in agendamentos:
        item["status"] = (item.get("status") or "PENDENTE").upper()
        item["nome_tatuador"] = nomes.get(item.get("id_tatuador")) or item.get("profissional") or "Tatuador"
        item["tem_ficha"] = item["id"] in com_ficha
        # Texto pronto: horário marcado ou "dia pedido · horário a definir"
        from shared.utils import quando
        item["quando"] = quando(item)

    agendamentos.sort(key=lambda a: str(a.get("data_hora") or a.get("data_desejada") or ""))
    return agendamentos


def cancelar_do_cliente(cliente_id, id_agendamento):
    """Cliente cancela a própria sessão. Retorna (ok, mensagem)."""
    resposta = (
        supabase.table("agendamento")
        .select("id, status")
        .eq("id", id_agendamento)
        .eq("cliente_auth_id", cliente_id)
        .limit(1)
        .execute()
    )
    if not resposta.data:
        return False, "Agendamento não encontrado."

    if (resposta.data[0].get("status") or "").upper() not in ("PENDENTE", "CONFIRMADO"):
        return False, "Esse agendamento não pode mais ser cancelado."

    supabase.table("agendamento").update({"status": "CANCELADO"}).eq("id", id_agendamento).eq("cliente_auth_id", cliente_id).execute()
    return True, "Agendamento cancelado."
