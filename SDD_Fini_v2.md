# 📐 SDD — Software Design Document
## Fini: Seu Parceiro Financeiro
**Versão:** 2.1 | **Data:** 2026-06-24 | **Revisão de:** SDD v2.0

---

## 1. Visão Geral

O **Fini** é um chatbot educacional de finanças pessoais para jovens (13–21 anos)
distribuído via Telegram. Seu **diferencial central** é o ciclo de aprendizagem
por reflexo:

```
REGISTRAR GASTO → VER O PADRÃO → RECEBER INSIGHT → REFLETIR → MUDAR COMPORTAMENTO
```

Todos os outros módulos (Q&A, simulador, gamificação) existem para dar sentido
e motivação a esse ciclo — não como fins em si mesmos.

### 1.1 Objetivos do Projeto

1. Criar o hábito de registro financeiro diário em jovens estudantes
2. Gerar consciência do padrão de consumo via dados próprios do estudante
3. Conectar conceitos de Matemática (porcentagem, juros, proporção) à vida real
4. Produzir evidências de aprendizagem para validação acadêmica
5. Operar com custo < R$50/mês em stack 100% open-source

### 1.2 Princípios de Design

| # | Princípio | Implicação prática |
|---|---|---|
| 1 | **Registro antes de educação** | F9 é o módulo mais importante; todos os outros servem a ele |
| 2 | **Insight contextualizado** | Nunca dar teoria sem conectar ao dado real do usuário |
| 3 | **Open-Source First** | MIT/Apache/GPL antes de SaaS proprietário |
| 4 | **Custo Mínimo** | Free tiers; evitar lock-in de vendor |
| 5 | **Privacidade por Design** | Coletar apenas o necessário; nada de dados bancários |
| 6 | **Pedagogia antes de Tech** | UX do chat serve ao aprendizado |
| 7 | **Validação com Estudantes** | Evoluir a partir de evidências reais de uso |

---

## 2. Stack Tecnológica

### 2.1 Stack Final

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Canal** | Telegram Bot API | 100% gratuito, sem aprovação, adoção alta entre jovens |
| **Framework Telegram** | `python-telegram-bot` v21 (async) | OSS, melhor suporte a ConversationHandler |
| **Backend** | FastAPI (Python 3.12) | Async nativo, performance, tipagem |
| **ORM** | SQLAlchemy 2.0 + Alembic | OSS, migrations robustas |
| **Banco de dados** | PostgreSQL 16 | Confiável, free tier Supabase |
| **Cache / Rate limiting** | Redis 7 OSS | Rate limit, session cache, filas |
| **LLM Principal** | Groq API + `llama-3.3-70b-versatile` | OSS, free tier generoso, < 500ms PT-BR |
| **LLM Fallback** | Ollama + `gemma3:4b` | Offline, privacidade máxima |
| **Geração de planilha** | `openpyxl` | OSS, controle total de formatação |
| **Monitoramento** | GlitchTip (Sentry OSS clone) | Gratuito, open-source |
| **CI/CD** | GitHub Actions | Gratuito para repos públicos |
| **Containerização** | Docker Compose | Dev e produção com um comando |
| **Hospedagem** | Railway (backend) + Supabase (DB) | Deploy via GitHub, free tiers suficientes para MVP |

### 2.2 Diagrama da Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                     TELEGRAM (canal)                        │
│    Jovem digita mensagem no celular ou tablet               │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS Webhook / Long Polling
                           ▼
┌─────────────────────────────────────────────────────────────┐
│             BACKEND — FastAPI (Python 3.12)                 │
│                                                             │
│  TelegramHandler                                            │
│       │                                                     │
│       ├── IntentRouter ──► OnboardingFlow (F1)              │
│       │                ├── FinanceFlow (F9) ◄── CENTRAL     │
│       │                ├── QAEngine (F2)                    │
│       │                ├── SimulatorFlow (F3)               │
│       │                ├── ChallengeService (F4)            │
│       │                ├── GamificationEngine (F5)          │
│       │                ├── GoalManager (F6)                 │
│       │                └── ReportService (F7)               │
│       │                                                     │
│       └── LLMGateway ──► Groq (primary)                     │
│                       └► Ollama (fallback)                  │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐  ┌────────────────┐
│ PostgreSQL   │  │ Redis OSS      │
│              │  │                │
│ users        │  │ rate_limit:uid │
│ transactions │  │ session:uid    │
│ goals        │  │ streak:uid     │
│ challenges   │  │ xlsx_job:uid   │
│ user_chall.  │  └────────────────┘
│ message_logs │
└──────────────┘
```

---

## 3. Estrutura de Arquivos

```
finibot/
├── app/
│   ├── main.py                      # FastAPI entrypoint, webhook route
│   ├── api/
│   │   ├── telegram_handler.py      # Recebe updates, despacha para flows
│   │   └── health.py                # GET /health
│   ├── core/
│   │   ├── config.py                # Settings via pydantic-settings + .env
│   │   ├── database.py              # SQLAlchemy engine, SessionLocal, Base
│   │   └── redis_client.py          # Redis connection singleton
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── transaction.py           # receitas e despesas
│   │   ├── goal.py
│   │   ├── challenge.py
│   │   ├── user_challenge.py
│   │   └── message_log.py
│   ├── content/
│   │   └── bncc_learning.py         # Cards L01-L09 do módulo Aprender BNCC
│   ├── services/
│   │   ├── llm_service.py           # Abstração Groq/Ollama
│   │   ├── gamification_service.py  # Pontos, níveis, streaks
│   │   ├── challenge_service.py     # Banco de desafios, progresso
│   │   ├── goal_service.py          # CRUD de metas
│   │   └── report_service.py        # Geração do relatório mensal
│   ├── flows/
│   │   ├── onboarding_flow.py       # F1: ConversationHandler onboarding
│   │   ├── finance_flow.py          # F9: parser + confirmação + resumo
│   │   ├── xlsx_export.py           # F9.4: geração do .xlsx
│   │   ├── qa_engine.py             # F2: Q&A via LLM
│   │   ├── learning_flow.py         # /aprender: cards, quizzes e mini-desafios
│   │   ├── simulator_flow.py        # F3: simulador financeiro
│   │   └── goal_flow.py             # F6: criação e atualização de metas
│   └── prompts/
│       ├── system_prompt.py         # Persona Fini (versionada)
│       ├── parse_prompt.py          # Prompt para parsing de transações
│       └── insight_prompt.py        # Prompt para geração de insights
├── migrations/                      # Alembic migrations
│   ├── env.py
│   └── versions/
├── tests/
│   ├── test_finance_parser.py       # ≥30 casos de entrada
│   ├── test_gamification.py
│   ├── test_xlsx_export.py
│   ├── test_goal_flow.py
│   ├── test_simulator.py
│   └── test_rate_limiter.py
├── docker-compose.yml
├── docker-compose.test.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Modelos de Dados

### 4.1 Schema SQL completo

