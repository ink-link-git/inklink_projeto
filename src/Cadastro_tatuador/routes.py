from flask import Blueprint, render_template, redirect, url_for
from forms import RegisterForm
from db import supabase

# 1. Cria a instância do Blueprint primeiro
main_bp = Blueprint('main', __name__)

# 2. Define as rotas abaixo
@main_bp.route('/')
def home():
    return redirect(url_for('main.register'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            dados = {
                "nome": form.nome.data,
                "cpf": form.cpf.data,
                "tel": form.tel.data,
                "especialidade": form.especialidade.data,
                "senha": form.password.data  # Usando 'password' conforme o seu forms.py
            }
            
            # Substitua 'usuarios' pelo nome EXATO da sua tabela no Supabase
            response = supabase.table('tatuador').insert(dados).execute()
            print(">>> SUCESSO NO SUPABASE:", response.data)

            return redirect(url_for('main.template'))

        except Exception as e:
            print(">>> ERRO DO SUPABASE:", e)
    else:
        if form.errors:
            print(">>> ERROS DE VALIDAÇÃO DO FORMULÁRIO:", form.errors)

    return render_template('register.html', form=form)

@main_bp.route('/template')
def template():
    return render_template('index.html')