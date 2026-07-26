from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import pymysql


# =========================
# CONFIGURAÇÕES
# =========================

load_dotenv()


# =========================
# CONEXÃO COM O BANCO
# =========================

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

        # Busca o usuário pelo e-mail
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s",
            (email,)
        )

        usuario = cursor.fetchone()

        # Verifica o usuário e compara a senha com o HASH salvo no banco
        if usuario and check_password_hash(usuario["senha"], senha):

            # Salva os dados do usuário na sessão
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

    # Impede acesso sem login
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

        # Transforma a senha em HASH antes de salvar
        senha = generate_password_hash(senha)

        # Cria a empresa
        cursor.execute("""
            INSERT INTO empresas
            (nome_fantasia)
            VALUES (%s)
        """, (
            empresa,
        ))

        empresa_id = cursor.lastrowid

        # Cria o primeiro usuário como ADMIN
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

        # Futuramente será implementado o envio de e-mail
        return redirect(url_for("login"))

    return render_template("recuperar.html")


# =========================
# USUÁRIOS
# =========================

@app.route("/usuarios")
def usuarios():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    # Apenas ADMIN pode gerenciar usuários
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


# =========================
# ADICIONAR USUÁRIO
# =========================

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

        # Nunca salvar a senha original no banco
        senha = generate_password_hash(senha)

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


# =========================
# EDITAR USUÁRIO
# =========================

@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session["nivel_permissao"] != "ADMIN":
        return "Acesso negado."

    # Busca apenas usuários da mesma empresa
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


# =========================
# EXCLUIR USUÁRIO
# =========================

@app.route("/usuarios/excluir/<int:id>")
def excluir_usuario(id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session["nivel_permissao"] != "ADMIN":
        return "Acesso negado."

    # Impede que o usuário exclua a própria conta
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
# SOLICITAR USUÁRIO
# =========================

@app.route("/solicitar-usuario", methods=["GET", "POST"])
def solicitar_usuario():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    # Apenas GERENTE pode solicitar novos usuários
    if session["nivel_permissao"] != "GERENTE":
        return "Acesso negado."

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        cargo = request.form["cargo"]

        # Cria uma solicitação que será analisada pelo ADMIN
        cursor.execute("""
            INSERT INTO solicitacoes
            (tipo, solicitante_id, empresa_id, nome_usuario, email_usuario, cargo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            "ADICIONAR_USUARIO",
            session["usuario_id"],
            session["empresa_id"],
            nome,
            email,
            cargo
        ))

        return render_template(
            "solicitar_usuario.html",
            sucesso="Solicitação enviada com sucesso! Aguarde a análise do administrador."
        )

    return render_template("solicitar_usuario.html")


# =========================
# SOLICITAÇÕES
# =========================

@app.route("/solicitacoes")
def solicitacoes():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    # Apenas ADMIN pode analisar solicitações
    if session["nivel_permissao"] != "ADMIN":
        return "Acesso negado."

    cursor.execute("""
        SELECT *
        FROM solicitacoes
        WHERE empresa_id = %s
        AND status = 'PENDENTE'
        ORDER BY data_criacao DESC
    """, (
        session["empresa_id"],
    ))

    solicitacoes = cursor.fetchall()

    return render_template(
        "solicitacoes.html",
        solicitacoes=solicitacoes
    )


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