```sql
-- ─────────────────────────────────────────────
-- USERS
-- ─────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id     BIGINT UNIQUE NOT NULL,
    name            VARCHAR(100),
    age             INTEGER,
    income_source   VARCHAR(50),   -- 'mesada'|'estagio'|'freelas'|'trabalho'|'outros'
    monthly_income  DECIMAL(10,2), -- renda mensal informada no onboarding
    profile         VARCHAR(30) DEFAULT 'iniciante', -- 'iniciante'|'em_desenvolvimento'|'avancado'
    points          INTEGER DEFAULT 0,
    level           INTEGER DEFAULT 1,      -- 1=Aprendiz ... 5=Mestre
    streak_days     INTEGER DEFAULT 0,      -- dias consecutivos com lançamento
    last_entry_date DATE,                   -- última data com lançamento
    onboarded       BOOLEAN DEFAULT FALSE,
    report_opt_out  BOOLEAN DEFAULT FALSE,  -- opt-out do relatório mensal
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- TRANSACTIONS (receitas e despesas — módulo central F9)
-- ─────────────────────────────────────────────
CREATE TABLE transactions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    amount           DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    category         VARCHAR(80) NOT NULL,
    -- Categorias válidas para expense:
    --   'Alimentação'|'Transporte'|'Lazer'|'Assinaturas'|'Educação'|
    --   'Saúde'|'Compras'|'Presente'|'Outros'
    -- Categorias válidas para income:
    --   'Mesada'|'Salário'|'Estágio'|'Freelas'|'Presente'|'Outros'
    description      TEXT,
    happened_on      DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at       TIMESTAMP DEFAULT NOW(),
    -- para edição dentro de 24h (regra RN-13)
    updated_at       TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transactions_user_month
    ON transactions (user_id, DATE_TRUNC('month', happened_on));

-- ─────────────────────────────────────────────
-- GOALS (metas financeiras — F6)
-- ─────────────────────────────────────────────
CREATE TABLE goals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(200) NOT NULL,
    target_amount   DECIMAL(10,2) NOT NULL CHECK (target_amount > 0),
    current_amount  DECIMAL(10,2) DEFAULT 0 CHECK (current_amount >= 0),
    deadline        DATE NOT NULL,
    completed       BOOLEAN DEFAULT FALSE,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- CHALLENGES (desafios semanais — F4)
-- ─────────────────────────────────────────────
CREATE TABLE challenges (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(10) UNIQUE NOT NULL,  -- 'D01', 'D02', etc.
    title           VARCHAR(200) NOT NULL,
    description     TEXT NOT NULL,
    points_reward   INTEGER NOT NULL DEFAULT 50,
    difficulty      VARCHAR(10) NOT NULL CHECK (difficulty IN ('facil','medio','dificil')),
    category        VARCHAR(50)  -- 'registro'|'planejamento'|'comportamento'
);

CREATE TABLE user_challenges (
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    challenge_id    UUID REFERENCES challenges(id),
    week_number     INTEGER NOT NULL,  -- número ISO da semana
    year            INTEGER NOT NULL,
    accepted_at     TIMESTAMP DEFAULT NOW(),
    completed_at    TIMESTAMP,
    PRIMARY KEY (user_id, challenge_id, year, week_number)
);

-- ─────────────────────────────────────────────
-- MESSAGE LOGS (contexto de conversa LLM — F2)
-- ─────────────────────────────────────────────
CREATE TABLE message_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    role        VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- job semanal purga mensagens com > 90 dias
CREATE INDEX idx_message_logs_user_created ON message_logs (user_id, created_at);
```

### 4.2 Modelos SQLAlchemy (Python)

```python
# app/models/user.py
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, Numeric, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id     = Column(BigInteger, unique=True, nullable=False, index=True)
    name            = Column(String(100))
    age             = Column(Integer)
    income_source   = Column(String(50))
    monthly_income  = Column(Numeric(10, 2))
    profile         = Column(String(30), default="iniciante")
    points          = Column(Integer, default=0, nullable=False)
    level           = Column(Integer, default=1, nullable=False)
    streak_days     = Column(Integer, default=0)
    last_entry_date = Column(Date)
    onboarded       = Column(Boolean, default=False)
    report_opt_out  = Column(Boolean, default=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

# app/models/transaction.py
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

EXPENSE_CATEGORIES = [
    "Alimentação", "Transporte", "Lazer", "Assinaturas",
    "Educação", "Saúde", "Compras", "Presente", "Outros"
]
INCOME_CATEGORIES = ["Mesada", "Salário", "Estágio", "Freelas", "Presentes", "Bolsa/Auxílio", "Outros"]

class Transaction(Base):
    __tablename__ = "transactions"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id          = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'income' | 'expense'
    amount           = Column(Numeric(10, 2), nullable=False)
    category         = Column(String(80), nullable=False)
    description      = Column(Text)
    happened_on      = Column(Date, nullable=False, server_default=func.current_date())
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 5. Módulo Central: Finance Flow (F9)

Este é o módulo mais crítico do sistema. Toda IA usada para implementação deve
priorizar a qualidade deste módulo acima de todos os outros.

### 5.1 Parser de Linguagem Natural

**Arquivo:** `app/flows/finance_flow.py`
**Prompt:** `app/prompts/parse_prompt.py`

O parser usa o LLM para extrair dados estruturados de mensagens em texto livre.
A saída deve ser sempre JSON validado por Pydantic.

**Prompt de parsing (versão completa):**

```python
# app/prompts/parse_prompt.py

PARSE_SYSTEM_PROMPT = """
Você é um extrator de dados financeiros. Sua única função é analisar mensagens
em português brasileiro e extrair informações de transações financeiras.

Responda APENAS com JSON válido. Nenhum texto antes ou depois.

Schema de saída:
{
  "found": true/false,
  "transaction_type": "income" ou "expense",
  "amount": float (positivo, sem símbolo de moeda),
  "category": string (uma das categorias válidas abaixo),
  "description": string (descrição curta, máx 50 chars),
  "date_offset": integer (0=hoje, -1=ontem, -7=semana passada, etc.)
}

Se a mensagem não contiver uma transação financeira, retorne {"found": false}.

CATEGORIAS VÁLIDAS para expense:
  Alimentação, Transporte, Lazer, Assinaturas, Educação, Saúde, Compras, Presente, Outros

CATEGORIAS VÁLIDAS para income:
  Mesada, Estágio, Freelas, Presente, Outros

REGRAS DE CLASSIFICAÇÃO:
- lanche, restaurante, delivery, mercado, padaria → Alimentação
- ônibus, metrô, uber, táxi, combustível, bilhete, passagem → Transporte
- cinema, show, jogo, balada, festa, passeio → Lazer
- netflix, spotify, amazon, youtube premium, icloud, academia → Assinaturas
- escola, faculdade, curso, livro (estudo), material → Educação
- remédio, consulta, dentista, hospital, farmácia → Saúde
- roupa, tênis, acessório, celular, notebook, eletrônico → Compras
- presente pra alguém → Presente (expense)
- dinheiro de presente recebido → Presente (income)
- mesada → Mesada (income)
- salário, pagamento mensal, CLT → Salário (income)
- estágio → Estágio (income)
- freela, bico, serviço avulso → Freelas (income)

TRATAMENTO DE DATAS:
- "hoje" → 0
- "ontem" → -1
- "anteontem" → -2
- "essa semana" → 0 (assume hoje)
- "semana passada" → -7
- "mês passado" → calcule o offset em dias para o 1º do mês passado
- sem menção → 0 (hoje)

EXEMPLOS:
Input: "Gastei R$18,50 num lanche hoje"
Output: {"found":true,"transaction_type":"expense","amount":18.50,"category":"Alimentação","description":"Lanche","date_offset":0}

Input: "Recebi R$200 de mesada"
Output: {"found":true,"transaction_type":"income","amount":200.00,"category":"Mesada","description":"Mesada","date_offset":0}

Input: "Netflix R$37"
Output: {"found":true,"transaction_type":"expense","amount":37.00,"category":"Assinaturas","description":"Netflix","date_offset":0}

Input: "paguei 12 conto no ônibus ontem"
Output: {"found":true,"transaction_type":"expense","amount":12.00,"category":"Transporte","description":"Ônibus","date_offset":-1}

Input: "freela de 150 na semana passada"
Output: {"found":true,"transaction_type":"income","amount":150.00,"category":"Freelas","description":"Freela","date_offset":-7}

Input: "oi tudo bem"
Output: {"found":false}
"""
```

**Schema Pydantic para validação da saída:**

```python
# app/flows/finance_flow.py (trecho do schema)

from pydantic import BaseModel, field_validator
from typing import Literal, Optional
from datetime import date, timedelta

class ParsedTransaction(BaseModel):
    found: bool
    transaction_type: Optional[Literal["income", "expense"]] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date_offset: Optional[int] = 0

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Valor deve ser positivo")
        return v

    def get_date(self) -> date:
        return date.today() + timedelta(days=self.date_offset or 0)
```

### 5.2 Fluxo de Confirmação (ConversationHandler)

```python
# app/flows/finance_flow.py (fluxo completo)
# Usando python-telegram-bot ConversationHandler

