from flask import Blueprint, render_template, redirect, url_for, flash, session
from Cadastro_tatuador.forms import RegisterForm
from Cadastro_tatuador.db import supabase

# Blueprint do módulo. O static_url_path próprio evita conflito com os outros módulos.
main_bp = Blueprint(
    'cadastro_tatuador',
    __name__,
    static_folder='static',
    static_url_path='/static/cadastro_tatuador',
)


@main_bp.route('/cadastro/tatuador', methods=['GET', 'POST'])
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

            # Pega o ID único (UUID) gerado na autenticação
            id_tatuador = auth_response.user.id

            # 2. Prepara os dados do perfil (SEM a senha)
            dados_tatuador = {
                "id_tatuador": id_tatuador,  # Chave estrangeira ligada ao auth.users
                "nome": form.nome.data,
                "email": form.email.data,
                "cpf": form.cpf.data,
                "tel": form.tel.data,
                "especialidade": form.especialidade.data
            }

            # 3. Insere os dados adicionais na tabela 'tatuador'
            response = supabase.table('tatuador').insert(dados_tatuador).execute()
            print(">>> SUCESSO NO SUPABASE:", response.data)

            session['cadastro_tatuador_ok'] = True
            return redirect(url_for('cadastro_tatuador.sucesso'))

        except Exception as e:
            print(">>> ERRO DO SUPABASE:", e)
            if "already registered" in str(e).lower():
                flash("Este e-mail já está cadastrado.", "danger")
            else:
                flash("Erro ao realizar o cadastro. Verifique os dados informados.", "danger")
    else:
        if form.errors:
            print(">>> ERROS DE VALIDAÇÃO DO FORMULÁRIO:", form.errors)

    return render_template('Cadastro_tatuador/register.html', form=form)


@main_bp.route('/cadastro/tatuador/sucesso')
def sucesso():
    # Só mostra a tela de boas-vindas para quem acabou de se cadastrar.
    if not session.get('cadastro_tatuador_ok'):
        return redirect(url_for('cadastro_tatuador.register'))
    return render_template('Cadastro_tatuador/index.html')
