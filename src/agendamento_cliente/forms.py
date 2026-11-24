import time
from datetime import date, datetime, timezone
from urllib.parse import quote

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


def _telefone_whatsapp(valor):
    """Deixa só os números e coloca o 55 (Brasil). Devolve None se não parecer um telefone."""
    digitos = "".join(ch for ch in str(valor or "") if ch.isdigit())
    if len(digitos) < 10:
        return None
    # Até 11 dígitos = DDD + número (sem o código do país). O 55 também é DDD do RS,
    # por isso a decisão é pelo tamanho e não por "começa com 55".
    if len(digitos) <= 11:
        digitos = "55" + digitos
    return digitos


def contatar_tatuador_whatsapp(cliente, id_agendamento):
    """Libera o contato por WhatsApp de um pedido PENDENTE, uma única vez.

    Retorna (True, url_do_whatsapp) ou (False, mensagem_de_erro).
    """
    resposta = (
        supabase.table("agendamento")
        .select("*")
        .eq("id", id_agendamento)
        .eq("cliente_auth_id", cliente["id"])
        .limit(1)
        .execute()
    )
    if not resposta.data:
        return False, "Agendamento não encontrado."
    agendamento = resposta.data[0]

    if (agendamento.get("status") or "").upper() != "PENDENTE":
        return False, "O contato por WhatsApp só está disponível enquanto o agendamento está pendente."
    if agendamento.get("whatsapp_enviado_em"):
        return False, "Você já usou o contato por WhatsApp neste agendamento."

    # Antes de gastar a única chance, garante que existe para quem mandar a mensagem.
    resposta = (
        supabase.table("tatuador")
        .select("nome, tel")
        .eq("id_tatuador", agendamento["id_tatuador"])
        .limit(1)
        .execute()
    )
    tatuador = resposta.data[0] if resposta.data else None
    telefone = _telefone_whatsapp(tatuador.get("tel")) if tatuador else None
    if not telefone:
        return False, "Este tatuador ainda não cadastrou um WhatsApp para contato."

    # Marca como usado SOMENTE se continuar pendente e ainda não usado. Tudo numa única
    # operação no banco: dois cliques ao mesmo tempo não passam os dois.
    marcado = (
        supabase.table("agendamento")
        .update({"whatsapp_enviado_em": datetime.now(timezone.utc).isoformat()})
        .eq("id", id_agendamento)
        .eq("cliente_auth_id", cliente["id"])
        .eq("status", "PENDENTE")
        .is_("whatsapp_enviado_em", "null")
        .execute()
    )
    if not marcado.data:
        return False, "Você já usou o contato por WhatsApp neste agendamento."

    from shared.utils import formatar_dia

    # formatar_dia devolve "seg, 02/11/2026"; aqui basta a data.
    dia = (formatar_dia(agendamento.get("data_desejada")) or "").split(", ")[-1]
    periodo = PERIODOS.get(agendamento.get("periodo")) or "Sem preferência"
    descricao = (agendamento.get("descricao") or "").strip()
    if len(descricao) > 500:
        descricao = descricao[:500].rstrip() + "…"

    linhas = [
        f"Olá, {tatuador.get('nome') or 'tudo bem'}! Aqui é {cliente.get('nome') or 'um cliente'}. "
        "Fiz um pedido de agendamento pelo InkLink:",
        "",
        f"📅 Data desejada: {dia}",
        f"🕐 Período: {periodo}",
    ]
    if descricao:
        linhas.append(f"📝 Ideia da tatuagem: {descricao}")
    linhas += ["", "Poderia me passar um orçamento e os horários disponíveis?"]

    return True, f"https://wa.me/{telefone}?text={quote(chr(10).join(linhas))}"
