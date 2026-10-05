import os
from flask import Flask
from dotenv import load_dotenv
from routes import bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave_secreta_padrao")

    # Registro do Blueprint único
    app.register_blueprint(bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)