# Estados do ConversationHandler
AWAITING_CORRECTION_FIELD = 1
AWAITING_CORRECTION_VALUE = 2

# Etapas do fluxo:

# 1. finance_entry_handler(update, context)
#    Chamado por: qualquer mensagem que não seja comando e não seja onboarding
#    Chama: LLMGateway.parse_transaction(text)
#    Se parsed.found == False: passa para QA engine
#    Se parsed.found == True:  monta mensagem de confirmação com InlineKeyboard

# 2. Mensagem de confirmação enviada ao usuário:
#    ┌─────────────────────────────────────────┐
#    │ 📝 Confirmando lançamento:              │
#    │                                         │
#    │ 💸 Despesa • R$18,50 • Alimentação     │
#    │ 📅 Hoje, 23/05/2026                     │
#    │ 📌 Lanche                               │
#    │                                         │
#    │ [✅ Confirmar] [✏️ Corrigir] [❌ Cancelar] │
#    └─────────────────────────────────────────┘

# 3. confirm_transaction(update, context)
#    Salva Transaction no banco
#    Atualiza streak do usuário
#    Calcula pontos via GamificationEngine
#    Gera resumo rápido do mês
#    Gera insight via LLM se relevante
#    Envia mensagem de confirmação com saldo

# 4. correct_transaction(update, context)
#    Exibe InlineKeyboard com campos corrigíveis:
#    [💰 Valor] [🏷️ Categoria] [📅 Data] [📌 Descrição]

# 5. apply_correction(update, context)
#    Aplica a correção e volta para mensagem de confirmação (passo 2)
```

### 5.3 Geração de Insight Pós-Registro

Após cada lançamento confirmado, o sistema gera um insight contextualizado.
Não é sempre — apenas quando há informação relevante para mostrar.

```python
# app/prompts/insight_prompt.py

INSIGHT_SYSTEM_PROMPT = """
Você é o Fini, parceiro financeiro de jovens brasileiros.
Gere um insight curto (máx. 2 frases) sobre o padrão de gastos do usuário.
Use os dados fornecidos. Seja específico, use os valores reais.
Tom: amigável e direto, como um amigo que entende de dinheiro.
Termine com uma observação útil ou pergunta reflexiva.
Não use linguagem de banco ou termos formais.
"""

# Lógica de quando disparar insight:
# - Quando o gasto de uma categoria ultrapassa 30% da renda mensal
# - Quando o saldo mensal fica negativo pela primeira vez no mês
# - Quando o usuário fecha o 7º dia consecutivo de registros (streak)
# - Quando uma categoria tem >5 lançamentos no mês
# - No 20º dia do mês (projeção de fechamento)
```

### 5.4 Resumo Mensal (`/resumo`)

```python
# Lógica de construção do resumo (app/flows/finance_flow.py)

async def build_monthly_summary(user_id: UUID, month: int, year: int) -> str:
    """
    Constrói o resumo mensal formatado para exibição no Telegram.
    
    Queries necessárias:
    1. SUM(amount) WHERE type='income' AND month/year
    2. SUM(amount) WHERE type='expense' AND month/year  
    3. SUM(amount) GROUP BY category WHERE type='expense' AND month/year
    4. Mesmo do mês anterior (para comparação)
    5. Goals ativas do usuário
    
    Formato de saída: string Markdown para Telegram (MarkdownV2)
    Máx: ~25 linhas (legível em mobile sem scroll excessivo)
    
    Inclui:
    - Header: "📊 Resumo de {mês}/{ano} — {nome} {emoji_nível}"
    - Receitas: total + breakdown por categoria
    - Gastos: total + % da renda + breakdown por categoria ordenado por valor
    - Destaque visual na maior categoria de gasto
    - Saldo: valor + indicador visual (✅ positivo / ⚠️ negativo)
    - Comparação com mês anterior (se houver dados)
    - Insight do Fini (gerado por LLM com dados reais)
    - Metas ativas (mini preview de progresso)
    """
```

---

## 6. Módulo de Exportação XLSX (F9.4)

**Arquivo:** `app/flows/xlsx_export.py`

Este módulo gera o arquivo `.xlsx` sob demanda e o envia diretamente pelo
Telegram como documento. O arquivo é gerado em memória (`BytesIO`) e nunca
persiste em disco — enviado e descartado.

### 6.1 Código completo de geração

```python
# app/flows/xlsx_export.py

import io
from datetime import date
from decimal import Decimal
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

# ── Paleta de cores ──────────────────────────────────────────
COLOR_GREEN_BG    = "C6EFCE"  # fundo verde claro (receitas)
COLOR_GREEN_TEXT  = "276221"  # texto verde escuro
COLOR_RED_BG      = "FFC7CE"  # fundo vermelho claro (despesas)
COLOR_RED_TEXT    = "9C0006"  # texto vermelho escuro
COLOR_BLUE_HEADER = "2F75B6"  # azul para cabeçalhos
COLOR_YELLOW_TOTAL= "FFEB9C"  # amarelo para totais
COLOR_WHITE       = "FFFFFF"
COLOR_GRAY_ROW    = "F5F5F5"  # linhas alternadas


