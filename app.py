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
        email = request.form["email"]
        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]

        if senha != confirmar_senha:
            return "As senhas não coincidem."

        cursor.execute("""
            INSERT INTO empresas
            (nome_fantasia)
            VALUES (%s)
        """, (
            empresa,
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



@app.route("/usuarios")
def usuarios():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session["nivel_permissao"] != "ADMIN":
        return "Acesso negado."

    cursor.execute("""
        SELECT id, nome, email, cargo, nivel_permissao
        FROM usuarios
        WHERE empresa_id = %s
    """, (
        session["empresa_id"],
    ))

    usuarios = cursor.fetchall()

    return render_template(
        "usuarios.html",
        usuarios=usuarios
    )

@app.route("/usuarios/adicionar", methods=["GET", "POST"])
def adicionar_usuario():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session["nivel_permissao"] != "ADMIN":
        return "Acesso negado."

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        cargo = request.form["cargo"]
        nivel_permissao = request.form["nivel_permissao"]

        cursor.execute("""
            INSERT INTO usuarios
            (nome, email, senha, cargo, nivel_permissao, empresa_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            nome,
            email,
            senha,
            cargo,
            nivel_permissao,
            session["empresa_id"]
        ))

        return redirect(url_for("usuarios"))

    return render_template("adicionar_usuario.html")

@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session["nivel_permissao"] != "ADMIN":
        return "Acesso negado."

    cursor.execute("""
        SELECT *
        FROM usuarios
        WHERE id = %s
        AND empresa_id = %s
    """, (
        id,
        session["empresa_id"]
    ))

    usuario = cursor.fetchone()

    if not usuario:
        return "Usuário não encontrado."

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        cargo = request.form["cargo"]
        nivel_permissao = request.form["nivel_permissao"]

        cursor.execute("""
            UPDATE usuarios
            SET nome = %s,
                email = %s,
                cargo = %s,
                nivel_permissao = %s
            WHERE id = %s
            AND empresa_id = %s
        """, (
            nome,
            email,
            cargo,
            nivel_permissao,
            id,
            session["empresa_id"]
        ))

        return redirect(url_for("usuarios"))

    return render_template(
        "editar_usuario.html",
        usuario=usuario
    )

@app.route("/usuarios/excluir/<int:id>")
def excluir_usuario(id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session["nivel_permissao"] != "ADMIN":
        return "Acesso negado."

    if id == session["usuario_id"]:
        return "Você não pode excluir sua própria conta."

    cursor.execute("""
        DELETE FROM usuarios
        WHERE id = %s
        AND empresa_id = %s
    """, (
        id,
        session["empresa_id"]
    ))

    return redirect(url_for("usuarios"))


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

    