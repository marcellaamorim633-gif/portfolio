from flask import Flask, render_template, request, redirect, url_for,session
from dotenv import load_dotenv
import os
import pymysql

# Carregar o .env
load_dotenv()

# Conectar ao banco
conexao = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    connect_timeout=10,
    autocommit=True
)

cursor = conexao.cursor()

app = Flask(__name__)
app.secret_key = "as_analytics_2026"


# =========================
# LOGIN
# =========================
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

            session["usuario_id"] = usuario["id"]
            session["nome"] = usuario["nome"]
            session["email"] = usuario["email"]
            session["cargo"] = usuario["cargo"]
            session["nivel_permissao"] = usuario["nivel_permissao"]
            session["empresa_id"] = usuario["empresa_id"]
            

            return redirect(url_for("portal"))

        return "Usuário ou senha inválidos"

    return render_template("index.html")


# =========================
# PORTAL
# =========================
@app.route("/portal")
def portal():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    return render_template("portal.html")


# =========================
# CADASTRO
# =========================
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]
        empresa = request.form["empresa"]
        razao_social = request.form["razao_social"]
        cnpj = request.form["cnpj"]
        email = request.form["email"]
        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]

        if senha != confirmar_senha:
            return "As senhas não coincidem."

        cursor.execute("""
            INSERT INTO empresas
            (nome_fantasia, razao_social, cnpj)
            VALUES (%s, %s, %s)
        """, (
            empresa,
            razao_social,
            cnpj
        ))

        empresa_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO usuarios
            (nome, email, senha, cargo, nivel_permissao, empresa_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            nome,
            email,
            senha,
            "Administrador",
            "ADMIN",
            empresa_id
        ))

        conexao.commit()

        return redirect(url_for("login"))

    return render_template("cadastro.html")


# =========================
# RECUPERAR SENHA
# =========================
@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    if request.method == "POST":
        # Depois faremos o envio do e-mail
        return redirect(url_for("login"))

    return render_template("recuperar.html")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# =========================
# EXECUTAR
# =========================
if __name__ == "__main__":
    app.run(debug=True, port=5001)