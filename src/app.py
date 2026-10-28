"""Ponto de entrada único do InkLink.

Cada pasta de src/ continua sendo um módulo independente (routes, forms, db,
templates e static próprios). Este arquivo só junta todos eles em uma única
aplicação Flask, para que as telas consigam navegar entre si.

Telas: perfil, login/cadastro (cliente e tatuador), agendar sessão, agenda do
tatuador, portfólio e fichas de anamnese.

Para rodar:
    cd src
    python app.py
"""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, session
from jinja2 import FileSystemLoader, PrefixLoader

SRC_DIR = Path(__file__).resolve().parent

# Módulos que têm telas: pasta -> (arquivo de rotas, nome do blueprint nesse arquivo).
# O nome da pasta também é o prefixo usado nos templates:
# render_template("login_cliente/perfil.html") -> src/login_cliente/templates/perfil.html
#
# Só entra no sistema o módulo cuja pasta existe em src/. Assim cada módulo pode chegar
# ao projeto em um PR diferente: as telas que dependem de um módulo ausente
# (barra lateral, botões) simplesmente mostram "em breve" ou escondem o atalho.
MODULOS = {
    "shared": ("shared.routes", "bp"),
    "login_cliente": ("login_cliente.routes", "bp"),
    "login_tatuador": ("login_tatuador.routes", "main_bp"),
    "Cadastro_tatuador": ("Cadastro_tatuador.routes", "main_bp"),
    "agendamento_cliente": ("agendamento_cliente.routes", "bp"),
    "agendamento_tatuador": ("agendamento_tatuador.routes", "agenda_bp"),
    "portfolio_tatuador": ("portfolio_tatuador.routes", "portfolio_bp"),
    "gestao_anamnese": ("gestao_anamnese.routes", "bp"),
}


def modulos_presentes():
    return [nome for nome in MODULOS if (SRC_DIR / nome).is_dir()]


def create_app():
    # O .env fica na raiz do projeto. Precisa ser carregado antes de importar
    # os módulos, porque cada db.py lê as variáveis assim que é importado.
    load_dotenv(SRC_DIR.parent / ".env")

    app = Flask(__name__, static_folder=None)

    secret_key = os.getenv("FLASK_SECRET_KEY")
    if not secret_key:
        # Sem chave fixa as sessões (login) se perdem a cada reinício do servidor.
        secret_key = secrets.token_hex(32)
        print(">>> AVISO: FLASK_SECRET_KEY não definida no .env; usando uma chave temporária.")
    app.config["SECRET_KEY"] = secret_key

    # Vários módulos têm templates com o mesmo nome (index.html, por exemplo).
    # O prefixo evita que um sobrescreva o outro, sem precisar mover arquivos.
    app.jinja_loader = PrefixLoader(
        {nome: FileSystemLoader(str(SRC_DIR / nome / "templates")) for nome in modulos_presentes()}
    )

    # Limite de upload (portfólio e referências): 4 imagens de 5 MB + folga.
    app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

    from shared.utils import formatar_data_hora, formatar_dia, quando
    app.jinja_env.filters["datahora"] = formatar_data_hora
    app.jinja_env.filters["dia"] = formatar_dia
    app.jinja_env.filters["quando"] = quando

    # O layout do tatuador sempre sabe quem está logado, sem cada rota precisar passar.
    @app.context_processor
    def dados_do_tatuador():
        return {"tatuador": session.get("tatuador")}

    # Registra cada módulo que existe em src/
    from importlib import import_module

    for nome in modulos_presentes():
        caminho, atributo = MODULOS[nome]
        app.register_blueprint(getattr(import_module(caminho), atributo))

    # Ajudantes de template para links entre módulos que podem não estar instalados:
    #   tem_rota('agendamento_cliente.agendar_sessao')            -> True/False
    #   rota('portfolio_tatuador.mostrar_portfolio', 'portfolio')  -> link, ou "em breve" se faltar
    @app.template_global()
    def tem_rota(endpoint):
        return endpoint in app.view_functions

    @app.template_global()
    def rota(endpoint, secao=None, **valores):
        from flask import url_for
        if endpoint in app.view_functions:
            return url_for(endpoint, **valores)
        if secao and "shared.em_breve" in app.view_functions:
            return url_for("shared.em_breve", secao=secao)
        return "#"

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
