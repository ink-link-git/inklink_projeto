from datetime import date, datetime

from estoque_tatuador.db import supabase

LIMITE_BAIXO = 2  # a partir daqui o item aparece como "Estoque baixo"

# Itens que o tatuador recebe na primeira vez que abre o Estoque (categoria, nome, qtd, plural, singular).
ITENS_INICIAIS = [
    ("TINTA", "Tinta Preta #1", 12, "frascos", "frasco"),
    ("TINTA", "Tinta Cinza Wash", 2, "frascos", "frasco"),
    ("AGULHA", "Agulha 7RL", 30, "unid.", "unid."),
    ("AGULHA", "Agulha 3RL Fineline", 15, "unid.", "unid."),
    ("CURATIVO", "Película Protetora", 1, "rolo", "rolo"),
    ("CURATIVO", "Vaselina", 5, "potes", "pote"),
    ("MATERIAL", "Stencil Paper", 40, "folhas", "folha"),
]
ORDEM_CATEGORIAS = ["TINTA", "AGULHA", "CURATIVO", "MATERIAL"]
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def _rotulo(qtd, plural, singular):
    return singular if qtd == 1 else plural


def listar_itens(id_tatuador):
    """Itens do tatuador. Na primeira vez cria o catálogo inicial."""
    dados = supabase.table("estoque_item").select("*").eq("id_tatuador", id_tatuador).execute().data or []
    if not dados:
        supabase.table("estoque_item").insert([
            {"id_tatuador": id_tatuador, "categoria": c, "nome": n, "quantidade": q, "unidade": p, "unidade_singular": s}
            for c, n, q, p, s in ITENS_INICIAIS
        ]).execute()
        dados = supabase.table("estoque_item").select("*").eq("id_tatuador", id_tatuador).execute().data or []
    dados.sort(key=lambda i: (ORDEM_CATEGORIAS.index(i["categoria"]) if i["categoria"] in ORDEM_CATEGORIAS else 99, i["id"]))
    for i in dados:
        i["baixo"] = i["quantidade"] <= LIMITE_BAIXO
        i["rotulo"] = _rotulo(i["quantidade"], i["unidade"], i["unidade_singular"])
    return dados


def agrupar_por_categoria(itens):
    grupos = {}
    for i in itens:
        grupos.setdefault(i["categoria"], []).append(i)
    return grupos


def listar_clientes(id_tatuador):
    """Nomes dos clientes com agendamento (pendente, confirmado ou realizado) com este tatuador, sem repetir."""
    ags = (
        supabase.table("agendamento").select("cliente_auth_id")
        .eq("id_tatuador", id_tatuador).neq("status", "CANCELADO").execute().data or []
    )
    ids = list({a["cliente_auth_id"] for a in ags if a.get("cliente_auth_id")})
    if not ids:
        return []
    clientes = supabase.table("cliente").select("nome").in_("auth_id", ids).execute().data or []
    return sorted({c["nome"] for c in clientes if c.get("nome")}, key=str.lower)


def _data_fmt(valor):
    d = date.fromisoformat(str(valor)[:10])
    return f"{d.day:02d} {MESES[d.month - 1]} {d.year}"


def listar_historico(id_tatuador):
    """Usos em sessões e compras de material, do mais recente para o mais antigo."""
    registros = []

    usos = (
        supabase.table("estoque_uso").select("*").eq("id_tatuador", id_tatuador).execute().data or []
    )
    if usos:
        linhas = supabase.table("estoque_uso_item").select("*").in_("uso_id", [u["id"] for u in usos]).execute().data or []
        por_uso = {}
        for l in linhas:
            por_uso.setdefault(l["uso_id"], []).append(
                {"quantidade": l["quantidade"], "nome": l["nome_item"], "rotulo": _rotulo(l["quantidade"], l["unidade"], l["unidade_singular"])}
            )
        for u in usos:
            registros.append({
                "tipo": "uso", "titulo": u["cliente"], "ordem": (str(u["data_sessao"])[:10], u["id"]),
                "data_fmt": _data_fmt(u["data_sessao"]), "itens": por_uso.get(u["id"], []),
            })

    compras = (
        supabase.table("estoque_compra").select("*").eq("id_tatuador", id_tatuador).execute().data or []
    )
    for c in compras:
        registros.append({
            "tipo": "compra", "titulo": "Compra de material", "ordem": (str(c["data_compra"])[:10], c["id"]),
            "data_fmt": _data_fmt(c["data_compra"]),
            "itens": [{"quantidade": c["quantidade"], "nome": c["nome_item"], "rotulo": _rotulo(c["quantidade"], c["unidade"], c["unidade_singular"])}],
        })

    registros.sort(key=lambda r: r["ordem"], reverse=True)
    return registros


