# 📐 SDD — Software Design Document
## Fini: Seu Parceiro Financeiro
**Versão:** 1.2  
**Data:** 2026-04-27  
**Baseado em:** PRD FinBot Jovem v1.0  
**Estratégia:** Open-Source First  
**Contexto acadêmico:** Especialização em Ciências da Natureza e Matemática  

---

## 1. Visão Geral

O **Fini** é um chatbot educacional de finanças pessoais voltado ao público jovem (13–21 anos), distribuído via **Telegram**. Seu diferencial está na persona acolhedora ("parceiro financeiro"), na gamificação leve, no registro prático de receitas e despesas e na abordagem pedagógica conectada à BNCC.

Este documento define a proposta pedagógica, a metodologia de desenvolvimento e validação, a arquitetura técnica, as escolhas de tecnologia open-source, os modelos de dados, os fluxos de sistema e o plano de implementação. Também serve como material de alinhamento para professor orientador, equipe técnica e estudantes participantes da validação.

### 1.1 Objetivo do Projeto

O objetivo geral do Fini é apoiar estudantes jovens no desenvolvimento de noções de educação financeira por meio de uma ferramenta conversacional simples, acessível e de baixo custo, integrando conceitos de Matemática, consumo consciente e tomada de decisão.

Objetivos específicos:

1. Promover a compreensão de conceitos como receita, despesa, saldo, porcentagem, juros, metas e planejamento financeiro.
2. Estimular o registro diário de gastos e receitas para que o estudante identifique padrões de consumo.
3. Relacionar situações financeiras cotidianas com conteúdos de Matemática e Ciências da Natureza, como proporcionalidade, análise de dados, gráficos, sustentabilidade e consumo responsável.
4. Oferecer um ambiente seguro para perguntas sobre finanças pessoais, sem coleta de dados bancários ou informações sensíveis.
5. Produzir evidências de validação com estudantes, permitindo avaliar clareza, engajamento, utilidade percebida e adequação pedagógica.

### 1.2 Público-Alvo da Validação

A validação será realizada com estudantes jovens, preferencialmente entre 13 e 21 anos, em contexto escolar, projeto de extensão, oficina pedagógica ou atividade orientada. A participação deve ocorrer mediante autorização institucional e, quando necessário, autorização de responsáveis legais, respeitando a LGPD e as normas éticas da instituição.

Durante a validação, os estudantes usarão o bot no Telegram para:

- realizar o onboarding e o quiz diagnóstico;
- fazer perguntas sobre finanças pessoais;
- simular escolhas financeiras;
- registrar receitas mensais, como mesada, estágio, freelas ou presentes;
- registrar despesas por categoria, como alimentação, transporte, lazer, estudos e assinaturas;
- acompanhar saldo mensal automático;
- criar metas de economia e planejamento por objetivos;
- solicitar resumo visual em texto e planilha `.xlsx` com lançamentos e resumo por categoria.

### 1.3 Metodologia de Desenvolvimento e Validação

O projeto seguirá uma metodologia aplicada, iterativa e orientada por evidências, combinando desenvolvimento incremental de software com validação pedagógica junto aos estudantes.

| Etapa | Descrição | Produto esperado |
|---|---|---|
| 1. Planejamento pedagógico | Definição dos conteúdos de educação financeira, Matemática e consumo consciente que serão trabalhados pelo bot | Matriz de temas, objetivos de aprendizagem e critérios de validação |
| 2. Desenvolvimento do MVP | Implementação dos fluxos principais no Telegram: onboarding, Q&A, simulador, desafios, metas, controle financeiro e exportação de planilha | Bot funcional para teste piloto |
| 3. Validação técnica interna | Testes unitários, testes de integração, revisão de mensagens e checagem de privacidade | Versão estável para uso com estudantes |
| 4. Aplicação com estudantes | Uso orientado do bot em atividade prática, oficina ou sequência didática | Registros de uso, respostas dos estudantes e observações do professor |
| 5. Coleta de feedback | Questionário pré/pós, roteiro de observação e avaliação da experiência | Dados qualitativos e quantitativos de validação |
| 6. Análise e melhoria | Análise dos resultados, identificação de problemas e ajustes no bot | Relatório de validação e backlog de melhorias |

Indicadores sugeridos para validação:

