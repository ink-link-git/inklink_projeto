from flask import Blueprint, render_template, redirect, url_for, flash, session
from forms import RegisterForm, LoginForm
from db import supabase

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if 'usuario_logado' in session:
        return redirect(url_for('main.home_logada'))
    return redirect(url_for('main.login'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
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

            id_tatuador = auth_response.user.id

            dados_tatuador = {
                "id_tatuador": id_tatuador,
                "nome": form.nome.data,
                "email": form.email.data,
                "cpf": form.cpf.data,
                "tel": form.tel.data,
                "especialidade": form.especialidade.data
            }
            
            response = supabase.table('tatuador').insert(dados_tatuador).execute()
            print(">>> SUCESSO NO SUPABASE:", response.data)

            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('main.login'))

        except Exception as e:
            print(">>> ERRO DO SUPABASE:", e)
            flash("Erro ao realizar o cadastro. Verifique os dados informados.", "danger")
    else:
        if form.errors:
            print(">>> ERROS DE VALIDAÇÃO DO FORMULÁRIO:", form.errors)

    # Corrigido aqui para renderizar register.html
    return render_template('register.html', form=form)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            supabase.auth.sign_in_with_password({
                "email": form.email.data,
                "password": form.password.data
            })
            session['usuario_logado'] = form.email.data
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.home_logada'))
        except Exception as e:
            print(">>> ERRO NO LOGIN:", e)
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html', form=form)


@main_bp.route('/home')
def home_logada():
    if 'usuario_logado' not in session:
        flash('Você precisa fazer login primeiro.', 'warning')
        return redirect(url_for('main.login'))
    return render_template('home.html')


@main_bp.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.login'))


@main_bp.route('/template')
def template():
    return render_template('index.html')