from flask import Blueprint, flash, redirect, render_template, request, url_for

from estoque_tatuador.forms import agrupar_por_categoria, CATEGORIAS, listar_clientes, listar_historico, listar_itens, registrar_compra, registrar_uso
from shared.auth import tatuador_logado, tatuador_required

bp = Blueprint(
    "estoque_tatuador",
    __name__,
    static_folder="static",
    static_url_path="/static/estoque_tatuador",
)

ABAS = ("listagem", "uso", "historico")


@bp.route("/tatuador/estoque")
@tatuador_required
def estoque():
    aba = request.args.get("aba", "listagem")
    if aba not in ABAS:
        aba = "listagem"
    id_tatuador = tatuador_logado()["id"]
    itens, historico, clientes, erro, erro_clientes = [], [], [], None, False
    try:
        itens = listar_itens(id_tatuador)
        if aba == "historico":
            historico = listar_historico(id_tatuador)
    except Exception as exc:
        print(">>> ERRO AO CARREGAR ESTOQUE (rodou o 05_estoque.sql no Supabase?):", exc)
        erro = "Não foi possível carregar o estoque agora. Tente novamente."

    # Clientes em bloco separado: se falhar, o resto da tela continua funcionando.
    if aba == "uso":
        try:
            clientes = listar_clientes(id_tatuador)
        except Exception as exc:
            print(">>> ERRO AO LISTAR CLIENTES DO ESTOQUE:", exc)
            erro_clientes = True

    return render_template(
        "estoque_tatuador/estoque.html",
        aba=aba, itens=itens, grupos=agrupar_por_categoria(itens),
        historico=historico, clientes=clientes, categorias=CATEGORIAS, erro_clientes=erro_clientes, erro=erro, ativo="estoque",
    )


@bp.route("/tatuador/estoque/uso", methods=["POST"])
@tatuador_required
def registrar():
    quantidades = {}
    for chave, valor in request.form.items():
        if chave.startswith("qtd_"):
            try:
                quantidades[int(chave[4:])] = int(valor)
            except ValueError:
                flash("Quantidade inválida.", "danger")
                return redirect(url_for("estoque_tatuador.estoque", aba="uso"))
    cliente = request.form.get("cliente")
    if cliente == "__outro__":  # cliente que não veio da agenda (digitado)
        cliente = request.form.get("cliente_outro")
    try:
        ok, mensagem = registrar_uso(
            tatuador_logado()["id"], cliente, request.form.get("data_sessao"), quantidades
        )
    except Exception as exc:
        print(">>> ERRO AO REGISTRAR USO:", exc)
        ok, mensagem = False, "Erro ao registrar o uso. Tente novamente."
    flash(mensagem, "success" if ok else "danger")
    return redirect(url_for("estoque_tatuador.estoque", aba="historico" if ok else "uso"))


@bp.route("/tatuador/estoque/compra", methods=["POST"])
@tatuador_required
def comprar():
    f = request.form
    try:
        ok, mensagem = registrar_compra(
            tatuador_logado()["id"], f.get("item"),
            {"nome": f.get("novo_nome"), "categoria": f.get("novo_categoria"), "unidade": f.get("novo_unidade")},
            f.get("quantidade"), f.get("data_compra"),
        )
    except Exception as exc:
        print(">>> ERRO AO REGISTRAR COMPRA (rodou o 06_estoque_compra.sql?):", exc)
        ok, mensagem = False, "Erro ao registrar a compra. Tente novamente."
    flash(mensagem, "success" if ok else "danger")
    return redirect(url_for("estoque_tatuador.estoque", aba="listagem"))