- clareza das respostas do bot;
- facilidade de uso no Telegram;
- compreensão dos conceitos financeiros e matemáticos;
- engajamento dos estudantes;
- utilidade do registro de gastos e receitas;
- percepção sobre metas de economia;
- adequação da linguagem para a faixa etária;
- erros ou limitações percebidos durante o uso.

### 1.4 Princípios de Design
| # | Princípio | Implicação |
|---|---|---|
| 1 | **Open-Source First** | Priorizar soluções com licença MIT/Apache/GPL antes de SaaS proprietário |
| 2 | **Custo Mínimo no MVP** | Free tiers > planos pagos; evitar lock-in de vendor |
| 3 | **Privacidade por Design** | Coletar apenas o necessário; nada de dados sensíveis |
| 4 | **Resiliência** | Fallback gracioso quando serviços externos falharem |
| 5 | **Pedagogia Antes de Tech** | A UX do chat deve servir ao aprendizado, não ao contrário |
| 6 | **Validação com Estudantes** | Evoluir o produto a partir de evidências reais de uso, feedback e observação pedagógica |

---

## 2. Stack Tecnológica — Open-Source First

### 2.1 Comparação: PRD Original vs. Proposta Open-Source

| Componente | PRD Original (proprietário) | ✅ Proposta Open-Source |
|---|---|---|
| **LLM / IA** | Claude API (Anthropic) | **Ollama** + `llama3.2` ou `gemma3:4b` (local) / **OpenRouter** com modelos OSS como `mistral-7b` como fallback gerenciado |
| **Canal de Mensagens** | WhatsApp Business API (Meta) | ✅ **Telegram Bot API** — 100% gratuito, sem aprovação, sem número comercial. Token gerado em < 1 min via @BotFather |
| **Backend** | Node.js / FastAPI no Railway | **FastAPI** (Python) + **Docker Compose** — auto-hospedado ou no **Fly.io** (free tier generoso) |
| **Banco de Dados** | Supabase (PostgreSQL) | **PostgreSQL** diretamente (via Docker) + **SQLAlchemy** ORM |
| **Fila de Mensagens** | Redis (Upstash) | **Redis OSS** via Docker / **RQ** (Redis Queue) |
| **Monitoramento** | Sentry | **GlitchTip** (clone open-source do Sentry) ou **Grafana** + **Loki** |
| **Testes** | Jest / Pytest | **Pytest** + **pytest-asyncio** + **httpx** para testes de integração |
| **CI/CD** | — | **GitHub Actions** (gratuito para repositórios públicos) |
| **Orquestração** | — | **Docker Compose** para dev; **Coolify** (PaaS open-source) para produção |

### 2.2 Stack Final Recomendada

