import re
import unicodedata

from login_cliente.db import supabase

MAX_MINIATURAS = 3


def _chave(texto):
    """'Fine Line', 'fineline' e 'Fine-line' viram a mesma chave."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", sem_acento.lower())


def _tags(especialidade, estilos=()):
    """Tipos de arte de um tatuador: especialidade (texto livre, separado por vírgula,
    barra, ponto e vírgula, '&' ou ' e ') + estilos dos trabalhos do portfólio."""
    partes = re.split(r"[,/;|&]| e ", especialidade or "")
    vistos, tags = set(), []
    for parte in list(partes) + list(estilos):
        rotulo = (parte or "").strip()
        chave = _chave(rotulo)
        if not chave or chave in vistos or len(rotulo) > 30:
            continue
        vistos.add(chave)
        tags.append({"chave": chave, "rotulo": rotulo[:1].upper() + rotulo[1:]})
    return tags


def _miniaturas(ids):
    """Até 3 imagens recentes do portfólio de cada tatuador. Sem portfólio, volta vazio."""
    if not ids:
        return {}, {}
    try:
        resposta = (
            supabase.table("portfolio")
            .select("id_tatuador, caminho_imagem, titulo, estilo")
            .in_("id_tatuador", ids)
            .order("data_upload", desc=True)
            .execute()
        )
    except Exception as exc:
        print(">>> ERRO AO BUSCAR MINIATURAS DO PORTFÓLIO:", exc)
        return {}, {}

    por_tatuador, estilos = {}, {}
    for trabalho in resposta.data or []:
        if trabalho.get("estilo"):
            estilos.setdefault(trabalho["id_tatuador"], []).append(trabalho["estilo"])
        if not trabalho.get("caminho_imagem"):
            continue
        lista = por_tatuador.setdefault(trabalho["id_tatuador"], [])
        if len(lista) < MAX_MINIATURAS:
            lista.append({"url": trabalho["caminho_imagem"], "titulo": trabalho.get("titulo") or ""})
    return por_tatuador, estilos


def _ficha(t, miniaturas=None, estilos=None):
    nome = (t.get("nome") or "Tatuador").strip()
    partes = nome.split()
    return {
        "id_tatuador": t["id_tatuador"],
        "nome": nome,
        "iniciais": ((partes[0][:1] if partes else "?") + (partes[1][:1] if len(partes) > 1 else "")).upper(),
        "especialidade": (t.get("especialidade") or "").strip(),
        "foto_url": t.get("foto_url") or None,
        "endereco": (t.get("endereco") or "").strip(),
        "miniaturas": (miniaturas or {}).get(t["id_tatuador"], []),
        "tags": _tags(t.get("especialidade"), (estilos or {}).get(t["id_tatuador"], [])),
    }


def buscar_ficha(id_tatuador):
    """Ficha pública de um tatuador (ou None). Usada pelo agendamento."""
    resposta = supabase.table("tatuador").select("*").eq("id_tatuador", id_tatuador).limit(1).execute()
    return _ficha(resposta.data[0]) if resposta.data else None


def listar_fichas():
    """Fichas dos tatuadores para o cliente escolher.

    Só sai daqui o que pode ser público: nome, especialidade, foto, endereço e
    miniaturas do portfólio. CPF, e-mail e telefone NUNCA vão para a tela.
    'foto_url' e 'endereco' são colunas opcionais (database/migracoes/05_tatuador_perfil.sql).
    """
    resposta = supabase.table("tatuador").select("*").order("nome").execute()
    tatuadores = resposta.data or []
    miniaturas, estilos = _miniaturas([t["id_tatuador"] for t in tatuadores])

    return [_ficha(t, miniaturas, estilos) for t in tatuadores]


def filtros_das_fichas(fichas):
    """Botões de filtro: todos os tipos de arte que aparecem nas fichas, com a contagem."""
    contagem = {}
    for f in fichas:
        for tag in f["tags"]:
            item = contagem.setdefault(tag["chave"], {"chave": tag["chave"], "rotulo": tag["rotulo"], "total": 0})
            item["total"] += 1
    return sorted(contagem.values(), key=lambda i: (-i["total"], i["rotulo"].lower()))
