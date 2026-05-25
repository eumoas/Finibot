# 🎯 project.md — Termo de Abertura do Projeto
## Fini: Seu Parceiro Financeiro
**Versão:** 1.0 | **Data:** 2026-04-04 | **Status:** Em Planejamento

---

## 1. Visão do Produto

> **"Um jovem que entende de finanças antes dos 20 anos muda sua trajetória de vida."**

O **Fini** é um chatbot de educação financeira distribuído via **Telegram**, projetado para ser o "parceiro financeiro" de jovens brasileiros de 13 a 21 anos. Em vez de um app que precisa ser baixado ou um curso que exige comprometimento, o Fini encontra o jovem onde ele já está — no chat — e ensina finanças de forma conversacional, gamificada e sem jargões bancários.

### 1.1 Problema a Resolver

| Sintoma | Evidência |
|---|---|
| Jovens gastam antes de poupar | 72% dos jovens brasileiros não têm reserva de emergência (SPC Brasil, 2023) |
| Educação financeira formal é insuficiente | Apenas 30% das escolas abordam finanças pessoais (ENEF, 2022) |
| Aplicativos financeiros têm baixa retenção | Mediana de abandono em apps de finanças: < 7 dias (App Annie) |
| Conteúdo disponível é inadequado para jovens | Linguagem técnica e exemplos irrelevantes para a realidade de quem tem mesada |

### 1.2 Proposta de Valor

```
Para jovens de 13–21 anos
Que querem entender e controlar seu dinheiro
O Fini é um chatbot conversacional no Telegram
Que ensina finanças pessoais de forma gamificada e personalizada
Diferente de apps de controle financeiro ou cursos online
Ele conversa, desafia e celebra cada pequena conquista financeira do usuário
```

---

## 2. Objetivos

### 2.1 Objetivos de Negócio / Pesquisa

| # | Objetivo | Meta (Piloto 16 semanas) | Métrica |
|---|---|---|---|
| O1 | Aumentar o conhecimento financeiro dos jovens | +30% no score pós-teste | Questionário financeiro pré/pós |
| O2 | Engajar jovens de forma sustentada | Retenção ≥ 40% após 4 semanas | DAU/WAU no banco de dados |
| O3 | Validar abordagem conversacional | NPS ≥ 50 | Pesquisa de satisfação |
| O4 | Gerar evidência acadêmica | Artigo publicado em periódico Qualis B1+ | Submissão pós-piloto |

### 2.2 Objetivos de Produto (MVP)

- ✅ Bot funcional no Telegram com persona consistente (Fini)
- ✅ Onboarding conversacional com quiz de diagnóstico
- ✅ Motor de Q&A cobrindo ≥ 50 tópicos de finanças pessoais
- ✅ Simulador básico (poupar x gastar x investir)
- ✅ Sistema de gamificação (pontos + 5 níveis)
- ✅ Desafios semanais (biblioteca de 20+ desafios)
- ✅ Registro e acompanhamento de metas financeiras

---

## 3. Escopo

### 3.1 Dentro do Escopo — MVP (Versão 1.0)

| ID | Feature | Prioridade |
|---|---|---|
| F1 | Onboarding conversacional com quiz de diagnóstico | 🔴 Must Have |
| F2 | Motor de Q&A: responde perguntas sobre finanças pessoais (≥ 50 tópicos) | 🔴 Must Have |
| F3 | Simulador básico: guardar vs. gastar vs. investir | 🔴 Must Have |
| F4 | Desafios semanais (biblioteca de 20+ desafios) | 🟡 Should Have |
| F5 | Sistema de pontos e níveis (gamificação leve) | 🟡 Should Have |
| F6 | Registro de metas financeiras pessoais | 🟡 Should Have |
| F7 | Relatório de progresso mensal enviado pelo bot | 🟢 Could Have |
| F8 | Comando `/ajuda` com menu de opções rápidas | 🔴 Must Have |

### 3.2 Fora do Escopo — MVP (Versão 2.0+)

- Integração com Google Sheets para acompanhar gastos (F9)
- Modo Professor: painel de acompanhamento da turma (F10)
- Grupos de turma no Telegram com desafios colaborativos (F11)
- Mini-cursos temáticos: cripto, empreendedorismo, ENEM financeiro (F12)
- Integração com Open Finance (F13)
- Dashboard web para escola/professor (F14)

---

## 4. Público-Alvo

### 4.1 Perfis de Usuário (Personas)

#### 👦 Lucas — O Gastador Impulsivo
- **Idade:** 16 anos | Ensino Médio
- **Situação:** Recebe R$600/mês de mesada, gasta tudo antes do fim do mês
- **Dor:** "Sempre fico sem grana e não sei onde foi"
- **Motivação com o Fini:** Quer um plano concreto, não lições genéricas

