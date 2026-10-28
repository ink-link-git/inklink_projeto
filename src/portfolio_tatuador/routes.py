from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from portfolio_tatuador.forms import (
    buscar_tatuador,
    criar_trabalho,
    deletar_trabalho,
    enviar_imagem,
    listar_trabalhos,
    validar_trabalho,
)
from shared.auth import tatuador_logado, tatuador_required

# Blueprint do módulo. O static_url_path próprio evita conflito com os outros módulos.
portfolio_bp = Blueprint(
    "portfolio_tatuador",
    __name__,
    static_folder="static",
    static_url_path="/static/portfolio_tatuador",
)


@portfolio_bp.route("/tatuador/portfolio")
@tatuador_required
def mostrar_portfolio():
    tatuador = tatuador_logado()
    try:
        trabalhos = listar_trabalhos(tatuador["id"])
        erro = None
    except Exception as exc:
        print(f">>> ERRO AO BUSCAR PORTFÓLIO: {exc}")
        trabalhos, erro = [], "Não foi possível carregar o portfólio agora."

    return render_template(
        "portfolio_tatuador/portfolio_tela.html",
        tatuador=tatuador,
        trabalhos=trabalhos,
        erro=erro,
        ativo="portfolio",
    )


@portfolio_bp.route("/tatuador/portfolio/novo", methods=["GET", "POST"])
@tatuador_required
def adicionar_portfolio():
    tatuador = tatuador_logado()
    erros, valores = {}, {}

    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        estilo = (request.form.get("estilo") or "").strip()
        descricao = (request.form.get("descricao") or "").strip()
        arquivo = request.files.get("imagem")
        valores = {"titulo": titulo, "estilo": estilo, "descricao": descricao}

        erros = validar_trabalho(titulo, estilo, descricao, arquivo)
        if not erros:
            try:
                url = enviar_imagem(arquivo, tatuador["id"])
                criar_trabalho(tatuador["id"], titulo, estilo, descricao, url)
                flash("Trabalho adicionado ao portfólio.", "success")
                return redirect(url_for("portfolio_tatuador.mostrar_portfolio"))
            except ValueError as exc:
                erros["imagem"] = str(exc)
            except Exception as exc:
                print(f">>> ERRO AO CADASTRAR TRABALHO: {exc}")
                flash("Não foi possível salvar o trabalho. Tente novamente.", "danger")

    return render_template(
        "portfolio_tatuador/portfolio_adicionar.html",
        tatuador=tatuador,
        erros=erros,
        valores=valores,
        ativo="portfolio",
    )


@portfolio_bp.route("/tatuador/portfolio/deletar/<string:id_portfolio>", methods=["POST"])
@tatuador_required
def deletar_portfolio(id_portfolio):
    try:
        deletar_trabalho(tatuador_logado()["id"], id_portfolio)
        flash("Trabalho removido.", "info")
    except Exception as exc:
        print(f">>> ERRO AO DELETAR TRABALHO: {exc}")
        flash("Não foi possível remover o trabalho.", "danger")
    return redirect(url_for("portfolio_tatuador.mostrar_portfolio"))


@portfolio_bp.route("/tatuadores/<string:id_tatuador>/portfolio")
def portfolio_publico(id_tatuador):
    """Portfólio visto pelo cliente (só leitura). Precisa de alguém logado."""
    if not session.get("cliente") and not tatuador_logado():
        return redirect(url_for("login_cliente.selecionar_perfil"))

    try:
        tatuador = buscar_tatuador(id_tatuador)
        trabalhos = listar_trabalhos(id_tatuador) if tatuador else []
    except Exception as exc:
        print(f">>> ERRO AO BUSCAR PORTFÓLIO PÚBLICO: {exc}")
        abort(404)

    if not tatuador:
        abort(404)

    # Quem chegou pelo "Ver como cliente" volta para o próprio portfólio.
    voltar = (
        url_for("portfolio_tatuador.mostrar_portfolio")
        if tatuador_logado() and tatuador_logado()["id"] == id_tatuador
        else (
            url_for("agendamento_cliente.agendar_sessao")
            if "agendamento_cliente.agendar_sessao" in current_app.view_functions
            else url_for("login_cliente.home_cliente")
        )
    )
    return render_template(
        "portfolio_tatuador/portfolio_publico.html",
        tatuador=tatuador,
        trabalhos=trabalhos,
        voltar=voltar,
    )
