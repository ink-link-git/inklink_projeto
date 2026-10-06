from flask import Flask
from routes_agenda import agenda_bp

app = Flask(__name__)

# Configurações básicas da aplicação
app.config['SECRET_KEY'] = 'chave_secreta_tcc'

# Registrar o Blueprint que contém as rotas da agenda
app.register_blueprint(agenda_bp)

if __name__ == '__main__':
    # Roda o servidor de desenvolvimento
    app.run(debug=True)