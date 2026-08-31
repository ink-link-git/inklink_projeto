from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Email

class RegisterForm(FlaskForm):
    first_name = StringField('Primeiro nome', validators=[DataRequired()])
    last_name = StringField('Sobrenome')
    email = StringField('E-mail', validators=[Email(message='Email invalido')])
    password = PasswordField('Senha', validators=[InputRequired(), EqualTo('confirm', message='As senhas devem ser iguais')])
    confirm = PasswordField('Confirme a senha')
    submit = SubmitField('Cadastrar')