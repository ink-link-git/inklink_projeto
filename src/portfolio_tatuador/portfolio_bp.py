# Blueprint do portfólio 
from flask import Blueprint, render_template
from portfolio_db import supabase

# Blueprint ajustado
portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/portfolio')
def mostrar_portfolio():
    try:
        response = supabase.table('portfolio').select("*").execute()
        trabalhos = response.data
    except Exception as e:
        print(f"Erro ao buscar dados do Supabase: {e}")
        trabalhos = []

    return render_template('portfolio_tela.html', trabalhos=trabalhos)