from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/projetos/acompanhamento-wms")
def acompanhamento_wms():
    return render_template("projetos/acompanhamento_wms.html")


@app.route("/projetos/projeto")
def projeto():
    return render_template("projetos/projeto.html")


if __name__ == "__main__":
    app.run(debug=True)