```
┌─────────────────────────────────────────────────────────┐
│                    CANAL DE ENTRADA                     │
│            Telegram Bot API (100% gratuito)             │
│  python-telegram-bot (OSS) ◄──── webhook / polling     │
└──────────────────────┬──────────────────────────────────┘
                       │ Webhook HTTPS / Long Polling
                       ▼
┌─────────────────────────────────────────────────────────┐
│              BACKEND — FastAPI (Python 3.12)            │
│  • Telegram Handler • Session Manager • Prompt Builder │
│  • Gamification Engine  • Challenge Engine             │
│  • Finance Flow         • XLSX Export                  │
└────────┬────────────────────┬──────────────────────────┘
         │                    │
         ▼                    ▼
┌────────────────┐   ┌────────────────────────────────────┐
│  PostgreSQL    │   │         LLM Gateway                │
│  (SQLAlchemy)  │   │  Groq + Llama 3.3 70B (primary)   │
│  Usuários      │   │  Ollama + Gemma 3 4B (fallback)   │
│  Metas         │   │  System prompt pedagógico (Fini)   │
│  Lançamentos   │   └────────────────────────────────────┘
│  Pontos        │
│  Histórico     │
│  Resumos XLSX  │
└────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Redis OSS (via Docker)                     │
│  • Rate limiting (30 msg/usuário/hora)                 │
│  • Session cache  • Filas assíncronas (RQ)             │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Justificativa das Escolhas de LLM

| Opção | Tipo | Custo | Privacidade | Qualidade PT-BR | Recomendação |
|---|---|---|---|---|---|
| **Ollama + Llama 3.2 (3B)** | Local / OSS | Gratuito | ✅ Máxima | Boa | MVP local / dev |
| **Ollama + Gemma 3 (4B)** | Local / OSS | Gratuito | ✅ Máxima | Muito boa | MVP local / dev |
| **OpenRouter (Mistral 7B OSS)** | API / OSS | ~$0.07/1M tokens | Média | Boa | Produção low-cost |
| **Groq + Llama 3 (70B)** | API / OSS | Free tier generoso | Média | Excelente | Produção MVP |
| ~~Claude Sonnet~~ | API proprietária | $3/1M tokens | Baixa | Excelente | Evitar |

> **Decisão:** Usar **Groq API** (free tier) com `llama-3.3-70b-versatile` em produção MVP. É OSS, tem latência < 500ms, e o free tier cobre largamente as necessidades do piloto. Fallback: `gemma3:4b` via Ollama no servidor.

---

## 3. Arquitetura de Componentes

### 3.1 Diagrama de Componentes

```
finibot/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── api/
│   │   ├── telegram_handler.py  # Handler Telegram (python-telegram-bot)
│   │   └── health.py            # Health check endpoint
│   ├── core/
│   │   ├── config.py            # Configurações (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   └── redis_client.py      # Redis connection
│   ├── models/
│   │   ├── user.py              # Modelo User (ORM)
│   │   ├── goal.py              # Modelo Goal (metas)
│   │   ├── transaction.py       # Receitas, despesas e categorias
│   │   ├── challenge.py         # Modelo Challenge (desafios)
│   │   └── message_log.py       # Log de mensagens
│   ├── services/
│   │   ├── llm_service.py       # Abstração LLM (Groq/Ollama)
│   │   ├── telegram_service.py  # Envio e formatação de msgs Telegram
│   │   ├── session_service.py   # Gerenciamento de sessão
│   │   ├── gamification.py      # Pontos, níveis, conquistas
│   │   └── challenge_service.py # Desafios semanais
│   ├── flows/
│   │   ├── onboarding.py        # F1: Quiz de onboarding
│   │   ├── qa_engine.py         # F2: Q&A financeiro
│   │   ├── simulator.py         # F3: Guardar/gastar/investir
│   │   ├── finance_flow.py      # F9: Controle financeiro + planilha
│   │   └── report.py            # F7: Relatório mensal
│   └── prompts/
│       ├── system_prompt.py     # Persona Fini
│       └── templates.py         # Templates de mensagem
├── migrations/                  # Alembic migrations
├── tests/
│   ├── test_flows.py
│   ├── test_finance_flow.py
│   ├── test_gamification.py
│   └── test_llm_service.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

### 3.2 Módulo LLM Gateway (Abstração Open-Source)

```python
# app/services/llm_service.py (esboço)
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], system: str) -> str: ...

class GroqProvider(LLMProvider):
    """Groq API com Llama 3.3 70B (OSS) — free tier produção"""
    MODEL = "llama-3.3-70b-versatile"
    
class OllamaProvider(LLMProvider):
    """Ollama local — dev e fallback"""
    MODEL = "gemma3:4b"  # ou llama3.2

class LLMGateway:
    """Seleciona provedor com fallback automático"""
    def __init__(self):
        self.primary = GroqProvider()
        self.fallback = OllamaProvider()
```

---

## 4. Modelos de Dados

### 4.1 Entidades Principais

