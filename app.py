from flask import Flask, render_template, request, redirect, url_for

from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

print("HOST:", os.getenv("DB_HOST"))
print("PORT:", os.getenv("DB_PORT"))
print("USER:", os.getenv("DB_USER"))
print("DB:", os.getenv("DB_NAME"))

conexao = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = conexao.cursor()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s AND senha = %s",
            (email, senha)
        )

        usuario = cursor.fetchone()

        if usuario:
            return redirect(url_for("acesso"))

        return "Usuário ou senha inválidos"

    return render_template("index.html")


@app.route("/acesso")
def acesso():
    return render_template("acesso.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s AND senha = %s",
            (email, senha)
        )

        usuario = cursor.fetchone()

        if usuario:
            return redirect(url_for("acesso"))

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