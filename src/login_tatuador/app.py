import os
from flask import Flask
from dotenv import load_dotenv
from login_tatuador.routes import main_bp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5152)