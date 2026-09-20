from flask import Blueprint, render_template, redirect, url_for, flash
from forms import RegisterForm
from db import supabase

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return redirect(url_for('main.register'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # 1. Cria o usuário com e-mail e senha no Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": form.email.data,
                "password": form.password.data,
                "options": {
                    "data": {
                        "tipo_usuario": "tatuador",
                        "nome": form.nome.data
                    }
                }
            })

            # Verifica se o usuário foi gerado corretamente
            if not auth_response.user:
                raise Exception("Não foi possível criar o utilizador no Supabase Auth.")

            id_tatuador = auth_response.user.id

            # 2. Prepara os dados do perfil
            dados_tatuador = {
                "id_tatuador": id_tatuador,
                "nome": form.nome.data,
                "email": form.email.data,
                "cpf": getattr(form, 'cpf', None) and form.cpf.data,
                "tel": getattr(form, 'tel', None) and form.tel.data,
                "especialidade": form.especialidade.data
            }
            
            # 3. Insere os dados na tabela 'tatuador'
            response = supabase.table('tatuador').insert(dados_tatuador).execute()
            print(">>> SUCESSO NO SUPABASE:", response.data)

            return redirect(url_for('main.template'))

        except Exception as e:
            print(">>> ERRO DO SUPABASE:", e)
            flash("Erro ao realizar o cadastro. Verifique os dados informados.", "danger")
    else:
        if form.errors:
            print(">>> ERROS DE VALIDAÇÃO DO FORMULÁRIO:", form.errors)

    return render_template('register.html', form=form)

@main_bp.route('/template')
def template():
    return render_template('index.html')