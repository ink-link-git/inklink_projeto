from flask import Flask
from routes import main_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc123'

# Registra as rotas na aplicação
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5152)