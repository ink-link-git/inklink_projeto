from flask import Blueprint, render_template

from shared.auth import tatuador_required

# Blueprint com o que é comum às telas: CSS do layout do tatuador e telas "em breve".
bp = Blueprint(
    "shared",
    __name__,
    static_folder="static",
    static_url_path="/static/shared",
)

SECOES_EM_BREVE = {
    "perfil": "Meu Perfil",
    "agenda": "Minha Agenda",
    "portfolio": "Meu Portfólio",
    "anamnese": "Fichas de Anamnese",
    "estoque": "Estoque",
    "configuracoes": "Configurações",
}


@bp.route("/tatuador/em-breve/<secao>")
@tatuador_required
def em_breve(secao):
    titulo = SECOES_EM_BREVE.get(secao, "Em breve")
    return render_template("shared/tatuador_em_breve.html", titulo=titulo, ativo=secao)
