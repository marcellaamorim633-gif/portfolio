from datetime import datetime, timedelta
from flask import Flask, make_response, render_template, render_template_string, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do Banco de Dados SQLite interno
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metrics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Modelo da tabela de métricas no Banco de Dados
class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    referer = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


# Middleware que regista cada acesso (ignora os teus acessos se o cookie estiver ativo)
@app.before_request
def track_visitor():
    if (
        request.endpoint
        and 'static' not in request.endpoint
        and request.path != '/dash'
        and request.path != '/dash/toggle-ignore'
    ):
        if request.cookies.get('ignore_me') != 'true':
            try:
                view = PageView(
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')[:200],
                    referer=request.headers.get('Referer', '')[:200],
                )
                db.session.add(view)
                db.session.commit()
            except Exception:
                db.session.rollback()


# Rota Principal: Carrega o teu index.html completo
@app.route("/")
def home():
    return render_template("index.html")


# Rota Privada de Métricas: /dash
@app.route("/dash")
def metrics_dashboard():
    total_views = PageView.query.count()

    # Visitas de hoje em UTC
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_views = PageView.query.filter(PageView.timestamp >= today_start).count()

    # Visitas vindas do LinkedIn
    linkedin_views = PageView.query.filter(PageView.referer.like('%linkedin%')).count()

    recent_views = PageView.query.order_by(PageView.timestamp.desc()).limit(30).all()

    # Converte os registos para o Horário do Brasil (BRT = UTC - 3h)
    formatted_views = []
    for view in recent_views:
        brt_time = view.timestamp - timedelta(hours=3)
        formatted_views.append({
            'id': view.id,
            'timestamp_brt': brt_time.strftime('%d/%m/%Y %H:%M:%S'),
            'referer': view.referer,
            'user_agent': view.user_agent
        })

    is_ignored = request.cookies.get('ignore_me') == 'true'

    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Métricas de Acesso — Marcella</title>
        <style>
            body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0B172A; color: #F8FAFC; padding: 20px; margin: 0; }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { font-size: 1.4rem; color: #14B1E7; margin: 0; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 25px 0; }
            .card { background: #111F31; border: 1px solid rgba(148,163,184,0.15); border-radius: 8px; padding: 18px; }
            .card h3 { margin: 0; font-size: 0.8rem; color: #94A3B8; }
            .card p { margin: 8px 0 0; font-size: 1.8rem; font-weight: bold; color: #14B1E7; }
            .btn { background: #14B1E7; color: #0B172A; border: none; padding: 8px 14px; font-weight: bold; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 0.85rem; display: inline-block; }
            .btn-ignored { background: #22C55E; color: #0B172A; }
            .table-responsive { overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; background: #111F31; border-radius: 8px; font-size: 0.85rem; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid rgba(148,163,184,0.1); }
            th { background: #07111F; color: #94A3B8; }
            tr:hover { background: #14263B; }
            .badge { padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
            .badge-linkedin { background: rgba(10, 102, 194, 0.2); color: #38bdf8; border: 1px solid #0a66c2; }
            .badge-direct { background: rgba(148, 163, 184, 0.1); color: #94a3b8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <h1>📊 Painel Privado de Métricas</h1>
                {% if is_ignored %}
                    <a href="/dash/toggle-ignore" class="btn btn-ignored">✓ Seus acessos estão sendo ignorados</a>
                {% else %}
                    <a href="/dash/toggle-ignore" class="btn">🚫 Ignorar Meus Acessos</a>
                {% endif %}
            </div>

            <div class="cards">
                <div class="card">
                    <h3>Total de Acessos</h3>
                    <p>{{ total_views }}</p>
                </div>
                <div class="card">
                    <h3>Acessos de Hoje</h3>
                    <p>{{ today_views }}</p>
                </div>
                <div class="card">
                    <h3>Vindos do LinkedIn</h3>
                    <p>{{ linkedin_views }}</p>
                </div>
            </div>

            <h2 style="font-size: 1.1rem; color: #F8FAFC; margin-bottom: 15px;">Últimas 30 Visitas</h2>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Data / Hora (BRT)</th>
                            <th>Origem (Referer)</th>
                            <th>Navegador / Dispositivo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for view in formatted_views %}
                        <tr>
                            <td>{{ view.id }}</td>
                            <td>{{ view.timestamp_brt }}</td>
                            <td>
                                {% if view.referer and 'linkedin' in view.referer.lower() %}
                                    <span class="badge badge-linkedin">LinkedIn</span>
                                {% else %}
                                    <span class="badge badge-direct">{{ view.referer or 'Acesso Direto / PDF' }}</span>
                                {% endif %}
                            </td>
                            <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{{ view.user_agent }}">
                                {{ view.user_agent }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        total_views=total_views,
        today_views=today_views,
        linkedin_views=linkedin_views,
        formatted_views=formatted_views,
        is_ignored=is_ignored
    )


# Rota para ativar/desativar a ignorância dos teus acessos
@app.route("/dash/toggle-ignore")
def toggle_ignore():
    resp = make_response('<script>window.location.href="/dash";</script>')
    if request.cookies.get('ignore_me') == 'true':
        resp.set_cookie('ignore_me', '', expires=0)
    else:
        resp.set_cookie('ignore_me', 'true', max_age=60*60*24*365*5)
    return resp


if __name__ == "__main__":
    app.run(debug=True)