#### 👧 Ana — A Curiosa Sem Direção
- **Idade:** 19 anos | 1º ano de faculdade
- **Situação:** Trabalha meio período, quer investir mas não sabe por onde começar
- **Dor:** "Ouço falar em Tesouro Direto mas parece complicado demais"
- **Motivação com o Fini:** Quer aprender na linguagem dela, sem jargão

#### 👦 Pedro — O Competitivo
- **Idade:** 14 anos | 8º ano
- **Situação:** Adora jogos e rankings, tem mesada pequena
- **Dor:** "Quero ser o mais esperto da turma em dinheiro"
- **Motivação com o Fini:** Gamificação e desafios semanais

---

## 5. Partes Interessadas

| Parte | Papel | Expectativa |
|---|---|---|
| **Pesquisador / Dev** | Criador e mantenedor | Validar hipótese acadêmica + construir produto funcional |
| **Escola parceira** | Facilitadora do piloto | Engajamento dos alunos, privacidade garantida |
| **Professores** | Agentes de divulgação | Facilidade de uso, relatórios claros |
| **Pais/Responsáveis** | Consentimento (< 18 anos) | Segurança, sem coleta de dados sensíveis |
| **Jovens usuários** | Usuários finais | Aprender sem ser chateado |

---

## 6. Cronograma

```
 Sem 1─2   │ Fase 0 — Setup
            │ • Repositório GitHub + CI/CD
            │ • Docker Compose (Postgres + Redis + Ollama)
            │ • Bot Telegram criado (@BotFather)
            │ • Schema DB inicial + migrations (Alembic)
 ───────────┼──────────────────────────────────────────────
 Sem 3─8   │ Fase 1 — MVP
            │ • Flows F1–F8 implementados
            │ • LLM Gateway (Groq + Ollama fallback)
            │ • Gamificação + Desafios
            │ • Deploy Fly.io
            │ • Testes internos com 5 beta testers
 ───────────┼──────────────────────────────────────────────
 Sem 9─16  │ Fase 2 — Piloto Escolar
            │ • 2–3 turmas parceiras (50–150 jovens)
            │ • Coleta de dados para pesquisa
            │ • Iteração com base em feedback
            │ • Questionários pré/pós
 ───────────┼──────────────────────────────────────────────
 Sem 17─20 │ Fase 3 — Análise e Publicação
            │ • Análise quantitativa e qualitativa
            │ • Elaboração do artigo acadêmico
            │ • Apresentação dos resultados
```

---

## 7. Orçamento

| Item | Custo/Mês |
|---|---|
| Fly.io (backend FastAPI) | R$0 — free tier |
| Supabase or PostgreSQL | R$0 — free tier |
| Redis (Upstash) | R$0 — free tier |
| Groq API (LLM Llama 3.3 70B) | R$0 — free tier |
| Telegram Bot API | R$0 — sem limites |
| GitHub Actions (CI/CD) | R$0 — repo público |
| Domínio + SSL | ~R$4/mês |
| **TOTAL** | **~R$4/mês** |

---

## 8. Riscos do Projeto

| Risco | Probabilidade | Impacto | Resposta |
|---|---|---|---|
| Baixo engajamento após 1ª semana | Alta | Alto | Gamificação + desafios semanais + notificações opt-in |
| Resistência de pais/escola por privacidade | Média | Alto | Termo de uso claro + apresentação prévia à gestão |
| Groq free tier excedido | Média | Médio | Fallback Ollama local + roteamento por complexidade |
| Qualidade do PT-BR no LLM | Média | Alto | System prompt refinado + teste A/B de modelos |
| Jovens testando limites do bot | Média | Baixo | Filtros no system prompt + fallback educativo |

---

## 9. Critérios de Sucesso do MVP

- [ ] Bot responde em < 3 segundos para 95% das mensagens
- [ ] Onboarding completo por ≥ 80% dos usuários que iniciam
- [ ] Retenção ≥ 40% na semana 4 do piloto
- [ ] Zero incidentes de privacidade (dados de menores)
- [ ] Score NPS ≥ 50 ao final do piloto

---

## 10. Stack Tecnológica (Resumo)

| Componente | Tecnologia |
|---|---|
| Canal | Telegram Bot API + `python-telegram-bot` |
| Backend | FastAPI (Python 3.12) |
| LLM | Groq API — `llama-3.3-70b-versatile` (OSS) |
| LLM Fallback | Ollama — `gemma3:4b` (local) |
| Banco de Dados | PostgreSQL 16 |
| Cache / Fila | Redis 7 OSS |
| Orquestração | Docker Compose |
| CI/CD | GitHub Actions |
| Monitoramento | GlitchTip (Sentry OSS clone) |

---

*Fini — Seu Parceiro Financeiro | project.md v1.0 | 2026-04-04*
