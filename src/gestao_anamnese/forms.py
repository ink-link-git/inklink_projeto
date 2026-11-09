from gestao_anamnese.db import supabase

# Perguntas de sim/não da ficha. O texto é o que aparece na tela e no resumo do tatuador.
PERGUNTAS = [
    ("possui_alergia", "Possui alguma alergia?", "descricao_alergia", "Quais? (ex: pigmentos, látex)"),
    ("possui_doenca_pele", "Possui alguma doença de pele no local?", "descricao_doenca_pele", "Qual? (ex: psoríase, dermatite)"),
    ("diabetico", "É diabético?", None, None),
    ("hemofilico", "Tem problemas de coagulação do sangue?", None, None),
    ("cardiopata", "É cardiopata?", None, None),
    ("epileptico", "Tem epilepsia?", None, None),
    ("hipertenso", "É hipertenso?", None, None),
    ("faz_uso_medicamento", "Usa algum medicamento contínuo?", "descricao_medicamento", "Quais medicamentos?"),
    ("usa_anticoagulante", "Usa remédios que afinam o sangue?", None, None),
    ("gestante", "Está grávida ou amamentando?", None, None),
    ("ja_fez_tatuagem", "Já fez tatuagem antes?", None, None),
    ("teve_reacao_tatuagem_anterior", "Teve problemas de cicatrização em tatuagem anterior?", "descricao_reacao", "O que aconteceu?"),
    ("consome_alcool_drogas", "Consumiu álcool ou drogas nas últimas 24 horas?", None, None),
]

STATUS_ATIVOS = ("PENDENTE", "CONFIRMADO")


def validar_ficha(data):
    """Valida as respostas da ficha. Retorna (erros, dados_limpos)."""
    errors = {}
    limpos = {}

    for campo, _texto, campo_descricao, _dica in PERGUNTAS:
        marcado = data.get(campo) is True
        limpos[campo] = marcado

        if campo_descricao:
            descricao = (data.get(campo_descricao) or "").strip()
            if len(descricao) > 500:
                errors[campo_descricao] = "Use no máximo 500 caracteres."
            elif marcado and not descricao:
                errors[campo_descricao] = "Conte um pouco mais sobre isso."
            limpos[campo_descricao] = descricao if marcado else None

    if data.get("ciente_riscos") is not True:
        errors["ciente_riscos"] = "Confirme que está ciente dos riscos."
    if data.get("termo_aceito") is not True:
        errors["termo_aceito"] = "É preciso aceitar o termo de responsabilidade."
    limpos["ciente_riscos"] = True
    limpos["termo_aceito"] = True

    return errors, limpos


def agendamentos_sem_ficha(cliente_id):
    """Sessões ativas do cliente que ainda não têm ficha."""
    resposta = (
        supabase.table("agendamento")
        .select("id, data_hora, data_desejada, periodo, status, id_tatuador, profissional")
        .eq("cliente_auth_id", cliente_id)
        .execute()
    )
    agendamentos = [a for a in resposta.data or [] if (a.get("status") or "").upper() in STATUS_ATIVOS]
    agendamentos.sort(key=lambda a: str(a.get("data_hora") or a.get("data_desejada") or ""))
    if not agendamentos:
        return []

    fichas = (
        supabase.table("anamnese")
        .select("agendamento_id")
        .in_("agendamento_id", [a["id"] for a in agendamentos])
        .execute()
    )
    preenchidas = {f["agendamento_id"] for f in fichas.data or []}
    return [a for a in agendamentos if a["id"] not in preenchidas]


def salvar_ficha(cliente_id, id_agendamento, dados):
    """Grava a ficha. Retorna (ok, mensagem, status_http)."""
    resposta = (
        supabase.table("agendamento")
        .select("id, status")
        .eq("id", id_agendamento)
        .eq("cliente_auth_id", cliente_id)
        .limit(1)
        .execute()
    )
    if not resposta.data:
        return False, "Agendamento não encontrado.", 404

    if (resposta.data[0].get("status") or "").upper() not in STATUS_ATIVOS:
        return False, "Esse agendamento não aceita mais ficha.", 400

    existente = supabase.table("anamnese").select("id").eq("agendamento_id", id_agendamento).limit(1).execute()
    if existente.data:
        return False, "A ficha deste agendamento já foi preenchida.", 409

    supabase.table("anamnese").insert({
        "agendamento_id": id_agendamento,
        "cliente_id": cliente_id,
        **dados,
    }).execute()
    return True, "Ficha enviada com sucesso!", 201


def buscar_ficha_do_tatuador(id_tatuador, id_agendamento):
    """Retorna (agendamento, cliente, ficha) se o agendamento for do tatuador; senão None."""
    resposta = (
        supabase.table("agendamento")
        .select("*")
        .eq("id", id_agendamento)
        .eq("id_tatuador", id_tatuador)
        .limit(1)
        .execute()
    )
    if not resposta.data:
        return None

    agendamento = resposta.data[0]
    agendamento["status"] = (agendamento.get("status") or "PENDENTE").upper()

    cliente = (
        supabase.table("cliente")
        .select("nome, telefone, email")
        .eq("auth_id", agendamento.get("cliente_auth_id"))
        .limit(1)
        .execute()
    )
    ficha = supabase.table("anamnese").select("*").eq("agendamento_id", id_agendamento).limit(1).execute()
    return (
        agendamento,
        cliente.data[0] if cliente.data else {},
        ficha.data[0] if ficha.data else None,
    )


def listar_fichas_do_tatuador(id_tatuador):
    """Sessões confirmadas/realizadas do tatuador, com o status da ficha de cada uma."""
    resposta = (
        supabase.table("agendamento")
        .select("id, data_hora, status, cliente_auth_id")
        .eq("id_tatuador", id_tatuador)
        .in_("status", ["CONFIRMADO", "REALIZADO"])
        .order("data_hora", desc=False)
        .execute()
    )
    agendamentos = resposta.data or []
    if not agendamentos:
        return []

    clientes = (
        supabase.table("cliente")
        .select("auth_id, nome")
        .in_("auth_id", list({a["cliente_auth_id"] for a in agendamentos if a.get("cliente_auth_id")}))
        .execute()
    )
    nomes = {c["auth_id"]: c["nome"] for c in clientes.data or []}

    fichas = (
        supabase.table("anamnese")
        .select("*")
        .in_("agendamento_id", [a["id"] for a in agendamentos])
        .execute()
    )
    por_agendamento = {f["agendamento_id"]: f for f in fichas.data or []}

    for item in agendamentos:
        item["nome_cliente"] = nomes.get(item.get("cliente_auth_id")) or "Cliente"
        item["ficha"] = por_agendamento.get(item["id"])
        item["alertas"] = alertas_da_ficha(item["ficha"]) if item["ficha"] else []
    return agendamentos


def alertas_da_ficha(ficha):
    """Lista curta com o que merece atenção do tatuador (respostas 'sim' de risco)."""
    return [texto for campo, texto, *_ in PERGUNTAS if ficha.get(campo) and campo != "ja_fez_tatuagem"]


def respostas_da_ficha(ficha):
    """Perguntas + respostas prontas para mostrar na tela."""
    linhas = []
    for campo, texto, campo_descricao, _dica in PERGUNTAS:
        linhas.append({
            "pergunta": texto,
            "resposta": bool(ficha.get(campo)),
            "detalhe": ficha.get(campo_descricao) if campo_descricao else None,
        })
    return linhas
