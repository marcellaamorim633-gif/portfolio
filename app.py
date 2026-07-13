from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        if email == "admin@astech.com" and senha == "123456":
            return redirect(url_for("portal"))

        return "Usuário ou senha inválidos"

    return render_template("index.html")


@app.route("/portal")
def portal():
    return render_template("portal.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":
        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    if request.method == "POST":
        return render_template("email_enviado.html")

    return render_template("recuperar.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)