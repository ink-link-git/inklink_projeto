from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


def gerar_iniciais(nome):
    partes = nome.split()
    if len(partes) > 1:
        return (partes[0][0] + partes[-1][0]).upper()
    return nome[:2].upper()


@app.route("/")
def inicio():
    return redirect(url_for("perfil"))


@app.route("/perfil")
def perfil():
    nome = "Fer Art"  # depois, virá do banco de dados
    return render_template(
        "perfil.html",
        nome_tatuador=nome,
        iniciais=gerar_iniciais(nome),
    )


if __name__ == "__main__":
    app.run(debug=True)