```sql
-- Usuário / Perfil
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id     BIGINT UNIQUE NOT NULL,  -- identificador Telegram (chat_id)
    name        VARCHAR(100),
    age         INTEGER,
    school      VARCHAR(200),
    points      INTEGER DEFAULT 0,
    level       INTEGER DEFAULT 1,         -- 1=Aprendiz → 5=Mestre
    onboarded   BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Metas Financeiras (F6)
CREATE TABLE goals (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    target_amount DECIMAL(10,2),
    current_amount DECIMAL(10,2) DEFAULT 0,
    deadline    DATE,
    completed   BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Controle Financeiro: receitas e despesas (F9)
CREATE TABLE transactions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(10) NOT NULL, -- 'income' ou 'expense'
    amount      DECIMAL(10,2) NOT NULL,
    category    VARCHAR(80) NOT NULL DEFAULT 'geral',
    description TEXT,
    happened_on DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Desafios Semanais (F4)
CREATE TABLE challenges (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    points_reward INTEGER DEFAULT 50,
    category    VARCHAR(50),  -- orcamento, poupanca, credito, etc.
    difficulty  VARCHAR(20)   -- facil, medio, dificil
);

-- Progresso do Usuário nos Desafios
CREATE TABLE user_challenges (
    user_id     UUID REFERENCES users(id),
    challenge_id UUID REFERENCES challenges(id),
    accepted_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    PRIMARY KEY (user_id, challenge_id)
);

-- Log de Mensagens (contexto de conversa)
CREATE TABLE message_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id),
    role        VARCHAR(10) NOT NULL,  -- 'user' ou 'assistant'
    content     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### 4.2 Sistema de Gamificação

| Nível | Nome | Pontos Necessários | Benefício |
|---|---|---|---|
| 1 | 🌱 Aprendiz | 0 | Acesso básico |
| 2 | 📚 Estudante | 200 | Desbloqueio de simulador avançado |
| 3 | 💡 Consciente | 500 | Desafios especiais |
| 4 | 🚀 Investidor | 1.000 | Relatório detalhado |
| 5 | 🏆 Mestre | 2.000 | Badge de honra |

| Ação | Pontos |
|---|---|
| Completar onboarding | +100 |
| Responder corretamente quiz | +20 |
| Completar desafio semanal | +50–150 |
| Definir uma meta | +30 |
| Fazer login 7 dias seguidos | +80 |

### 4.3 Controle Financeiro e Planilha

O módulo de controle financeiro transforma o Telegram em uma interface simples para registro e reflexão. A planilha `.xlsx` não é o banco principal do sistema; ela é uma exportação gerada sob demanda para facilitar a consulta pelo estudante, professor ou pesquisador.

Comandos previstos:

| Comando | Finalidade | Exemplo |
|---|---|---|
| `/receita` | Registrar dinheiro que entrou no mês | `/receita 200 mesada` |
| `/gasto` | Registrar despesa diária por categoria | `/gasto 18.50 alimentacao lanche` |
| `/resumo` | Exibir entradas, saídas, saldo e totais por categoria | `/resumo` |
| `/planilha` | Gerar e enviar arquivo `.xlsx` pelo Telegram | `/planilha` |

Categorias iniciais sugeridas:

- receitas: mesada, estágio, freela, presentes;
- despesas: alimentação, transporte, lazer, estudos, assinaturas;
- metas: celular, viagem, curso, reserva, material escolar.

A planilha exportada deve conter pelo menos duas abas:

1. **Lançamentos:** data, tipo, categoria, descrição e valor.
2. **Resumo:** total de receitas, total de despesas, saldo mensal e total gasto por categoria.

Esse módulo apoia diretamente a validação com estudantes porque gera evidências de aprendizagem e permite discutir leitura de tabelas, organização de dados, saldo, porcentagem, priorização e planejamento por objetivos.

---

## 5. Fluxos de Sistema

### 5.1 Fluxo Principal de Mensagem

```
Jovem envia mensagem no Telegram
        │
        ▼
Webhook FastAPI recebe POST /webhook
        │
        ▼
Rate Limiter (Redis) ──── limite excedido ───► Mensagem amigável de throttle
        │ ok
        ▼
Session Service: busca contexto + histórico recente (últimas 10 msgs)
        │
        ▼
Router de Intenção (regras simples + LLM):
  ├── /ajuda            ► Menu de opções (F8)
  ├── Onboarding needed ► Onboarding Flow (F1)
  ├── Pergunta financeira► QA Engine (F2)
  ├── /simular          ► Simulator Flow (F3)
  ├── /desafio          ► Challenge Service (F4)
  ├── /meta             ► Goal Manager (F6)
  ├── /receita          ► Finance Flow: registra entrada (F9)
  ├── /gasto            ► Finance Flow: registra despesa (F9)
  ├── /resumo           ► Resumo mensal e categorias (F9)
  ├── /planilha         ► Exportação XLSX (F9)
  └── Conversa livre    ► LLM Gateway com persona Fini
        │
        ▼
LLM Gateway: Groq (primary) ou Ollama (fallback)
  sistema: system_prompt.py (persona Fini + contexto pedagógico)
        │
        ▼
Gamification Engine: atualiza pontos/nível se aplicável
        │
        ▼
Telegram Service: envia resposta formatada (MarkdownV2)
        │
        ▼
Message Log: persiste interação no PostgreSQL
```

### 5.2 Fluxo de Onboarding (F1)

```
Estado: user.onboarded == False
  │
  ▼
Passo 1: Apresentação do Fini
  ▼
Passo 2: "Qual é o seu nome?"
  ▼
