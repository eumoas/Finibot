# 🏗️ design.md — Documento de Design Técnico
## Fini: Seu Parceiro Financeiro
**Versão:** 1.0 | **Data:** 2026-04-04

---

## 1. Visão Arquitetural

O Fini segue uma **arquitetura de camadas** (Layered Architecture) com separação clara entre:
- **Entrega (Delivery):** Telegram Bot API
- **Aplicação (Application):** FastAPI + Fluxos de conversa
- **Domínio (Domain):** Gamificação, metas, desafios
- **Infraestrutura (Infrastructure):** PostgreSQL, Redis, LLM Gateway

```
┌──────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT API                          │
│           python-telegram-bot (OSS, Apache 2.0)             │
│        Webhook (prod) ◄────────► Long Polling (dev)         │
└───────────────────────────┬──────────────────────────────────┘
                            │ Updates (mensagens, callbacks)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   FASTAPI APPLICATION                        │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Telegram   │  │   Command    │  │   Conversation     │  │
│  │  Handler   ─┼─►│   Router    ─┼─►│   Flows            │  │
│  └─────────────┘  └──────────────┘  │  • onboarding      │  │
│                                     │  • qa_engine        │  │
│                                     │  • simulator        │  │
│                                     │  • challenges       │  │
│                                     └────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   DOMAIN SERVICES                    │   │
│  │  GamificationEngine │ GoalManager │ ChallengeService │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────┬───────────────────────┬───────────────────────┘
               │                       │
               ▼                       ▼
┌─────────────────────────┐  ┌─────────────────────────────────┐
│   INFRASTRUCTURE        │  │         LLM GATEWAY             │
│  ┌────────────────────┐ │  │  ┌──────────────────────────┐   │
│  │  PostgreSQL 16     │ │  │  │  Groq API (primary)      │   │
│  │  SQLAlchemy ORM    │ │  │  │  llama-3.3-70b-versatile │   │
│  │  Alembic Migrations│ │  │  └──────────┬───────────────┘   │
│  └────────────────────┘ │  │             │ fallback          │
│  ┌────────────────────┐ │  │  ┌──────────▼───────────────┐   │
│  │  Redis 7 OSS       │ │  │  │  Ollama (local)          │   │
│  │  Rate Limiting     │ │  │  │  gemma3:4b               │   │
│  │  Session Cache     │ │  │  └──────────────────────────┘   │
│  └────────────────────┘ │  └─────────────────────────────────┘
└─────────────────────────┘
```

---

## 2. Estrutura de Diretórios

```
finibot/
├── app/
│   ├── main.py                     # FastAPI app + registro dos handlers
│   ├── api/
│   │   ├── telegram_handler.py     # Ponto de entrada: webhook e polling
│   │   ├── command_router.py       # /start /ajuda /simular /desafio /meta /pontos
│   │   └── health.py               # GET /health
│   ├── core/
│   │   ├── config.py               # pydantic-settings: vars de ambiente
│   │   ├── database.py             # SQLAlchemy async engine + session factory
│   │   └── redis_client.py         # Conexão Redis (aioredis)
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── user.py                 # User, UserProfile
│   │   ├── goal.py                 # Goal
│   │   ├── challenge.py            # Challenge, UserChallenge
│   │   └── message_log.py          # MessageLog
│   ├── repositories/               # Data Access Layer
│   │   ├── user_repo.py
│   │   ├── goal_repo.py
│   │   └── challenge_repo.py
│   ├── services/                   # Business Logic
│   │   ├── llm_service.py          # LLM Gateway (Groq + Ollama)
│   │   ├── telegram_service.py     # Envio de mensagens, InlineKeyboard
│   │   ├── session_service.py      # Contexto de conversa (Redis)
│   │   ├── gamification.py         # Pontos, níveis, streaks
│   │   └── challenge_service.py    # CRUD + lógica de desafios semanais
│   ├── flows/                      # Conversation Flows (estado de máquina simples)
│   │   ├── onboarding.py           # F1: Quiz diagnóstico
│   │   ├── qa_engine.py            # F2: Perguntas livres → LLM
│   │   ├── simulator.py            # F3: Simular guardar/gastar/investir
│   │   └── goal_flow.py            # F6: Criar e acompanhar metas
│   └── prompts/
│       ├── system_prompt.py        # Persona Fini (versionada e testável)
│       └── templates.py            # Respostas fixas (onboarding, menus, erros)
├── migrations/                     # Alembic
│   ├── env.py
│   └── versions/
├── tests/
│   ├── unit/
│   │   ├── test_gamification.py
│   │   ├── test_flows.py
│   │   └── test_llm_service.py
│   ├── integration/
│   │   └── test_api.py
│   └── load/
│       └── webhook_test.js         # k6 load test
├── docker-compose.yml
├── docker-compose.test.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── .github/
    └── workflows/
        └── ci.yml                  # GitHub Actions: lint + test + deploy
```

