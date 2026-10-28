from flask import Blueprint, render_template, request, redirect, url_for, session
from portfolio_db import supabase
import time

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

@portfolio_bp.route('/portfolio/novo', methods=['GET', 'POST'])
def adicionar_portfolio():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        estilo = request.form.get('estilo')
        descricao = request.form.get('descricao')
        arquivo = request.files.get('imagem')
        
        try:
            id_tatuador = session.get('id_tatuador') or "083b36a4-44b2-49cf-9918-8d07f211ee00"

            if arquivo and id_tatuador:
                # Nome único para evitar conflitos
                nome_arquivo = f"{int(time.time())}_{arquivo.filename.replace(' ', '_')}"
                file_bytes = arquivo.read()

                # 1. Faz o upload para o bucket
                supabase.storage.from_('portfolio_images').upload(
                    path=nome_arquivo, 
                    file=file_bytes, 
                    file_options={"content-type": arquivo.content_type, "upsert": "true"}
                )

                # 2. Obtém a URL pública oficial do Supabase
                res_url = supabase.storage.from_('portfolio_images').get_public_url(nome_arquivo)
                
                if isinstance(res_url, dict):
                    public_url = res_url.get('publicUrl') or res_url.get('publicURL')
                else:
                    public_url = str(res_url)

                # 3. Insere os dados na tabela portfolio junto com a imagem
                supabase.table('portfolio').insert({
                    "id_tatuador": id_tatuador,
                    "titulo": titulo,
                    "estilo": estilo,
                    "descricao": descricao,
                    "caminho_imagem": public_url
                }).execute()

        except Exception as e:
            print(f"Erro ao cadastrar trabalho: {e}")

        return redirect(url_for('portfolio.mostrar_portfolio'))

    return render_template('portfolio_adicionar.html')

@portfolio_bp.route('/portfolio/deletar/<string:id_portfolio>', methods=['POST'])
def deletar_portfolio(id_portfolio):
    try:
        supabase.table('portfolio').delete().eq('id_portfolio', id_portfolio).execute()
    except Exception as e:
        print(f"Erro ao deletar trabalho: {e}")
    return redirect(url_for('portfolio.mostrar_portfolio'))