Passo 3: "Qual a sua idade?"
  ▼
Passo 4: Quiz diagnóstico (3 perguntas de múltipla escolha)
  Pergunta 1: Quando você recebe grana, o que faz primeiro?
    A) Gasto logo  B) Guardo uma parte  C) Depende do mês
  Pergunta 2: Você já ouviu falar em juros compostos?
    A) Sim e entendo  B) Já ouvi mas não sei  C) Nunca ouvi
  Pergunta 3: Você tem algum objetivo financeiro agora?
    A) Sim, tenho  B) Quero ter mas não sei  C) Não pensei nisso
  ▼
Passo 5: Diagnóstico personalizado baseado nas respostas
  ▼
Passo 6: +100 pontos → user.onboarded = True
```

### 5.3 System Prompt da Persona Fini

```
Você é o Fini, parceiro de educação financeira de jovens brasileiros de 13 a 21 anos.

PERSONALIDADE:
- Tom: Amigável, direto, levemente bem-humorado — como um colega mais experiente
- NUNCA use: termos como 'liquidez de portfólio', 'hedge', 'alavancagem', frases formais de banco
- SEMPRE use: exemplos reais com valores em reais ('tipo, se você guardar R$5 por dia...')
- Celebre conquistas: 'Arrasou! Você acabou de aprender juros compostos 🔥'
- Acolha erros: 'Sem julgamento. Vamos entender o que aconteceu?'
- Inspire ação: termine com uma pergunta ou um desafio pequeno e concreto

REGRAS:
1. Mensagens curtas: máx. 150 palavras por resposta
2. Use emojis com moderação (máx. 3 por mensagem)
3. Nunca dê conselhos de investimento específicos ('compre ação X')
4. Se a pergunta fugir de finanças, redirecione gentilmente
5. Se não souber algo, diga 'Boa pergunta! Deixa eu checar isso pra você' (não invente)
6. Tópicos cobertos: orçamento, poupança, crédito, investimentos básicos, consumo consciente, matemática financeira

CONTEXTO DO USUÁRIO:
Nome: {user_name} | Nível: {level} | Pontos: {points}
```

### 5.4 Fluxo de Validação com Estudantes

```
Professor/equipe apresenta a atividade e orienta o uso responsável
        │
        ▼
Estudante acessa o Fini no Telegram e realiza onboarding
        │
        ▼
Atividade 1: pergunta guiada sobre orçamento, consumo ou juros
        │
        ▼
Atividade 2: registro de receitas e gastos fictícios ou reais não sensíveis
        │
        ▼
Atividade 3: criação de meta financeira e análise de prioridades
        │
        ▼
Atividade 4: consulta de /resumo e /planilha
        │
        ▼
Questionário curto de feedback + observação do professor
        │
        ▼
Equipe analisa dados agregados e define melhorias
```

Instrumentos sugeridos:

- questionário diagnóstico antes do uso;
- questionário de percepção após o uso;
- roteiro de observação para professor ou pesquisador;
- análise dos comandos mais usados e dúvidas mais frequentes;
- registro de problemas técnicos e sugestões dos estudantes.

Critérios de sucesso do piloto:

- pelo menos 80% dos estudantes conseguem completar o onboarding sem ajuda técnica;
- pelo menos 70% conseguem registrar uma receita e um gasto corretamente;
- pelo menos 70% compreendem o saldo mensal exibido pelo bot;
- feedback majoritariamente positivo sobre clareza, linguagem e utilidade;
- ausência de coleta de dados sensíveis durante a atividade.

---

## 6. API Endpoints

### 6.1 Endpoints FastAPI

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/telegram/webhook` | Recebe updates do Telegram (modo webhook) |
| `GET` | `/health` | Health check (para uptime monitoring) |
| `GET` | `/users/{telegram_id}/profile` | Perfil do usuário (admin) |
| `GET` | `/users/{telegram_id}/goals` | Metas do usuário |
| `POST` | `/users/{telegram_id}/goals` | Criar nova meta |
| `GET` | `/challenges` | Lista desafios disponíveis |
| `GET` | `/admin/stats` | Estatísticas do piloto (protegido) |

### 6.2 Segurança

- Autenticação do webhook via **token secreto** no header `X-Telegram-Bot-Api-Secret-Token`
- Endpoints de admin protegidos por **API Key** no header
- Nenhum dado sensível (CPF, senha) é coletado ou armazenado
- Rate limiting via Redis: 30 mensagens/usuário/hora
- Toda comunicação via **HTTPS** (TLS 1.3) — Telegram só aceita webhook em HTTPS