---

## 3. Modelos de Dados

### 3.1 Diagrama Entidade-Relacionamento

```
┌──────────────┐         ┌──────────────────────┐
│    users     │         │       goals           │
├──────────────┤    1:N  ├──────────────────────┤
│ id (UUID) PK │────────►│ id (UUID) PK          │
│ telegram_id  │         │ user_id (UUID) FK     │
│ username     │         │ title                 │
│ first_name   │         │ target_amount         │
│ age          │         │ current_amount        │
│ points       │         │ deadline              │
│ level        │         │ completed             │
│ onboarded    │         │ created_at            │
│ streak_days  │         └──────────────────────┘
│ last_seen_at │
│ created_at   │         ┌──────────────────────┐
└──────┬───────┘         │     user_challenges   │
       │                 ├──────────────────────┤
       │   N:M (via      │ user_id (UUID) FK     │
       └────────────────►│ challenge_id (UUID) FK│
                         │ accepted_at           │
                         │ completed_at          │
                         └──────────┬───────────┘
                                    │ N:1
                         ┌──────────▼───────────┐
                         │      challenges       │
                         ├──────────────────────┤
                         │ id (UUID) PK          │
                         │ title                 │
                         │ description           │
                         │ points_reward         │
                         │ category              │
                         │ difficulty            │
                         │ week_number           │
                         └──────────────────────┘

┌──────────────────────────────────────────────┐
│               message_logs                   │
├──────────────────────────────────────────────┤
│ id (UUID) PK                                  │
│ user_id (UUID) FK → users.id                 │
│ role  VARCHAR(10)  -- 'user' | 'assistant'   │
│ content  TEXT                                │
│ created_at  TIMESTAMP                        │
│ (índice em user_id + created_at DESC)        │
└──────────────────────────────────────────────┘
```

### 3.2 Schema SQL Completo

```sql
-- Extensão para UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Usuários
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id     BIGINT UNIQUE NOT NULL,
    username        VARCHAR(100),
    first_name      VARCHAR(100),
    age             INTEGER,
    school          VARCHAR(200),
    profile_type    VARCHAR(20) DEFAULT 'iniciante',
      -- 'iniciante' | 'em_desenvolvimento' | 'avancado'
    points          INTEGER DEFAULT 0 CHECK (points >= 0),
    level           INTEGER DEFAULT 1 CHECK (level BETWEEN 1 AND 5),
    onboarded       BOOLEAN DEFAULT FALSE,
    streak_days     INTEGER DEFAULT 0,
    last_seen_at    TIMESTAMP,
    monthly_report  BOOLEAN DEFAULT TRUE,  -- opt-in relatório
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Metas Financeiras
CREATE TABLE goals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(200) NOT NULL,
    target_amount   DECIMAL(10,2) NOT NULL CHECK (target_amount > 0),
    current_amount  DECIMAL(10,2) DEFAULT 0 CHECK (current_amount >= 0),
    deadline        DATE,
    completed       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Biblioteca de Desafios
CREATE TABLE challenges (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(200) NOT NULL,
    description     TEXT NOT NULL,
    points_reward   INTEGER NOT NULL DEFAULT 50,
    category        VARCHAR(50) NOT NULL,
      -- 'orcamento' | 'poupanca' | 'credito' | 'investimento' | 'consumo' | 'matematica'
    difficulty      VARCHAR(10) NOT NULL,
      -- 'facil' | 'medio' | 'dificil'
    active          BOOLEAN DEFAULT TRUE
);

-- Progresso em Desafios
CREATE TABLE user_challenges (
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_id    UUID NOT NULL REFERENCES challenges(id),
    accepted_at     TIMESTAMP DEFAULT NOW(),
    completed_at    TIMESTAMP,
    week_number     INTEGER NOT NULL,  -- ISO week number
    PRIMARY KEY (user_id, challenge_id, week_number)
);

-- Log de Mensagens (janela de contexto para o LLM)
CREATE TABLE message_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role            VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Índices de performance
CREATE INDEX idx_message_logs_user_created ON message_logs(user_id, created_at DESC);
CREATE INDEX idx_goals_user_active ON goals(user_id) WHERE completed = FALSE;
CREATE INDEX idx_users_telegram_id ON users(telegram_id);

-- Trigger: atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## 4. Design dos Serviços

### 4.1 LLM Gateway

```python
# app/services/llm_service.py
from abc import ABC, abstractmethod
from typing import Protocol
import httpx