CATEGORIAS = ORDEM_CATEGORIAS


def registrar_compra(id_tatuador, item_id, novo, quantidade_texto, data_texto):
    """Soma a quantidade comprada ao estoque (criando o material, se for novo) e grava a compra."""
    try:
        quantidade = int((quantidade_texto or "").strip())
    except ValueError:
        return False, "Informe a quantidade comprada."
    if not 1 <= quantidade <= 100000:
        return False, "A quantidade comprada precisa ser de pelo menos 1."
    try:
        data_compra = datetime.strptime(data_texto or "", "%Y-%m-%d").date().isoformat()
    except ValueError:
        return False, "Informe a data da compra."

    if item_id == "__novo__":
        nome = (novo.get("nome") or "").strip()
        categoria = (novo.get("categoria") or "").upper()
        unidade = (novo.get("unidade") or "").strip()
        if not nome or not unidade:
            return False, "Informe o nome e a unidade do novo material."
        if categoria not in CATEGORIAS:
            return False, "Escolha a categoria do material."
        singular = unidade[:-1] if unidade.endswith("s") and not unidade.endswith(".") else unidade
        item = supabase.table("estoque_item").insert({
            "id_tatuador": id_tatuador, "categoria": categoria, "nome": nome[:80],
            "quantidade": 0, "unidade": unidade[:20], "unidade_singular": singular[:20],
        }).execute().data[0]
    else:
        try:
            item_id = int(item_id)
        except (TypeError, ValueError):
            return False, "Selecione o material comprado."
        itens = {i["id"]: i for i in listar_itens(id_tatuador)}  # só itens do próprio tatuador
        item = itens.get(item_id)
        if not item:
            return False, "Material inválido."

    supabase.table("estoque_compra").insert({
        "id_tatuador": id_tatuador, "item_id": item["id"], "nome_item": item["nome"],
        "quantidade": quantidade, "unidade": item["unidade"], "unidade_singular": item["unidade_singular"],
        "data_compra": data_compra,
    }).execute()
    supabase.table("estoque_item").update({"quantidade": item["quantidade"] + quantidade}).eq("id", item["id"]).eq("id_tatuador", id_tatuador).execute()
    return True, f"Compra registrada: +{quantidade} em {item['nome']}."


def registrar_uso(id_tatuador, cliente, data_sessao, quantidades):
    """quantidades: {id_item: qtd}. Valida tudo, baixa o estoque e grava o histórico."""
    cliente = (cliente or "").strip()
    if not cliente:
        return False, "Informe o nome do cliente."
    try:
        data_sessao = datetime.strptime(data_sessao or "", "%Y-%m-%d").date().isoformat()
    except ValueError:
        return False, "Informe a data da sessão."
    if not quantidades:
        return False, "Selecione ao menos um insumo."

    itens = {i["id"]: i for i in listar_itens(id_tatuador)}  # só itens do próprio tatuador
    for id_item, qtd in quantidades.items():
        item = itens.get(id_item)
        if not item:
            return False, "Insumo inválido."
        if qtd < 1:
            return False, "A quantidade precisa ser de pelo menos 1."
        if qtd > item["quantidade"]:
            return False, f"Estoque insuficiente de {item['nome']} (restam {item['quantidade']})."

    uso = supabase.table("estoque_uso").insert(
        {"id_tatuador": id_tatuador, "cliente": cliente[:120], "data_sessao": data_sessao}
    ).execute().data[0]
    supabase.table("estoque_uso_item").insert([
        {"uso_id": uso["id"], "item_id": i, "nome_item": itens[i]["nome"], "quantidade": q,
         "unidade": itens[i]["unidade"], "unidade_singular": itens[i]["unidade_singular"]}
        for i, q in quantidades.items()
    ]).execute()
    for i, q in quantidades.items():
        supabase.table("estoque_item").update({"quantidade": itens[i]["quantidade"] - q}).eq("id", i).eq("id_tatuador", id_tatuador).execute()
    return True, "Uso registrado e estoque atualizado."