def generate_xlsx(
    user_name: str,
    month: int,
    year: int,
    transactions: list[dict],  # [{date, type, category, description, amount}]
    monthly_income: Decimal,
) -> io.BytesIO:
    """
    Gera planilha .xlsx em memória e retorna BytesIO.
    
    Parâmetros:
    - user_name: nome do usuário (vai no título)
    - month/year: mês e ano de referência
    - transactions: lista de dicts ordenada por date ASC
    - monthly_income: renda informada no onboarding (para calcular %)
    
    Retorna: BytesIO com o arquivo .xlsx pronto para envio
    """
    wb = Workbook()
    
    # ── ABA 1: Lançamentos ───────────────────────────────────
    ws1 = wb.active
    ws1.title = "Lançamentos"
    
    month_name = _get_month_name(month)
    
    # Título
    ws1.merge_cells("A1:E1")
    title_cell = ws1["A1"]
    title_cell.value = f"Controle Financeiro — {user_name} — {month_name}/{year}"
    title_cell.font = Font(name="Arial", bold=True, size=13, color=COLOR_WHITE)
    title_cell.fill = PatternFill("solid", start_color=COLOR_BLUE_HEADER)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 28
    
    # Cabeçalho da tabela
    headers = ["Data", "Tipo", "Categoria", "Descrição", "Valor (R$)"]
    header_row = 2
    for col, header in enumerate(headers, 1):
        cell = ws1.cell(row=header_row, column=col, value=header)
        cell.font = Font(name="Arial", bold=True, size=11, color=COLOR_WHITE)
        cell.fill = PatternFill("solid", start_color=COLOR_BLUE_HEADER)
        cell.alignment = Alignment(horizontal="center")
        cell.border = _thin_border()
    
    # Dados
    data_start_row = 3
    for i, t in enumerate(transactions):
        row = data_start_row + i
        bg = COLOR_GRAY_ROW if i % 2 == 0 else COLOR_WHITE
        
        is_income = t["type"] == "income"
        value_color = COLOR_GREEN_TEXT if is_income else COLOR_RED_TEXT
        value_bg    = COLOR_GREEN_BG   if is_income else COLOR_RED_BG
        tipo_label  = "Receita" if is_income else "Despesa"
        
        # Data
        _write_cell(ws1, row, 1, t["date"].strftime("%d/%m/%Y"), bg, "Arial", 10)
        # Tipo
        _write_cell(ws1, row, 2, tipo_label, value_bg, "Arial", 10,
                    color=value_color, bold=True)
        # Categoria
        _write_cell(ws1, row, 3, t["category"], bg, "Arial", 10)
        # Descrição
        _write_cell(ws1, row, 4, t["description"] or "", bg, "Arial", 10)
        # Valor
        amount_cell = ws1.cell(row=row, column=5, value=float(t["amount"]))
        amount_cell.font = Font(name="Arial", size=10, color=value_color, bold=True)
        amount_cell.fill = PatternFill("solid", start_color=value_bg)
        amount_cell.number_format = 'R$#,##0.00'
        amount_cell.alignment = Alignment(horizontal="right")
        amount_cell.border = _thin_border()
    
    last_data_row = data_start_row + len(transactions) - 1
    
    # Linha de total
    total_row = last_data_row + 1
    ws1.merge_cells(f"A{total_row}:D{total_row}")
    total_label = ws1[f"A{total_row}"]
    total_label.value = "TOTAL"
    total_label.font = Font(name="Arial", bold=True, size=11)
    total_label.fill = PatternFill("solid", start_color=COLOR_YELLOW_TOTAL)
    total_label.alignment = Alignment(horizontal="right")
    
    total_value = ws1.cell(row=total_row, column=5)
    total_value.value = f"=SUM(E{data_start_row}:E{last_data_row})"
    total_value.font = Font(name="Arial", bold=True, size=11)
    total_value.fill = PatternFill("solid", start_color=COLOR_YELLOW_TOTAL)
    total_value.number_format = 'R$#,##0.00'
    total_value.alignment = Alignment(horizontal="right")
    
    # Filtros automáticos
    ws1.auto_filter.ref = f"A{header_row}:E{last_data_row}"
    
    # Largura das colunas
    ws1.column_dimensions["A"].width = 14  # Data
    ws1.column_dimensions["B"].width = 12  # Tipo
    ws1.column_dimensions["C"].width = 18  # Categoria
    ws1.column_dimensions["D"].width = 30  # Descrição
    ws1.column_dimensions["E"].width = 14  # Valor
    
    # Congelar linha de cabeçalho
    ws1.freeze_panes = "A3"
    
    # ── ABA 2: Resumo ─────────────────────────────────────────
    ws2 = wb.create_sheet("Resumo")
    
    # Título
    ws2.merge_cells("A1:C1")
    t2 = ws2["A1"]
    t2.value = f"Resumo — {month_name}/{year}"
    t2.font = Font(name="Arial", bold=True, size=13, color=COLOR_WHITE)
    t2.fill = PatternFill("solid", start_color=COLOR_BLUE_HEADER)
    t2.alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 28
    
    # Cabeçalhos da tabela de resumo
    for col, h in enumerate(["Indicador", "Valor (R$)", "% da Renda"], 1):
        c = ws2.cell(row=2, column=col, value=h)
        c.font = Font(name="Arial", bold=True, size=11, color=COLOR_WHITE)
        c.fill = PatternFill("solid", start_color=COLOR_BLUE_HEADER)
        c.alignment = Alignment(horizontal="center")
        c.border = _thin_border()
    
    # Calcular totais por categoria
    income_total = sum(t["amount"] for t in transactions if t["type"] == "income")
    expense_total = sum(t["amount"] for t in transactions if t["type"] == "expense")
    saldo = income_total - expense_total
    
    cat_totals: dict[str, Decimal] = {}
    for t in transactions:
        if t["type"] == "expense":
            cat_totals[t["category"]] = cat_totals.get(t["category"], Decimal(0)) + t["amount"]
    cat_totals_sorted = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
    
    ref_income = float(monthly_income) if monthly_income else float(income_total) or 1
    
    # Linhas de resumo
    summary_rows = [
        ("Total de Receitas", float(income_total), float(income_total) / ref_income),
        ("Total de Despesas", float(expense_total), float(expense_total) / ref_income),
        ("Saldo do Mês", float(saldo), float(saldo) / ref_income),
    ]
    
    r = 3
    for label, value, pct in summary_rows:
        is_saldo = "Saldo" in label
        is_receita = "Receita" in label
        bg = COLOR_GREEN_BG if (is_receita or (is_saldo and value >= 0)) else COLOR_RED_BG
        txt_color = COLOR_GREEN_TEXT if (is_receita or (is_saldo and value >= 0)) else COLOR_RED_TEXT
        
        lc = ws2.cell(row=r, column=1, value=label)
        lc.font = Font(name="Arial", bold=True, size=11, color=txt_color)
        lc.fill = PatternFill("solid", start_color=bg)
        lc.border = _thin_border()
        
        vc = ws2.cell(row=r, column=2, value=value)
        vc.font = Font(name="Arial", bold=True, size=11, color=txt_color)
        vc.fill = PatternFill("solid", start_color=bg)
        vc.number_format = 'R$#,##0.00'
        vc.alignment = Alignment(horizontal="right")
        vc.border = _thin_border()
        
        pc = ws2.cell(row=r, column=3, value=pct)
        pc.font = Font(name="Arial", size=10, color=txt_color)
        pc.fill = PatternFill("solid", start_color=bg)
        pc.number_format = '0.0%'
        pc.alignment = Alignment(horizontal="center")
        pc.border = _thin_border()
        r += 1
    
    # Separador
    r += 1
    ws2.cell(row=r, column=1, value="DESPESAS POR CATEGORIA").font = Font(
        name="Arial", bold=True, size=11)
    r += 1
    
    chart_data_start = r
    for cat, val in cat_totals_sorted:
        pct = float(val) / ref_income
        lc = ws2.cell(row=r, column=1, value=cat)
        lc.font = Font(name="Arial", size=11)
        lc.fill = PatternFill("solid", start_color=COLOR_RED_BG)
        lc.border = _thin_border()
        
        vc = ws2.cell(row=r, column=2, value=float(val))
        vc.font = Font(name="Arial", size=11, color=COLOR_RED_TEXT)
        vc.fill = PatternFill("solid", start_color=COLOR_RED_BG)
        vc.number_format = 'R$#,##0.00'
        vc.alignment = Alignment(horizontal="right")
        vc.border = _thin_border()
        
        pc = ws2.cell(row=r, column=3, value=pct)
        pc.font = Font(name="Arial", size=10)
        pc.number_format = '0.0%'
        pc.alignment = Alignment(horizontal="center")
        pc.border = _thin_border()
        r += 1
    
    chart_data_end = r - 1
    
    # Gráfico de barras horizontais
    if cat_totals_sorted:
        chart = BarChart()
        chart.type = "bar"  # horizontal
        chart.title = f"Gastos por Categoria — {month_name}/{year}"
        chart.y_axis.title = "Categoria"
        chart.x_axis.title = "R$"
        chart.shape = 4
        chart.style = 10
        
        data_ref = Reference(ws2, min_col=2, min_row=chart_data_start,
                             max_row=chart_data_end)
        cats_ref = Reference(ws2, min_col=1, min_row=chart_data_start,
                             max_row=chart_data_end)
        chart.add_data(data_ref)
        chart.set_categories(cats_ref)
        chart.series[0].title = None
        chart.width = 20
        chart.height = max(10, len(cat_totals_sorted) * 1.5)
        
        ws2.add_chart(chart, f"A{r + 2}")
    
    # Largura das colunas do resumo
    ws2.column_dimensions["A"].width = 28
    ws2.column_dimensions["B"].width = 16
    ws2.column_dimensions["C"].width = 14
    
    # ── Serializar para BytesIO ──────────────────────────────
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


# ── Helpers ──────────────────────────────────────────────────

def _write_cell(ws, row, col, value, bg, font_name, size,
                color="000000", bold=False):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(name=font_name, size=size, color=color, bold=bold)
    c.fill = PatternFill("solid", start_color=bg)
    c.border = _thin_border()
    return c


def _thin_border():
    s = Side(style="thin", color="D9D9D9")
    return Border(left=s, right=s, top=s, bottom=s)


def _get_month_name(month: int) -> str:
    names = ["Jan","Fev","Mar","Abr","Mai","Jun",
             "Jul","Ago","Set","Out","Nov","Dez"]
    return names[month - 1]
```

### 6.2 Handler do Telegram para envio da planilha

```python
# app/flows/finance_flow.py (trecho do handler /planilha)

