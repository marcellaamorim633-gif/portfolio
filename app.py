from datetime import datetime, timedelta
from flask import Flask, make_response, render_template_string, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metrics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    referer = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


# Middleware de contagem
@app.before_request
def track_visitor():
    # Ignora arquivos estáticos, a própria rota de estatísticas e acessos com cookie de admin
    if (
        request.endpoint
        and 'static' not in request.endpoint
        and request.path != '/dash'
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


@app.route('/')
def home():
    return render_template_string(
        '<h1>Portfólio Marcella</h1>'
    )  # Aqui chama seu render_template("index.html")


# Rota Visual e Curta: /dash
@app.route('/dash')
def metrics_dashboard():
    total_views = PageView.query.count()

    # Filtra visitas de hoje
    today_start = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_views = PageView.query.filter(
        PageView.timestamp >= today_start
    ).count()

    # Filtra acessos vindos do LinkedIn
    linkedin_views = PageView.query.filter(
        PageView.referer.like('%linkedin%')
    ).count()

    recent_views = (
        PageView.query.order_by(PageView.timestamp.desc()).limit(30).all()
    )

    is_ignored = request.cookies.get('ignore_me') == 'true'

    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Métricas de Acesso — Marcella</title>
        <style>
            body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0B172A; color: #F8FAFC; padding: 30px; margin: 0; }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { font-size: 1.5rem; color: #14B1E7; margin-bottom: 20px; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
            .card { background: #111F31; border: 1px solid rgba(148,163,184,0.15); border-radius: 8px; padding: 20px; }
            .card h3 { margin: 0; font-size: 0.85rem; color: #94A3B8; }
            .card p { margin: 10px 0 0; font-size: 1.8rem; font-weight: bold; color: #14B1E7; }
            .btn { background: #14B1E7; color: #0B172A; border: none; padding: 8px 14px; font-weight: bold; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn-ignored { background: #22C55E; color: #0B172A; }
            table { width: 100%; border-collapse: collapse; background: #111F31; border-radius: 8px; overflow: hidden; font-size: 0.85rem; }
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
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
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
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Data / Hora (UTC)</th>
                        <th>Origem (Referer)</th>
                        <th>Navegador / Dispositivo</th>
                    </tr>
                </thead>
                <tbody>
                    {% for view in recent_views %}
                    <tr>
                        <td>{{ view.id }}</td>
                        <td>{{ view.timestamp.strftime('%d/%m/%Y %H:%M:%S') }}</td>
                        <td>
                            {% if 'linkedin' in view.referer.lower() %}
                                <span class="badge badge-linkedin">LinkedIn</span>
                            {% else %}
                                <span class="badge badge-direct">{{ view.referer or 'Acesso Direto / PDF' }}</span>
                            {% endif %}
                        </td>
                        <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{{ view.user_agent }}">
                            {{ view.user_agent }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        total_views=total_views,
        today_views=today_views,
        linkedin_views=linkedin_views,
        recent_views=recent_views,
        is_ignored=is_ignored,
    )


# Rota para ligar/desligar a ignorância dos seus acessos
@app.route('/dash/toggle-ignore')
def toggle_ignore():
    resp = make_response('<script>window.location.href="/dash";</script>')
    if request.cookies.get('ignore_me') == 'true':
        resp.set_cookie('ignore_me', '', expires=0)
    else:
        resp.set_cookie('ignore_me', 'true', max_age=60 * 60 * 24 * 365 * 5)
    return resp


if __name__ == '__main__':
    app.run(debug=True)