---

## 7. Infraestrutura e Deploy

### 7.1 Docker Compose (Desenvolvimento e Produção)

```yaml
# docker-compose.yml (esboço)
services:
  fini-api:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
      - GROQ_API_KEY=${GROQ_API_KEY}         # LLM OSS via Groq
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}  # Token do @BotFather
      - TELEGRAM_SECRET_TOKEN=${TELEGRAM_SECRET_TOKEN}  # webhook security
      - OLLAMA_BASE_URL=http://ollama:11434  # fallback LLM
    depends_on: [postgres, redis]

  postgres:
    image: postgres:16-alpine       # OSS ✅
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine           # OSS ✅
    
  ollama:                           # OSS ✅ fallback LLM (offline)
    image: ollama/ollama
    volumes: ["ollama_data:/root/.ollama"]

  glitchtip:                        # OSS ✅ (Sentry clone)
    image: glitchtip/glitchtip
    
volumes:
  pgdata:
  ollama_data:
```

### 7.2 Opções de Hospedagem (Free Tier)

| Serviço | Tipo | Free Tier | Recomendação |
|---|---|---|---|
| **Fly.io** | PaaS | 3 VMs 256MB | ✅ Backend FastAPI |
| **Render** | PaaS | 750h/mês | ✅ Alternativa |
| **Supabase** | DBaaS | 500MB PostgreSQL | ✅ Banco de dados |
| **Upstash** | Redis | 10k cmd/dia | ✅ Redis rate limit |
| **Groq** | LLM API | 14.4k tokens/min | ✅ LLM principal |
| **Telegram Bot API** | Canal | 100% gratuito, sem limites | ✅ Canal obrigatório |
| **Cloudflare Tunnel** | Tunnel | Gratuito | ✅ Expor localhost no dev |

### 7.3 Plano de Migração para Self-Hosted (Coolify)

Para maior controle e privacidade, toda a stack pode ser migrada para **Coolify** (PaaS open-source) em um VPS simples (DigitalOcean/Hetzner ~R$25/mês):

```
VPS (4GB RAM, 2 vCPUs)
└── Coolify (auto-deploy via GitHub)
    ├── fini-api (FastAPI)
    ├── PostgreSQL 16
    ├── Redis 7
    ├── Ollama (Gemma 3 4B) — fallback LLM offline
    └── GlitchTip (monitoramento)
```

---

## 8. Plano de Testes

### 8.1 Testes Unitários (Pytest)

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx pytest-cov

# Executar todos os testes
pytest tests/ -v --cov=app --cov-report=html
```

Cobertura esperada:
- `test_gamification.py` — Cálculo de pontos e nível
- `test_finance_flow.py` — Parser de receitas/gastos, resumo mensal e geração de `.xlsx`
- `test_flows.py` — Fluxo de onboarding, Q&A, simulador
- `test_rate_limiter.py` — Limite de 30 msg/hora
- `test_llm_service.py` — Mock do provider LLM

### 8.2 Validação Pedagógica com Estudantes

A validação pedagógica deverá observar tanto a qualidade da interação quanto a aprendizagem percebida. O professor/equipe poderá aplicar uma atividade de 30 a 60 minutos com os estudantes, usando o bot como apoio para discutir orçamento, planejamento, metas, consumo consciente e interpretação de dados.

Plano sugerido:

| Momento | Atividade | Evidência |
|---|---|---|
| Antes | Questionário rápido sobre hábitos financeiros e familiaridade com conceitos matemáticos | Linha de base |
| Durante | Uso do bot para perguntas, simulações, registro de receitas/gastos e criação de metas | Observação e logs agregados |
| Depois | Questionário de percepção e discussão guiada | Feedback qualitativo e quantitativo |
| Análise | Comparação entre objetivos de aprendizagem e experiência real | Relatório de validação |

Cuidados éticos:

- não solicitar CPF, dados bancários, senhas, extratos ou informações familiares sensíveis;
- permitir que os estudantes usem valores fictícios durante a atividade;
- tratar resultados de forma agregada, sem exposição individual;
- solicitar autorização institucional e consentimento quando aplicável.

### 8.3 Testes de Integração

```bash
# Sobe ambiente de teste
docker compose -f docker-compose.test.yml up -d

