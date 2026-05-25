# Fini — Seu Parceiro Financeiro 🤖💰

Bot de educação financeira no Telegram para jovens de 13–21 anos.

## Stack

| Componente | Tecnologia |
|---|---|
| Canal | Telegram Bot API + `python-telegram-bot` |
| Backend | FastAPI (Python 3.12) |
| LLM Principal | Groq API — `llama-3.3-70b-versatile` (OSS) |
| LLM Fallback | Ollama — `gemma3:4b` (local) |
| Banco de Dados | PostgreSQL 16 |
| Cache/Fila | Redis 7 OSS |
| Orquestração | Docker Compose |
| CI/CD | GitHub Actions |

## Início Rápido

### 1. Clone e configure o ambiente

```bash
git clone https://github.com/seu-usuario/finibot.git
cd finibot
cp .env.example .env
# Edite .env com seu TELEGRAM_BOT_TOKEN e GROQ_API_KEY
```

### 2. Crie seu bot no Telegram

1. Abra o Telegram e fale com [@BotFather](https://t.me/BotFather)
2. Digite `/newbot` e siga as instruções
3. Copie o token gerado para `TELEGRAM_BOT_TOKEN` no `.env`

### 3. Obtenha sua chave Groq (LLM gratuito)

1. Acesse [console.groq.com](https://console.groq.com)
2. Crie uma conta gratuita
3. Gere uma API Key e coloque em `GROQ_API_KEY` no `.env`

### 4. Suba o ambiente

```bash
# Modo desenvolvimento (long polling — sem HTTPS necessário)
docker compose up -d postgres redis

# Instale as dependências localmente
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Rode as migrations
alembic upgrade head

# Inicie o bot (long polling automático em ENVIRONMENT=development)
python -m app.main
```

### 5. (Opcional) Suba o Ollama para fallback local

```bash
docker compose up -d ollama
# Baixe o modelo (só na primeira vez):
docker exec finibot-ollama-1 ollama pull gemma3:4b
```

## Comandos do Bot

| Comando | Descrição |
|---|---|
| `/start` | Apresentação + onboarding |
| `/simular` | Simulador financeiro |
| `/desafio` | Desafio da semana |
| `/meta` | Criar nova meta |
| `/metas` | Ver suas metas |
| `/gastos` | Abrir ajuda do controle de receitas e gastos |
| `/receita` | Registrar receitas mensais |
| `/gasto` | Registrar gastos diarios por categoria |
| `/resumo` | Ver saldo mensal e total por categoria |
| `/planilha` | Exportar controle financeiro em `.xlsx` |
| `/pontos` | Ver pontuação e nível |
| `/ajuda` | Menu de ajuda |

## Estrutura do Projeto

```
app/
├── main.py              # Entrypoint FastAPI
├── api/                 # Handlers e rotas
├── core/                # Config, DB, Redis
├── models/              # SQLAlchemy ORM
├── repositories/        # Acesso a dados
├── services/            # Lógica de negócio
├── flows/               # Fluxos de conversa
└── prompts/             # System prompt e templates
```

## Testes

```bash
pytest tests/ -v --cov=app --cov-report=html
```

## Deploy (Fly.io)

```bash
fly launch --name finibot --region gru
fly secrets set TELEGRAM_BOT_TOKEN=... GROQ_API_KEY=... ADMIN_API_KEY=...
fly deploy
```

## Documentação

- [project.md](project.md) — Visão do produto e cronograma
- [spec.md](spec.md) — Requisitos funcionais e não-funcionais
- [design.md](design.md) — Arquitetura técnica e decisões de design
- [SDD_Fini_v1.0.md](SDD_Fini_v1.0.md) — Software Design Document completo

---

*Fini — Seu Parceiro Financeiro | Open Source | 2026*
