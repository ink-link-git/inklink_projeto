from datetime import date, datetime, timedelta

from agendamento_tatuador.db import supabase
from shared.utils import parse_data_hora, quando

DURACAO_PADRAO = 120  # minutos, usado quando a sessão não tem duração definida
DURACOES = [60, 90, 120, 150, 180, 240, 300, 360, 480]

# Quais status podem virar quais (o backend não confia no botão que o navegador mostrou).
TRANSICOES = {
    "CANCELADO": {"PENDENTE", "CONFIRMADO"},
    "REALIZADO": {"CONFIRMADO"},
}


def _status(item):
    return (item.get("status") or "PENDENTE").upper()


def _clientes_por_id(ids):
    """Busca nome/telefone dos clientes de uma lista de agendamentos."""
    ids = list({i for i in ids if i})
    if not ids:
        return {}
    resposta = (
        supabase.table("cliente")
        .select("auth_id, nome, telefone, email")
        .in_("auth_id", ids)
        .execute()
    )
    return {c["auth_id"]: c for c in resposta.data or []}


def listar_agendamentos(id_tatuador):
    """Agendamentos do tatuador, já com os dados do cliente e as imagens de referência."""
    resposta = (
        supabase.table("agendamento")
        .select("*")
        .eq("id_tatuador", id_tatuador)
        .execute()
    )
    agendamentos = resposta.data or []
    agendamentos.sort(key=lambda a: str(a.get("data_hora") or a.get("data_desejada") or ""))
    clientes = _clientes_por_id([a.get("cliente_auth_id") for a in agendamentos])

    referencias = {}
    if agendamentos:
        refs = (
            supabase.table("referencia_visual")
            .select("agendamento_id, caminho_imagem")
            .in_("agendamento_id", [a["id"] for a in agendamentos])
            .execute()
        )
        for ref in refs.data or []:
            referencias.setdefault(ref["agendamento_id"], []).append(ref["caminho_imagem"])

    for item in agendamentos:
        cliente = clientes.get(item.get("cliente_auth_id")) or {}
        item["status"] = _status(item)
        item["nome_cliente"] = cliente.get("nome") or "Cliente"
        item["telefone_cliente"] = cliente.get("telefone")
        item["referencias"] = referencias.get(item["id"], [])
        item["quando"] = quando(item)
        item["dia"] = _dia_do_item(item)
    return agendamentos


def _dia_do_item(item):
    """Dia (AAAA-MM-DD) da sessão marcada ou do pedido."""
    dt = parse_data_hora(item.get("data_hora")) or parse_data_hora(item.get("data_desejada"))
    return dt.date().isoformat() if dt else ""


def sessoes_confirmadas(agendamentos):
    """Resumo das sessões confirmadas, para o tatuador enxergar o dia antes de aceitar outra."""
    saida = []
    for a in agendamentos:
        inicio = parse_data_hora(a.get("data_hora"))
        if a["status"] != "CONFIRMADO" or not inicio:
            continue
        fim = inicio + timedelta(minutes=a.get("duracao_min") or DURACAO_PADRAO)
        saida.append({
            "dia": inicio.date().isoformat(),
            "inicio": f"{inicio:%H:%M}",
            "fim": f"{fim:%H:%M}",
            "cliente": a["nome_cliente"],
        })
    return saida


def resumo_agenda(id_tatuador):
    """Números e próxima sessão para a tela inicial do tatuador."""
    resumo = {"pendentes": 0, "confirmados": 0, "fichas_pendentes": 0, "proximo": None}
    try:
        agendamentos = listar_agendamentos(id_tatuador)
        agora = datetime.now()
        futuros = [
            a for a in agendamentos
            if (parse_data_hora(a.get("data_hora")) or parse_data_hora(a.get("data_desejada")) or agora).date() >= agora.date()
        ]

        resumo["pendentes"] = sum(1 for a in futuros if a["status"] == "PENDENTE")
        confirmados = [a for a in futuros if a["status"] == "CONFIRMADO"]
        resumo["confirmados"] = len(confirmados)

        if confirmados:
            ids = [a["id"] for a in confirmados]
            fichas = supabase.table("anamnese").select("agendamento_id").in_("agendamento_id", ids).execute()
            preenchidas = {f["agendamento_id"] for f in fichas.data or []}
            resumo["fichas_pendentes"] = sum(1 for i in ids if i not in preenchidas)

        proximos = [a for a in futuros if a["status"] in ("PENDENTE", "CONFIRMADO")]
        if proximos:
            resumo["proximo"] = proximos[0]
    except Exception as exc:
        # A tela inicial não pode quebrar se a agenda estiver indisponível.
        print(">>> ERRO AO MONTAR RESUMO DA AGENDA:", exc)
    return resumo