# Roda testes de integração
pytest tests/integration/ -v
```

### 8.4 Teste de Carga (MVP)

```bash
# k6 (OSS) — simula 200 usuários simultâneos
k6 run --vus 200 --duration 60s tests/load/webhook_test.js
```

Meta: **< 3 segundos** de latência para p95 com 200 usuários simultâneos.

---

## 9. Cronograma Técnico

| Fase | Entregas Técnicas | Prazo |
|---|---|---|
| **Fase 0 — Setup** | Repositório GitHub, Docker Compose, schema DB, CI/CD (GitHub Actions), configuração Groq API | Sem 1–2 |
| **Fase 1 — MVP Técnico** | Flows F1–F8, LLM Gateway, Gamification Engine, controle financeiro F9, exportação `.xlsx`, testes unitários | Sem 3–8 |
| **Fase 2 — Preparação Pedagógica** | Roteiro de atividade, questionários, termo de uso/consentimento, revisão da linguagem e privacidade | Sem 9–10 |
| **Fase 3 — Piloto com Estudantes** | Aplicação orientada, coleta de feedback, observação docente, ajuste de prompts e comandos | Sem 11–16 |
| **Fase 4 — Análise** | Dados agregados, relatório de validação, dashboard opcional, recomendações para nova versão | Sem 17–20 |

---

## 10. Riscos Técnicos e Mitigações

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Groq free tier excedido no piloto | Média | Fallback para Ollama local; roteamento por complexidade (perguntas simples → template, complexas → LLM) |
| Telegram banir bot por spam | Baixa | Respeitar rate limits da API (30 msg/s); usar rate limiter Redis; opt-in explícito dos usuários |
| Qualidade do PT-BR no LLM OSS | Média | Fine-tuning do system prompt; teste A/B de modelos; Groq/Llama 3.3 70B tem boa cobertura PT-BR |
| Latência Ollama local para produção | Alta | Utilizar Ollama apenas como fallback; Groq tem latência < 500ms na maioria dos casos |
| Privacidade dos dados de menores | Baixa | LGPD: termo de uso claro, sem dados sensíveis, dados deletados ao pedido |
| Estudantes informarem dados financeiros reais sensíveis | Média | Orientação prévia para uso de valores fictícios ou genéricos; mensagens do bot reforçando que não deve enviar dados bancários |
| Baixo engajamento na atividade de validação | Média | Roteiro curto, tarefas práticas, exemplos próximos da realidade dos estudantes e acompanhamento do professor |

---

## 11. Estimativa de Custo Open-Source

| Item | Custo/Mês | Observação |
|---|---|---|
| Fly.io (backend) | **R$0** | Free tier 3 VMs |
| Supabase (PostgreSQL) | **R$0** | Free 500MB |
| Upstash (Redis) | **R$0** | Free 10k cmd/dia |
| Groq API (LLM OSS) | **R$0** | Free tier muito generoso |
| Telegram Bot API | **R$0** | 100% gratuito, sem limites de usuários |
| GitHub Actions (CI/CD) | **R$0** | Repo público |
| Domínio + SSL | **~R$4** | Único custo fixo |
| **TOTAL MVP** | **~R$4/mês** | vs. R$80–200/mês do PRD original |

> 🎯 **Redução de custo: > 95%** em relação à proposta original do PRD, com stack 100% open-source.

---

## 12. Próximos Passos

1. **Aprovação deste SDD** pela equipe
2. Validar com o professor orientador o objetivo pedagógico, faixa etária e contexto de aplicação
3. Preparar roteiro da atividade com estudantes, questionário pré/pós e critérios de análise
4. Criar bot no Telegram via **@BotFather** → obter `TELEGRAM_BOT_TOKEN`
5. Configurar Docker Compose local com PostgreSQL + Redis + Ollama
6. Testar os fluxos de onboarding, perguntas, metas, receitas, gastos, resumo e planilha
7. Realizar teste interno com 3–5 jovens voluntários antes do piloto formal
8. Aplicar piloto orientado com estudantes, usando valores fictícios ou não sensíveis
9. Consolidar feedback, métricas agregadas e recomendações em relatório para a especialização

---

*Documento v1.2 — Atualizado com objetivo acadêmico, metodologia de validação com estudantes e módulo de controle financeiro com exportação `.xlsx`. Baseado no PRD FinBot Jovem v1.0. Revisão recomendada a cada sprint (2 semanas).*
