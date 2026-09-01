from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length

class RegisterForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(message='O nome é obrigatório.')])
    
    cpf = StringField('CPF', validators=[
        DataRequired(message='O CPF é obrigatório.'),
        Length(min=11, max=14, message='O CPF deve ter entre 11 e 14 caracteres.')
    ])
    
    tel = StringField('Telefone', validators=[
        DataRequired(message='O telefone é obrigatório.'),
        Length(min=10, max=15, message='Informe um telefone válido.')
    ])
    
    especialidade = StringField('Especialidade', validators=[
        DataRequired(message='A especialidade é obrigatória.')
    ])
    
    password = PasswordField('Senha', validators=[
        InputRequired(message='A senha é obrigatória.'),
        EqualTo('confirm', message='As senhas devem ser iguais.')
    ])
    
    confirm = PasswordField('Confirme a senha')
    
    submit = SubmitField('Cadastrar Tatuador')