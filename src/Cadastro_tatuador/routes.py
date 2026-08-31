from flask import Blueprint, render_template, redirect
from forms import RegisterForm

main_bp = Blueprint('main', __name__)

# Rota raiz para redirecionar automaticamente e evitar o erro 404 ao abrir o servidor
@main_bp.route('/')
def home():
    return redirect('/register')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect('/template')  # Redireciona para a URL '/template'
    
    return render_template('register.html', form=form)

@main_bp.route('/template')
def template():
    return render_template('index.html')