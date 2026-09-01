from flask import Blueprint, render_template, redirect, url_for
from forms import RegisterForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return redirect(url_for('main.register'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Apenas valida os campos e envia para a próxima tela sem salvar no banco
        return redirect(url_for('main.template'))
    
    return render_template('register.html', form=form)

@main_bp.route('/template')
def template():
    return render_template('index.html')