class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],   # [{"role": "user", "content": "..."}]
        system: str             # system prompt
    ) -> str: ...

class GroqProvider(LLMProvider):
    """Primary: Groq API com Llama 3.3 70B (OSS, free tier)"""
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    MAX_TOKENS = 300  # manter respostas curtas

class OllamaProvider(LLMProvider):
    """Fallback: Ollama local com Gemma 3 4B"""
    BASE_URL = "http://ollama:11434/api/chat"
    MODEL = "gemma3:4b"

class LLMGateway:
    """Circuit breaker simples com fallback automático"""
    def __init__(self):
        self.primary = GroqProvider()
        self.fallback = OllamaProvider()
        self._primary_failures = 0
        self._circuit_open = False

    async def chat(self, messages: list[dict], system: str) -> str:
        if not self._circuit_open:
            try:
                response = await self.primary.chat(messages, system)
                self._primary_failures = 0
                return response
            except Exception:
                self._primary_failures += 1
                if self._primary_failures >= 3:
                    self._circuit_open = True  # abre circuito por 5 min
        return await self.fallback.chat(messages, system)
```

### 4.2 Session Service (Contexto de Conversa)

```python
# app/services/session_service.py
# Armazena contexto no Redis com TTL de 1 hora
# Janela deslizante: últimas 10 mensagens do usuário

KEY_PATTERN = "session:{telegram_id}"
TTL_SECONDS = 3600  # 1 hora de inatividade

class SessionService:
    async def get_context(self, telegram_id: int) -> list[dict]:
        """Retorna últimas 10 mensagens para o LLM"""
        ...

    async def add_message(self, telegram_id: int, role: str, content: str):
        """Adiciona mensagem e mantém janela de 10"""
        ...

    async def clear(self, telegram_id: int):
        """Limpa sessão (ex: /recomecar)"""
        ...
```

### 4.3 Gamification Engine

```python
# app/services/gamification.py

LEVELS = {
    1: {"name": "🌱 Aprendiz",   "min_points": 0},
    2: {"name": "📚 Estudante",   "min_points": 200},
    3: {"name": "💡 Consciente",  "min_points": 500},
    4: {"name": "🚀 Investidor",  "min_points": 1000},
    5: {"name": "🏆 Mestre",      "min_points": 2000},
}

POINTS = {
    "onboarding_complete": 100,
    "quiz_correct":         20,
    "challenge_easy":       50,
    "challenge_medium":    100,
    "challenge_hard":      150,
    "goal_created":         30,
    "goal_completed":       50,
    "streak_7days":         80,
}

class GamificationEngine:
    async def award(self, user_id: UUID, action: str) -> dict:
        """
        Retorna: {"points_gained": int, "new_total": int,
                  "level_up": bool, "new_level": dict | None}
        """
        ...

    def calculate_level(self, points: int) -> int:
        """Determina nível baseado nos pontos"""
        ...
```

### 4.4 Command Router

```python
# app/api/command_router.py
# Tabela de roteamento de comandos e intenções

COMMAND_MAP = {
    "/start":   flows.onboarding.handle,
    "/simular": flows.simulator.handle,
    "/desafio": services.challenge_service.handle,
    "/meta":    flows.goal_flow.handle_create,
    "/metas":   flows.goal_flow.handle_list,
    "/pontos":  services.gamification.handle_status,
    "/ajuda":   templates.send_help_menu,
}

