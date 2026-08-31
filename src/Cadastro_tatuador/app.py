from flask import  Flask, render_template, request, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Email
#criando aplicação flask
app = Flask (__name__)
app.config['SECRET_KEY'] = 'abc123'

class RegisterForm(FlaskForm):

    first_name = StringField ('Primeiro nome', validators=[DataRequired()])
    last_name = StringField ('Sobrenome')
    email = StringField ('E-mail', validators=[Email(message='Email invalido')])
    password = PasswordField ('Senha', validators=[InputRequired(), EqualTo('confirm',message= 'As senhas devem ser iguais ')])
    confirm = PasswordField ('Confirme a senha')
    submit = SubmitField ('Cadastrar')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
       return redirect('/template')
    
    return render_template('register.html', form=form)

@app.route('/template')
def template():
    return render_template('index.html')

#executando o servidor
if __name__ == '__main__':
    app.run(debug=True, port=5152) 