async def planilha_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_by_telegram_id(update.effective_user.id)
    now = date.today()
    
    await update.message.reply_text("⏳ Gerando sua planilha...")
    
    transactions = await get_transactions_for_month(
        user_id=user.id, month=now.month, year=now.year
    )
    
    if not transactions:
        await update.message.reply_text(
            "📭 Você ainda não tem lançamentos esse mês.\n"
            "Registre um gasto e depois peça a planilha!"
        )
        return
    
    xlsx_buffer = generate_xlsx(
        user_name=user.name,
        month=now.month,
        year=now.year,
        transactions=[
            {
                "date": t.happened_on,
                "type": t.transaction_type,
                "category": t.category,
                "description": t.description,
                "amount": t.amount,
            }
            for t in transactions
        ],
        monthly_income=user.monthly_income or Decimal(0),
    )
    
    filename = f"fini_{user.name.lower().replace(' ', '_')}_{now.month:02d}_{now.year}.xlsx"
    
    await update.message.reply_document(
        document=xlsx_buffer,
        filename=filename,
        caption=(
            f"📊 Sua planilha de {_get_month_name(now.month)}/{now.year} está pronta!\n"
            f"Tem {len(transactions)} lançamentos.\n\n"
            "📌 Dica: abra no Excel ou Google Sheets para ver o gráfico de categorias."
        )
    )
    
    # Pontos por exportação (primeira vez no mês)
    await gamification_service.award_points(
        user=user, action="xlsx_export", context=context
    )
```

---

## 7. Módulo LLM Gateway

### 7.1 Abstração com fallback automático

```python
# app/services/llm_service.py

import httpx
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], system: str, max_tokens: int = 300) -> str:
        ...