async def route(update: Update, context: CallbackContext):
    user = await get_or_create_user(update.effective_user)
    
    # Prioridade de roteamento:
    # 1. Usuário em estado de onboarding → onboarding flow
    # 2. Comando explícito (/cmd) → COMMAND_MAP
    # 3. Callback de InlineKeyboard → handler registrado
    # 4. Mensagem de texto livre → qa_engine (LLM)
    ...
```

---

## 5. Design da Persona Fini (System Prompt)

```python
# app/prompts/system_prompt.py

def build_system_prompt(user: User) -> str:
    return f"""
Você é o Fini, parceiro de educação financeira de jovens brasileiros de 13 a 21 anos.

IDENTIDADE:
- Nome: Fini | Tom: amigável, direto, levemente bem-humorado
- Pense em si como um colega mais experiente, nunca como um banco ou consultor formal

REGRAS DE COMUNICAÇÃO:
1. Respostas com no máximo 150 palavras
2. Use no máximo 3 emojis por mensagem
3. NUNCA use: 'liquidez', 'portfólio', 'hedge', 'alavancagem', jargões formais
4. SEMPRE use: exemplos em reais ("tipo, se você guardar R$5 por dia por 1 ano...")
5. Termine com 1 pergunta reflexiva OU 1 mini-desafio concreto
6. Se não souber, diga: "Boa pergunta! Posso pesquisar isso melhor pra você"
7. Se a pergunta fugir de finanças, redirecione gentilmente

PROIBIÇÕES:
- Nunca recomendar produto financeiro específico ("compre ação X", "invista no banco Y")
- Nunca opinar sobre criptomoedas como investimento recomendado
- Nunca inventar dados (taxa Selic, inflação) — use "verifique na calculadora do BC"

PEDAGO GIA:
- Celebre conquistas: "Arrasou! Isso é coisa de 1% da galera da sua idade 🔥"
- Acolha erros: "Sem julgamento aqui. Vamos entender o que aconteceu?"
- Inspire ação: sempre termine com algo pequeno e concreto para fazer

CONTEXTO DO USUÁRIO:
- Nome: {user.first_name}
- Nível: {LEVELS[user.level]['name']} ({user.points} pontos)
- Perfil: {user.profile_type}
""".strip()
```

---

## 6. Fluxo de Onboarding (Máquina de Estado)

```
Estado inicial: NEW_USER
        │
        ▼
[STEP_WELCOME]
  Bot: "Oi {nome}! Sou o Fini 👋..."
  → Aguarda qualquer mensagem
        │
        ▼
[STEP_ASK_NAME]
  Bot: "Qual é o seu nome?"
  → Usuário digita nome → salva em users.first_name
        │
        ▼
[STEP_ASK_AGE]
  Bot: "Quantos anos você tem?"
  → Usuário digita idade → valida 10–30 → salva em users.age
        │
        ▼
[STEP_QUIZ_Q1]   (InlineKeyboard)
  Bot: "Quando você recebe grana, o que faz primeiro?"
  → [A] [B] [C] → callback_query → salva resposta
        │
        ▼
[STEP_QUIZ_Q2]   (InlineKeyboard)
  Bot: "Você já ouviu falar em juros compostos?"
  → [A] [B] [C] → callback_query
        │
        ▼
[STEP_QUIZ_Q3]   (InlineKeyboard)
  Bot: "Você tem algum objetivo financeiro agora?"
  → [A] [B] [C] → callback_query
        │
        ▼
[STEP_RESULT]
  → Calcula profile_type (Iniciante/Em Desenvolvimento/Avançado)
  → +100 pontos → users.onboarded = True
  Bot: "Diagnóstico: {perfil}. Você ganhou 100 pontos! ..."
        │
        ▼
Estado final: ONBOARDED → Roteamento normal
```

---

## 7. Infraestrutura

### 7.1 docker-compose.yml

```yaml
version: "3.9"

services:
  fini-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - PYTHONUNBUFFERED=1
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: finibot
      POSTGRES_USER: fini
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fini"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 50mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=5m
    # Para GPU: adicionar runtime: nvidia + deploy.resources

