# Arquivo principal do Flask
from flask import Flask, redirect, url_for
from portfolio_bp import portfolio_bp

app = Flask(__name__)

# Registrando o blueprint corrigido
app.register_blueprint(portfolio_bp)

@app.route('/')
def index():
    return redirect(url_for('portfolio.mostrar_portfolio'))

if __name__ == '__main__':
    app.run(debug=True)