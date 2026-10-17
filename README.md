# Garimpei — Garimpo de Ofertas

Aplicação inicial para publicar ofertas no Telegram e acompanhar vendas/comissões importadas de CSVs oficiais.

## Deploy no Render

O projeto usa Python, Flask e Gunicorn. No Render, crie um Web Service ligado a este repositório, com build command `pip install -r requirements.txt` e start command `gunicorn app:app`.

Configure `APP_SECRET_KEY`, `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no painel Environment do Render. Nunca publique tokens no repositório.

## Importante

O plano gratuito do Render tem armazenamento efêmero. Não use SQLite local para manter histórico financeiro em produção; conecte um PostgreSQL persistente antes de confiar nos dados. O monitor externo não substitui banco persistente nem garante disponibilidade contínua.

As comissões devem ser importadas de relatórios oficiais dos programas de afiliados. O projeto não presume acesso automático a dados privados de vendas.
