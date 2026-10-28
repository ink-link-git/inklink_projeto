from flask import Blueprint, render_template, redirect, url_for, flash, session
from login_tatuador.forms import LoginForm
from login_tatuador.db import supabase
from shared.auth import tatuador_required, tatuador_logado

try:
    from agendamento_tatuador.forms import resumo_agenda
except ImportError:  # módulo da agenda ainda não está no projeto
    resumo_agenda = None

# Blueprint do módulo. O static_url_path próprio evita conflito com os outros módulos.
main_bp = Blueprint(
    'login_tatuador',
    __name__,
    static_folder='static',
    static_url_path='/static/login_tatuador',
)


@main_bp.route('/login/tatuador', methods=['GET', 'POST'])
def login():
    if tatuador_logado():
        return redirect(url_for('login_tatuador.home_logada'))

    form = LoginForm()

    if form.validate_on_submit():
        try:
            resposta = supabase.auth.sign_in_with_password({
                "email": form.email.data,
                "password": form.password.data
            })
        except Exception as e:
            print(">>> ERRO NO LOGIN:", e)
            flash('Usuário ou senha incorretos.', 'danger')
            return render_template('login_tatuador/login.html', form=form)

        # A conta existe no Auth, mas precisa ser de tatuador (e não de cliente).
        try:
            perfil = (
                supabase.table('tatuador')
                .select('id_tatuador, nome, email, especialidade')
                .eq('id_tatuador', resposta.user.id)
                .limit(1)
                .execute()
            )
        except Exception as e:
            print(">>> ERRO AO CONSULTAR TATUADOR:", e)
            flash('Não foi possível verificar sua conta. Tente novamente.', 'danger')
            return render_template('login_tatuador/login.html', form=form)

        if not perfil.data:
            supabase.auth.sign_out()
            flash('Esta conta não é de tatuador. Entre pela área do cliente.', 'danger')
            return render_template('login_tatuador/login.html', form=form)

        session['usuario_logado'] = form.email.data
        # Dados que as outras telas do tatuador (agenda, portfólio, fichas) usam.
        session['tatuador'] = {
            'id': perfil.data[0]['id_tatuador'],
            'nome': perfil.data[0].get('nome') or form.email.data,
            'email': form.email.data,
            'especialidade': perfil.data[0].get('especialidade'),
        }
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('login_tatuador.home_logada'))

    return render_template('login_tatuador/login.html', form=form)


@main_bp.route('/tatuador/home')
@tatuador_required
def home_logada():
    tatuador = tatuador_logado()
    resumo = resumo_agenda(tatuador['id']) if resumo_agenda else None
    return render_template('login_tatuador/home.html', tatuador=tatuador, resumo=resumo, ativo='inicio')


@main_bp.route('/logout/tatuador')
def logout():
    session.pop('usuario_logado', None)
    session.pop('tatuador', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login_tatuador.login'))
