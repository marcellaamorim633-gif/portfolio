# Portfólio — Marcella Amorim

Portfólio profissional responsivo em Flask, HTML, CSS e JavaScript.

## Executar localmente

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Acesse `http://127.0.0.1:5000`.

## Antes de publicar

- Troque `SEU_EMAIL_AQUI` no `templates/index.html` pelo e-mail profissional correto.
- Atualize os botões de demonstração/código quando houver links públicos seguros.
- Não publique credenciais, dados reais de clientes ou informações internas de empresas.

## Hospedagem

Para um serviço que aceite Flask, comando de build: `pip install -r requirements.txt`; comando de inicialização: `gunicorn app:app`.