volumes:
  pgdata:
  redisdata:
  ollama_data:
```

### 7.2 .env.example

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_SECRET_TOKEN=random_secret_for_webhook_auth

# LLM
GROQ_API_KEY=your_groq_api_key
OLLAMA_BASE_URL=http://ollama:11434

# Database
DATABASE_URL=postgresql+asyncpg://fini:password@postgres:5432/finibot
POSTGRES_PASSWORD=change_me_in_production

# Redis
REDIS_URL=redis://redis:6379/0

# App
ENVIRONMENT=development              # development | production
DEBUG=true
ADMIN_API_KEY=change_me_in_production
MAX_MESSAGES_PER_HOUR=30
CONTEXT_WINDOW_SIZE=10               # últimas N mensagens para o LLM
```

### 7.3 Pipeline CI/CD (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_PASSWORD: test, POSTGRES_DB: finibot_test }
      redis:
        image: redis:7-alpine

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: black --check app/        # lint
      - run: ruff app/                 # static analysis
      - run: pytest tests/unit/ -v --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4

  deploy:
    needs: lint-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env: { FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }} }
```

---

## 8. Decisões de Design (ADR — Architecture Decision Records)

### ADR-01: Telegram em vez de WhatsApp
**Status:** Aceito  
**Contexto:** WhatsApp exige aprovação de conta Business, número dedicado e compliance rigoroso (Meta).  
**Decisão:** Usar Telegram Bot API — gratuito, sem aprovação, InlineKeyboard nativo, long polling para dev.  
**Consequências:** Alcance menor no Brasil (WhatsApp > Telegram), compensado pela velocidade de MVP.

### ADR-02: Groq API como LLM primário
**Status:** Aceito  
**Contexto:** Precisamos de LLM com boa qualidade em PT-BR, baixa latência e custo zero no MVP.  
**Decisão:** Groq + `llama-3.3-70b-versatile` (modelo OSS). Free tier: 14.4k tokens/min, < 500ms.  
**Consequências:** Dependência de terceiro; mitigado com fallback Ollama local.

### ADR-03: Long Polling em dev, Webhook em produção
**Status:** Aceito  
**Contexto:** Webhook Telegram exige HTTPS, difícil de configurar localmente.  
**Decisão:** `ENVIRONMENT=development` → Long Polling automático; produção → Webhook HTTPS.  
**Consequências:** Zero fricção no desenvolvimento local, comportamento idêntico em produção.

### ADR-04: Janela de contexto de 10 mensagens
**Status:** Aceito  
**Contexto:** Enviar todo o histórico ao LLM aumenta latência e custo de tokens.  
**Decisão:** Manter apenas as últimas 10 mensagens no contexto (Redis), persistir tudo no PostgreSQL.  
**Consequências:** Bot pode "esquecer" contexto antigo; aceitável para conversas jovens que tendem a ser episódicas.

### ADR-05: Identificação por telegram_id (sem login)
**Status:** Aceito  
**Contexto:** Pedir login/senha aumenta fricção e risco de segurança.  
**Decisão:** `telegram_id` (chat_id) como identificador único imutável do usuário.  
**Consequências:** Sem autenticação extra; risco baixo dado que o acesso ao app Telegram já é autenticado.

---

## 9. Requisitos de Dependências

```txt
# requirements.txt
fastapi==0.115.*
uvicorn[standard]==0.29.*
python-telegram-bot==21.*        # Telegram Bot API SDK (OSS)
sqlalchemy[asyncio]==2.0.*
asyncpg==0.29.*                  # Driver async PostgreSQL
alembic==1.13.*
redis[hiredis]==5.0.*
pydantic-settings==2.2.*
httpx==0.27.*                    # HTTP client async para Groq/Ollama
tenacity==8.3.*                  # Retry logic para LLM calls

# requirements-dev.txt
pytest==8.*
pytest-asyncio==0.23.*
pytest-cov==5.*
httpx                            # já no prod, usado em testes
black==24.*
ruff==0.4.*
factory-boy==3.*                 # fixtures de teste
```

---

*Fini — Seu Parceiro Financeiro | design.md v1.0 | 2026-04-04*
