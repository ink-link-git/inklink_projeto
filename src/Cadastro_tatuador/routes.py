from flask import Blueprint, render_template, redirect
from forms import RegisterForm

# Criamos um Blueprint chamado 'main'
main_bp = Blueprint('main', __name__)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect('/template')
    
    return render_template('register.html', form=form)

@main_bp.route('/template')
def template():
    return render_template('index.html')