class GroqProvider(LLMProvider):
    """LLM principal: Groq + Llama 3.3 70B (OSS, free tier, < 500ms)"""
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL    = "llama-3.3-70b-versatile"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def chat(self, messages: list[dict], system: str, max_tokens: int = 300) -> str:
        payload = {
            "model": self.MODEL,
            "messages": [{"role": "system", "content": system}] + messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,  # mais determinístico para parsing
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                self.BASE_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

class OllamaProvider(LLMProvider):
    """Fallback: Ollama local com Gemma 3 4B"""
    MODEL = "gemma3:4b"
    
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.base_url = base_url
    
    async def chat(self, messages: list[dict], system: str, max_tokens: int = 300) -> str:
        payload = {
            "model": self.MODEL,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{self.base_url}/api/chat", json=payload)
            r.raise_for_status()
            return r.json()["message"]["content"]

class LLMGateway:
    """
    Seleciona Groq como primário, fallback automático para Ollama.
    
    Usos distintos:
    - parse_transaction(): temperatura baixa (0.3), saída JSON estrita
    - qa_answer(): temperatura média (0.7), resposta em português
    - generate_insight(): temperatura média (0.6), máx 2 frases
    """
    
    def __init__(self, groq_key: str, ollama_url: str):
        self.primary  = GroqProvider(api_key=groq_key)
        self.fallback = OllamaProvider(base_url=ollama_url)
    
    async def _call(self, messages, system, max_tokens) -> str:
        try:
            return await self.primary.chat(messages, system, max_tokens)
        except Exception as e:
            logger.warning(f"Groq falhou ({e}), usando Ollama fallback")
            return await self.fallback.chat(messages, system, max_tokens)
    
    async def parse_transaction(self, text: str) -> dict:
        """Usa sistema de parsing estrito. Retorna dict JSON."""
        from app.prompts.parse_prompt import PARSE_SYSTEM_PROMPT
        result = await self._call(
            messages=[{"role": "user", "content": text}],
            system=PARSE_SYSTEM_PROMPT,
            max_tokens=150,
        )
        # Limpeza defensiva: remove markdown fences se houver
        clean = result.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(clean)
    
    async def qa_answer(self, question: str, history: list[dict], user_context: dict) -> str:
        """Responde pergunta sobre finanças pessoais."""
        from app.prompts.system_prompt import build_system_prompt
        system = build_system_prompt(user_context)
        return await self._call(
            messages=history + [{"role": "user", "content": question}],
            system=system,
            max_tokens=300,
        )
    
    async def generate_insight(self, summary_data: dict) -> str:
        """Gera insight contextualizado de 1-2 frases."""
        from app.prompts.insight_prompt import INSIGHT_SYSTEM_PROMPT
        prompt = f"Dados do usuário: {json.dumps(summary_data, ensure_ascii=False)}"
        return await self._call(
            messages=[{"role": "user", "content": prompt}],
            system=INSIGHT_SYSTEM_PROMPT,
            max_tokens=100,
        )
```

---

## 8. Sistema de Gamificação

```python
# app/services/gamification_service.py

from enum import Enum

class GamificationAction(str, Enum):
    ONBOARDING_COMPLETE    = "onboarding_complete"     # +100
    FIRST_ENTRY_OF_DAY     = "first_entry_of_day"      # +10
    INCOME_REGISTERED      = "income_registered"       # +10
    POSITIVE_MONTH_CLOSE   = "positive_month_close"    # +80
    SEVEN_DAY_STREAK       = "seven_day_streak"        # +80
    XLSX_EXPORT            = "xlsx_export"             # +20
    GOAL_CREATED           = "goal_created"            # +30
    GOAL_PROGRESS_UPDATED  = "goal_progress_updated"   # +15
    GOAL_COMPLETED         = "goal_completed"          # +80
    CHALLENGE_EASY         = "challenge_easy"          # +50
    CHALLENGE_MEDIUM       = "challenge_medium"        # +100
    CHALLENGE_HARD         = "challenge_hard"          # +150
    SIMULATOR_FIRST_USE    = "simulator_first_use"     # +20
    QA_QUESTION            = "qa_question"             # +5 (1x/dia)
    LEARNING_TOPIC_VIEWED  = "learning_topic_viewed"   # +5
    LEARNING_QUIZ_CORRECT  = "learning_quiz_correct"   # +15
    LEARNING_CHALLENGE_DONE = "learning_challenge_done" # +25

POINTS_MAP = {
    GamificationAction.ONBOARDING_COMPLETE:   100,
    GamificationAction.FIRST_ENTRY_OF_DAY:    10,
    GamificationAction.INCOME_REGISTERED:     10,
    GamificationAction.POSITIVE_MONTH_CLOSE:  80,
    GamificationAction.SEVEN_DAY_STREAK:      80,
    GamificationAction.XLSX_EXPORT:           20,
    GamificationAction.GOAL_CREATED:          30,
    GamificationAction.GOAL_PROGRESS_UPDATED: 15,
    GamificationAction.GOAL_COMPLETED:        80,
    GamificationAction.CHALLENGE_EASY:        50,
    GamificationAction.CHALLENGE_MEDIUM:      100,
    GamificationAction.CHALLENGE_HARD:        150,
    GamificationAction.SIMULATOR_FIRST_USE:   20,
    GamificationAction.QA_QUESTION:           5,
    GamificationAction.LEARNING_TOPIC_VIEWED: 5,
    GamificationAction.LEARNING_QUIZ_CORRECT: 15,
    GamificationAction.LEARNING_CHALLENGE_DONE: 25,
}

LEVEL_THRESHOLDS = {1: 0, 2: 200, 3: 500, 4: 1000, 5: 2000}

LEVEL_NAMES = {
    1: "🌱 Aprendiz",
    2: "📚 Estudante",
    3: "💡 Consciente",
    4: "🚀 Investidor",
    5: "🏆 Mestre",
}

LEVEL_UP_MESSAGES = {
    2: "Você começou a entender o jogo. Agora vamos ver quanto você pode acumular.",
    3: "Você já tem consciência dos seus gastos. Isso é mais raro do que parece.",
    4: "Você pensa antes de gastar. Isso te coloca na frente da maioria.",
    5: "Você dominou o básico que 90% das pessoas nunca aprendem. Ensina alguém? 🏆",
}

def calculate_level(points: int) -> int:
    level = 1
    for lvl, threshold in sorted(LEVEL_THRESHOLDS.items()):
        if points >= threshold:
            level = lvl
    return level

async def award_points(user, action: GamificationAction, db_session) -> dict:
    """
    Adiciona pontos ao usuário e verifica se houve level up.
    
    Retorna:
    {
        "points_awarded": int,
        "new_total": int,
        "level_changed": bool,
        "new_level": int,
        "level_name": str,
        "level_up_message": str | None
    }
    """
    points = POINTS_MAP.get(action, 0)
    old_level = user.level
    
    user.points += points
    user.level = calculate_level(user.points)
    
    await db_session.commit()
    
    level_changed = user.level != old_level
    return {
        "points_awarded": points,
        "new_total": user.points,
        "level_changed": level_changed,
        "new_level": user.level,
        "level_name": LEVEL_NAMES[user.level],
        "level_up_message": LEVEL_UP_MESSAGES.get(user.level) if level_changed else None,
    }

async def update_streak(user, db_session) -> int:
    """
    Atualiza streak diário. Retorna o streak atual.
    Regra: precisa de ≥1 lançamento por dia. Interrupção zera.
    """
    from datetime import date, timedelta
    today = date.today()
    
    if user.last_entry_date == today:
        return user.streak_days  # já registrou hoje
    
    if user.last_entry_date == today - timedelta(days=1):
        user.streak_days += 1
    else:
        user.streak_days = 1  # zera e começa novo streak
    
    user.last_entry_date = today
    await db_session.commit()
    
    return user.streak_days
```

---

## 8.1 Módulo Aprender BNCC

O módulo `/aprender` oferece uma trilha curta de educação financeira alinhada à
BNCC, com cards de conteúdo, quiz rápido via InlineKeyboard e mini-desafios
conectados ao controle financeiro.

### Conteúdo

```python
# app/content/bncc_learning.py

@dataclass(frozen=True)
class LearningTopic:
    code: str              # L01, L02...
    slug: str              # saldo, porcentagem...
    title: str
    bncc_focus: str        # alinhamento pedagógico interno
    content: str           # explicação curta
    example: str           # exemplo com reais
    quiz_question: str
    quiz_options: dict[str, str]
    correct_option: str
    feedback_correct: str
    feedback_wrong: str
    mini_challenge: str
    related_commands: tuple[str, ...]
```

Tópicos MVP:

| Código | Tópico | Foco |
|---|---|---|
| L01 | Receita e despesa | Entradas, saídas e registro |
| L02 | Saldo | Diferença entre receitas e despesas |
| L03 | Porcentagem | Parte do todo e % da renda |
| L04 | Juros simples | Acréscimos proporcionais |
| L05 | Juros compostos | Crescimento acumulado |
| L06 | Metas financeiras | Valor, prazo e planejamento |
| L07 | Planejamento mensal | Prioridades e previsão |
| L08 | Consumo consciente | Necessidade, desejo e impulso |
| L09 | Bets e apostas | Por que apostas não são caminho financeiro saudável; onde buscar ajuda |

### Fluxo

```python
# app/flows/learning_flow.py

CALLBACK_MENU = "learn_menu"
CALLBACK_TOPIC_PREFIX = "learn_topic:"
CALLBACK_QUIZ_PREFIX = "learn_quiz:"
CALLBACK_CHALLENGE_PREFIX = "learn_challenge:"

async def handle_learning_command(update, db, user):
    # envia menu com L01-L09

async def handle_learning_callback(update, db, user, data):
    # topic -> renderiza card
    # quiz -> corrige alternativa e dá feedback
    # challenge -> aceita mini-desafio e pontua
```

### Personalização

Quando houver dados do mês, o card usa contexto real:

- `saldo`: receitas, despesas e saldo do mês atual.
- `porcentagem`: maior categoria como percentual da renda mensal.
- `planejamento`: 10% da renda informada como exemplo de meta.

Se não houver dados, o card usa exemplos genéricos em reais.

---

## 9. Persona Fini (System Prompt)

```python
# app/prompts/system_prompt.py

def build_system_prompt(user_context: dict) -> str:
    """
    Constrói o system prompt da persona Fini com contexto do usuário.
    
    user_context esperado:
    {
        "name": str,
        "profile": "iniciante" | "em_desenvolvimento" | "avancado",
        "level_name": str,
        "points": int,
        "monthly_income": float | None,
        "current_month_summary": {
            "income": float,
            "expenses": float,
            "balance": float,
            "top_category": str | None,
        } | None
    }
    """
    profile = user_context.get("profile", "iniciante")
    name    = user_context.get("name", "você")
    level   = user_context.get("level_name", "🌱 Aprendiz")
    points  = user_context.get("points", 0)
    income  = user_context.get("monthly_income")
    summary = user_context.get("current_month_summary")
    
    profile_instructions = {
        "iniciante": (
            "Use linguagem muito simples. Evite qualquer jargão financeiro. "
            "Explique tudo como se fosse a primeira vez que o usuário ouve. "
            "Exemplos: mesada, lanche, ônibus, streaming. "
            "Seja encorajador — qualquer passo é um avanço."
        ),
        "em_desenvolvimento": (
            "Use linguagem direta e clara. Pode usar termos básicos de finanças "
            "(orçamento, poupança, juro) mas sempre explique brevemente. "
            "Conecte os conceitos à realidade do jovem."
        ),
        "avancado": (
            "Trate como um colega que já entende o básico. Pode desafiar mais. "
            "Pode usar termos como Tesouro Direto, taxa Selic, inflação, custo "
            "de oportunidade — mas sempre com exemplos concretos. "
            "Seja mais analítico e menos didático."
        ),
    }
    
    context_block = f"Nome: {name} | Nível: {level} | Pontos: {points}"
    if income:
        context_block += f" | Renda mensal: R${income:.2f}"
    if summary:
        context_block += (
            f"\nMês atual: receitas R${summary['income']:.2f} | "
            f"gastos R${summary['expenses']:.2f} | "
            f"saldo R${summary['balance']:.2f}"
        )
        if summary.get("top_category"):
            context_block += f" | Maior gasto: {summary['top_category']}"
    
    return f"""
Você é o Fini, parceiro de educação financeira de jovens brasileiros (13–21 anos).

PERSONALIDADE:
- Tom: amigável, direto, levemente bem-humorado — como um colega mais experiente
- NUNCA use: "liquidez de portfólio", "hedge", "alavancagem", linguagem de banco
- SEMPRE use: exemplos com valores em reais ("tipo, se você guardar R$5 por dia...")
- Celebre conquistas: "Arrasou! Você acabou de aprender juros compostos 🔥"
- Acolha erros: "Sem julgamento. Vamos entender o que aconteceu?"
- Termine com pergunta reflexiva ou mini-desafio concreto

PERFIL DO USUÁRIO: {profile}
{profile_instructions[profile]}

REGRAS:
1. Máximo 150 palavras por resposta
2. Use emojis com moderação (máx. 3 por mensagem)
3. Nunca recomende produtos específicos ("compre ação X", "use o banco Y")
4. Se fugir de finanças, redirecione gentilmente
5. Se não souber, diga isso e sugira: Banco Central (bcb.gov.br), ENEF, Consumidor.gov.br
6. Use os dados financeiros do usuário quando forem relevantes para personalizar

CONTEXTO ATUAL DO USUÁRIO:
{context_block}
""".strip()
```

---

## 10. Fluxo de Onboarding (F1)

```python
# app/flows/onboarding_flow.py
# Usando python-telegram-bot ConversationHandler

# Estados
(
    WAITING_NAME,
    WAITING_AGE,
    WAITING_INCOME_SOURCE,
    WAITING_INCOME_VALUE,
    QUIZ_Q1,
    QUIZ_Q2,
    QUIZ_Q3,
) = range(7)

# ── Passo 1: /start ───────────────────────────────────────────
# Verifica se user existe e está onboarded.
# Se não: envia mensagem de boas-vindas e pede o nome.

WELCOME_MESSAGE = """
👋 Oi! Eu sou o *Fini*, seu parceiro de educação financeira.

Vou te ajudar a:
📊 Entender pra onde vai seu dinheiro
🎯 Criar metas e realizá-las
💡 Aprender sobre finanças do jeito fácil

Tudo isso direto aqui no Telegram, sem complicação.

Primeiro: *qual é o seu nome?*
"""

# ── Passo 2: Nome recebido → pede a idade ────────────────────

# ── Passo 3: Idade recebida → pede fonte de renda ────────────
# InlineKeyboard com opções:
INCOME_SOURCE_KEYBOARD = [
    [("💰 Mesada", "mesada"), ("👔 Estágio", "estagio")],
    [("💻 Freelas/bicos", "freelas"), ("🏪 Trabalho formal", "trabalho")],
    [("🤷 Outras", "outros")],
]

# ── Passo 4: Fonte de renda → pede valor aproximado ──────────
INCOME_VALUE_MESSAGE = """
Legal! E por mês, você recebe aproximadamente quanto?

Pode ser o valor real ou fictício — uso só pra calcular porcentagens no resumo.
Ex: 300, 500, 1200

_(Não precisa do R$, só o número)_
"""

# ── Passo 5-7: Quiz (3 perguntas, InlineKeyboard) ────────────
QUIZ_QUESTIONS = [
    {
        "text": "Pergunta 1/3 🎯\n\nQuando você recebe sua mesada/salário, o que faz primeiro?",
        "options": [
            ("💸 Gasto logo — o que sobrar guardo", "A"),
            ("🏦 Guardo uma parte antes de gastar", "B"),
            ("🤷 Depende do mês", "C"),
        ],
        "profile_map": {"A": "iniciante", "B": "avancado", "C": "em_desenvolvimento"},
    },
    {
        "text": "Pergunta 2/3 🎯\n\nVocê já ouviu falar em juros compostos?",
        "options": [
            ("✅ Sim e entendo como funciona", "A"),
            ("🤔 Já ouvi, mas não sei direito", "B"),
            ("❌ Nunca ouvi esse nome", "C"),
        ],
        "profile_map": {"A": "avancado", "B": "em_desenvolvimento", "C": "iniciante"},
    },
    {
        "text": "Pergunta 3/3 🎯\n\nVocê tem algum objetivo financeiro agora?",
        "options": [
            ("🎯 Sim, sei exatamente o que quero", "A"),
            ("💭 Quero ter, mas não sei como definir", "B"),
            ("😶 Não pensei nisso ainda", "C"),
        ],
        "profile_map": {"A": "avancado", "B": "em_desenvolvimento", "C": "iniciante"},
    },
]

# ── Passo 8: Resultado do onboarding ─────────────────────────
# Classifica perfil (maioria dos pontos), salva no banco, dá +100 pts.
# Exibe mensagem de conclusão + sugere primeiro registro de gasto.

ONBOARDING_COMPLETE_TEMPLATE = """
🎉 Pronto, {name}! Bem-vindo ao Fini!

📊 Seu perfil: *{profile_label}*
{profile_description}

Você ganhou *+100 pontos* por completar o onboarding! 🌱 Aprendiz

Agora vem a parte mais importante: vamos registrar seu primeiro gasto?

É simples — é só mandar uma mensagem do tipo:
💬 _"Gastei R$5 no lanche"_
💬 _"Recebi R$200 de mesada"_

Tenta agora! 👇
"""

PROFILE_DESCRIPTIONS = {
    "iniciante": "Você está começando agora — e isso é ótimo! Vou te guiar passo a passo.",
    "em_desenvolvimento": "Você já tem alguma noção de finanças. Vamos organizar isso melhor.",
    "avancado": "Você já pensa em dinheiro de forma estratégica. Vamos usar isso ao máximo.",
}
```

---

## 11. Rate Limiting (Redis)

```python
# app/core/redis_client.py (trecho do rate limiter)

import redis.asyncio as aioredis

RATE_LIMIT_WINDOW = 3600  # 1 hora em segundos
RATE_LIMIT_MAX    = 30    # mensagens por hora por usuário

async def check_rate_limit(redis: aioredis.Redis, telegram_id: int) -> bool:
    """
    Retorna True se dentro do limite, False se excedido.
    Usa sliding window com Redis INCR + EXPIRE.
    """
    key = f"rate:{telegram_id}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, RATE_LIMIT_WINDOW)
    return count <= RATE_LIMIT_MAX

RATE_LIMIT_MESSAGE = """
⏸️ Calma lá! Você enviou muitas mensagens rápido.

Aguarda um minutinho e tenta de novo.
Estou aqui quando você precisar! 😄
"""
```

---

## 12. API Endpoints (FastAPI)

```python
# app/main.py

from fastapi import FastAPI, Request, Header, HTTPException, Depends
from app.core.config import settings

app = FastAPI(title="Fini Bot API", docs_url=None)  # docs desabilitado em produção

@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    """
    Recebe updates do Telegram.
    Valida o token secreto para segurança.
    """
    if x_telegram_bot_api_secret_token != settings.TELEGRAM_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = await request.json()
    await telegram_app.process_update(data)  # python-telegram-bot async
    return {"ok": True}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fini-bot"}

# Endpoints de admin (protegidos por API Key)
@app.get("/admin/stats")
async def admin_stats(x_api_key: str = Header(None)):
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403)
    # Retorna: total usuários, lançamentos do mês, perguntas mais comuns
    ...
```

```
Endpoints disponíveis:

POST /telegram/webhook    → Recebe updates do Telegram
GET  /health              → Health check
GET  /admin/stats         → Estatísticas do piloto (protegido por API Key)
GET  /admin/users         → Lista usuários agregada (sem dados pessoais)
```

---

## 13. Docker Compose

```yaml
# docker-compose.yml

version: "3.9"

services:
  fini-api:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://fini:fini@postgres:5432/finidb
      REDIS_URL: redis://redis:6379/0
      GROQ_API_KEY: ${GROQ_API_KEY}
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      TELEGRAM_SECRET_TOKEN: ${TELEGRAM_SECRET_TOKEN}
      OLLAMA_BASE_URL: http://ollama:11434
      ADMIN_API_KEY: ${ADMIN_API_KEY}
      ENVIRONMENT: production
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: fini
      POSTGRES_PASSWORD: fini
      POSTGRES_DB: finidb
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redisdata:/data

  ollama:
    image: ollama/ollama
    restart: unless-stopped
    volumes:
      - ollama_data:/root/.ollama

volumes:
  pgdata:
  redisdata:
  ollama_data:
```

```
# .env.example
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=123456789:ABCxxxxxxxxxxxx
TELEGRAM_SECRET_TOKEN=seu_token_secreto_aleatorio
ADMIN_API_KEY=sua_api_key_admin
```

---

## 14. Testes

### 14.1 Parser (F9) — mínimo 30 casos

```python
# tests/test_finance_parser.py

import pytest
from app.flows.finance_flow import ParsedTransaction

# Cada caso: (input_text, expected_type, expected_amount, expected_category)
PARSER_TEST_CASES = [
    # Gastos básicos
    ("Gastei R$18,50 num lanche hoje",      "expense", 18.50, "Alimentação"),
    ("paguei 12 conto no ônibus",           "expense", 12.00, "Transporte"),
    ("netflix 37 reais",                    "expense", 37.00, "Assinaturas"),
    ("fui no cinema gastei 28",             "expense", 28.00, "Lazer"),
    ("comprei tênis por 120",               "expense", 120.00, "Compras"),
    ("remédio na farmácia 23,90",           "expense", 23.90, "Saúde"),
    ("apostila do cursinho 45",             "expense", 45.00, "Educação"),
    ("uber pra casa 15,50",                 "expense", 15.50, "Transporte"),
    ("pizza delivery 52",                   "expense", 52.00, "Alimentação"),
    ("spotify 21,90",                       "expense", 21.90, "Assinaturas"),
    # Receitas básicas
    ("recebi 200 de mesada",                "income",  200.00, "Mesada"),
    ("mesada chegou 350",                   "income",  350.00, "Mesada"),
    ("freela de design 400 reais",          "income",  400.00, "Freelas"),
    ("estágio caiu hoje 800",               "income",  800.00, "Estágio"),
    ("ganhei 50 de presente",               "income",  50.00, "Presente"),
    # Datas relativas
    ("ontem gastei 30 no lanche",           "expense", 30.00, "Alimentação"),
    ("paguei ônibus ontem 4,40",            "expense", 4.40,  "Transporte"),
    ("semana passada freela 180",           "income",  180.00, "Freelas"),
    # Formatos variados de valor
    ("lanche 8 reais",                      "expense", 8.00,  "Alimentação"),
    ("gastei R$ 23,00 no mercado",          "expense", 23.00, "Alimentação"),
    ("25.00 de uber",                       "expense", 25.00, "Transporte"),
    ("cinquenta reais de mesada",           "income",  50.00, "Mesada"),  # por extenso (bonus)
    # Linguagem informal
    ("fui no mc gastei uns 15",             "expense", 15.00, "Alimentação"),
    ("bala de goma 2,50",                   "expense", 2.50,  "Alimentação"),
    ("passei no caixa eletrônico tirei 50", None, None, None),  # não é lançamento
    ("oi tudo bem",                         None, None, None),
    ("quanto é 10% de 200?",               None, None, None),
    # Assinaturas diversas
    ("amazon prime 19,90",                  "expense", 19.90, "Assinaturas"),
    ("icloud 4,90",                         "expense", 4.90,  "Assinaturas"),
    ("academia 80 reais esse mês",          "expense", 80.00, "Assinaturas"),
]
```

### 14.2 Geração de XLSX

```python
# tests/test_xlsx_export.py

import io
from decimal import Decimal
from datetime import date
from openpyxl import load_workbook
from app.flows.xlsx_export import generate_xlsx

def make_sample_transactions():
    return [
        {"date": date(2026, 5, 1), "type": "income", "category": "Mesada",
         "description": "Mesada maio", "amount": Decimal("300.00")},
        {"date": date(2026, 5, 2), "type": "expense", "category": "Alimentação",
         "description": "Lanche", "amount": Decimal("18.50")},
        {"date": date(2026, 5, 3), "type": "expense", "category": "Transporte",
         "description": "Ônibus", "amount": Decimal("12.00")},
    ]

def test_xlsx_has_two_sheets():
    buf = generate_xlsx("João", 5, 2026, make_sample_transactions(), Decimal("300"))
    wb = load_workbook(buf)
    assert "Lançamentos" in wb.sheetnames
    assert "Resumo" in wb.sheetnames

def test_xlsx_lancamentos_row_count():
    transactions = make_sample_transactions()
    buf = generate_xlsx("João", 5, 2026, transactions, Decimal("300"))
    wb = load_workbook(buf, data_only=True)
    ws = wb["Lançamentos"]
    # Linha 1: título, Linha 2: cabeçalho, Linhas 3+: dados, Última: total
    data_rows = ws.max_row - 3  # -1 título -1 cabeçalho -1 total
    assert data_rows == len(transactions)

def test_xlsx_resumo_has_income_row():
    buf = generate_xlsx("João", 5, 2026, make_sample_transactions(), Decimal("300"))
    wb = load_workbook(buf, data_only=True)
    ws = wb["Resumo"]
    values = [ws.cell(row=r, column=1).value for r in range(1, ws.max_row + 1)]
    assert "Total de Receitas" in values

def test_xlsx_returns_bytesio():
    buf = generate_xlsx("João", 5, 2026, make_sample_transactions(), Decimal("300"))
    assert isinstance(buf, io.BytesIO)
    assert buf.tell() == 0  # ponteiro no início para envio
```

### 14.3 Gamificação

```python
# tests/test_gamification.py

from app.services.gamification_service import calculate_level, LEVEL_THRESHOLDS

def test_level_0_pts():
    assert calculate_level(0) == 1

def test_level_exactly_200():
    assert calculate_level(200) == 2

def test_level_exactly_500():
    assert calculate_level(500) == 3

def test_level_1999():
    assert calculate_level(1999) == 4

def test_level_2000():
    assert calculate_level(2000) == 5

def test_level_above_2000():
    assert calculate_level(9999) == 5
```

---

## 15. Infraestrutura e Hospedagem

### 15.1 Hospedagem recomendada (free tier)

| Serviço | Uso | Free Tier |
|---|---|---|
| **Railway** | Backend FastAPI | Deploy via GitHub |
| **Supabase** | PostgreSQL | 500MB + conexões ilimitadas |
| **Upstash** | Redis | 10k comandos/dia |
| **Groq** | LLM principal | 14.400 tokens/min |
| **Telegram Bot API** | Canal | 100% gratuito |
| **GitHub Actions** | CI/CD | Gratuito (repo público) |
| **Cloudflare Tunnel** | HTTPS local dev | Gratuito |

**Custo total estimado: R$4/mês** (só domínio + SSL)

### 15.2 Comandos de setup rápido

```bash
# 1. Clonar e configurar
git clone https://github.com/seu-usuario/finibot
cd finibot
cp .env.example .env
# Editar .env com suas chaves

# 2. Subir ambiente local
docker compose up -d

# 3. Rodar migrations
docker compose exec fini-api alembic upgrade head

# 4. Popular desafios no banco
docker compose exec fini-api python scripts/seed_challenges.py

# 5. Configurar webhook (produção)
curl "https://api.telegram.org/bot${TOKEN}/setWebhook" \
  -d "url=https://seu-dominio.fly.dev/telegram/webhook" \
  -d "secret_token=${TELEGRAM_SECRET_TOKEN}"

# 6. Rodar testes
docker compose exec fini-api pytest tests/ -v --cov=app
```

---

## 16. Plano de Validação com Estudantes

### 16.1 Sequência de atividades (30–60 min)

| Momento | Atividade | Evidência coletada |
|---|---|---|
| Antes | Questionário pré: hábitos financeiros, familiaridade com conceitos | Linha de base |
| Início | Onboarding no Telegram (5 min) | Taxa de conclusão sem ajuda |
| Atividade 1 | Registrar 3 lançamentos fictícios ou reais não-sensíveis (10 min) | Qualidade do parsing, erros percebidos |
| Atividade 2 | Consultar `/resumo` e interpretar os dados (10 min) | Compreensão de saldo, porcentagem |
| Atividade 3 | Criar uma meta com `/meta` e usar `/simular` (10 min) | Engajamento com planejamento |
| Atividade 4 | Exportar `/planilha` e abrir no celular ou PC (5 min) | Usabilidade, legibilidade |
| Depois | Questionário pós: percepção de utilidade, clareza, intenção de uso | Feedback qualitativo |

### 16.2 Critérios de sucesso do piloto

- ≥ 80% dos estudantes completam o onboarding sem ajuda técnica
- ≥ 70% conseguem registrar uma receita e um gasto corretamente
- ≥ 70% compreendem o saldo exibido no `/resumo`
- Feedback majoritariamente positivo sobre linguagem e utilidade
- Zero coleta de dados sensíveis durante a atividade

---

## 17. Estimativa de Custo

| Item | Custo/Mês |
|---|---|
| **Railway** (backend) | R$0 |
| Supabase (PostgreSQL) | R$0 |
| Upstash (Redis) | R$0 |
| Groq (LLM OSS) | R$0 |
| Telegram Bot API | R$0 |
| GitHub Actions (CI/CD) | R$0 |
| Domínio + SSL | ~R$4 |
| **TOTAL** | **~R$4/mês** |

---

## 18. Próximos Passos

```
Semana 1-2  → Setup: repo GitHub, Docker Compose, schema DB, CI/CD
Semana 3-4  → Sprint 1: Onboarding (F1) + Finance Flow base (F9.1 + F9.3)
Semana 5-6  → Sprint 2: XLSX Export (F9.4) + Gamificação (F5) + Metas (F6)
Semana 7-8  → Sprint 3: Q&A (F2) + Desafios (F4) + Simulador (F3)
Semana 9-10 → Sprint 4: Relatório mensal (F7) + testes + revisão pedagógica
Semana 11+  → Piloto com estudantes + coleta de feedback + ajustes
```

---

*Fini — Seu Parceiro Financeiro | SDD v2.1 | 2026-06-24*
*Revisão de: SDD v2.0 (2026-05-23)*
