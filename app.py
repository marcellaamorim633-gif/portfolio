from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        # Login de teste
        if email == "admin@astech.com" and senha == "123456":
            return redirect(url_for("acesso"))

        return "Usuário ou senha inválidos"

    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":
        # Por enquanto apenas volta para o login
        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/acesso")
def acesso():
    return render_template("acesso.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)