def buscar_do_tatuador(id_tatuador, id_agendamento):
    """Pega um agendamento só se ele pertencer ao tatuador logado."""
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
    item = resposta.data[0]
    item["status"] = _status(item)
    return item


def alterar_status(id_tatuador, id_agendamento, novo_status):
    """Muda o status respeitando as transições permitidas. Retorna (ok, mensagem)."""
    item = buscar_do_tatuador(id_tatuador, id_agendamento)
    if not item:
        return False, "Agendamento não encontrado."

    if item["status"] not in TRANSICOES.get(novo_status, set()):
        return False, "Essa ação não está disponível para este agendamento."

    supabase.table("agendamento").update({"status": novo_status}).eq("id", id_agendamento).execute()
    return True, "Agendamento atualizado."


def conflito_de_horario(id_tatuador, inicio, duracao_min, ignorar_id=None):
    """Retorna a sessão confirmada que se sobrepõe ao intervalo pedido (ou None)."""
    fim = inicio + timedelta(minutes=duracao_min)
    resposta = (
        supabase.table("agendamento")
        .select("id, data_hora, status, duracao_min")
        .eq("id_tatuador", id_tatuador)
        .gte("data_hora", f"{inicio.date().isoformat()}T00:00:00")
        .lte("data_hora", f"{inicio.date().isoformat()}T23:59:59")
        .execute()
    )
    for outro in resposta.data or []:
        if outro["id"] == ignorar_id or _status(outro) != "CONFIRMADO":
            continue
        outro_inicio = parse_data_hora(outro.get("data_hora"))
        if not outro_inicio:
            continue
        outro_fim = outro_inicio + timedelta(minutes=outro.get("duracao_min") or DURACAO_PADRAO)
        if inicio < outro_fim and outro_inicio < fim:
            return outro
    return None


def definir_horario(id_tatuador, id_agendamento, dia_texto, hora_texto, duracao_texto):
    """Aceita um pedido (ou muda o horário de uma sessão confirmada) com dia, hora e duração
    escolhidos pelo tatuador. Retorna (ok, mensagem)."""
    item = buscar_do_tatuador(id_tatuador, id_agendamento)
    if not item:
        return False, "Agendamento não encontrado."
    if item["status"] not in ("PENDENTE", "CONFIRMADO"):
        return False, "Esse agendamento não pode mais ser alterado."

    try:
        dia = date.fromisoformat(dia_texto or "")
        inicio = datetime.fromisoformat(f"{dia.isoformat()}T{hora_texto}")
        duracao = int(duracao_texto)
    except (TypeError, ValueError):
        return False, "Informe dia, hora e duração válidos."

    if not 15 <= duracao <= 720:
        return False, "A duração deve ficar entre 15 minutos e 12 horas."
    if inicio <= datetime.now():
        return False, "Escolha um horário futuro."

    inicio = inicio.replace(second=0, microsecond=0)
    if conflito_de_horario(id_tatuador, inicio, duracao, ignorar_id=id_agendamento):
        return False, "Esse horário se sobrepõe a outra sessão confirmada sua."

    supabase.table("agendamento").update({
        "data_hora": inicio.isoformat(),
        "duracao_min": duracao,
        "status": "CONFIRMADO",
    }).eq("id", id_agendamento).execute()
    return True, "Sessão confirmada para " + f"{inicio:%d/%m} às {inicio:%H:%M}."
