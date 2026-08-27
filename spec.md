# 📋 spec.md — Especificação de Requisitos
## Fini: Seu Parceiro Financeiro
**Versão:** 1.0 | **Data:** 2026-04-04

---

## 1. Convenções

| Sigla | Significado |
|---|---|
| RF | Requisito Funcional |
| RNF | Requisito Não-Funcional |
| 🔴 Must | Obrigatório para o MVP |
| 🟡 Should | Importante, mas pode ser diferido |
| 🟢 Could | Desejável se houver tempo |

---

## 2. Requisitos Funcionais

### 2.1 F1 — Onboarding Conversacional

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | O bot DEVE detectar se o usuário é novo (sem cadastro no banco) e iniciar o onboarding automaticamente | 🔴 Must |
| RF-02 | O onboarding DEVE coletar: nome e idade do usuário via mensagens de texto livre | 🔴 Must |
| RF-03 | O onboarding DEVE aplicar um quiz diagnóstico de 3 perguntas via InlineKeyboard do Telegram | 🔴 Must |
| RF-04 | As respostas do quiz DEVEM categorizar o usuário em um perfil (Iniciante / Em Desenvolvimento / Avançado) | 🔴 Must |
| RF-05 | Ao concluir o onboarding, o bot DEVE presentear o usuário com +100 pontos e exibir o perfil diagnosticado | 🔴 Must |
| RF-06 | O usuário DEVE poder refazer o onboarding com o comando `/recomecar` | 🟢 Could |

**Perguntas do Quiz Diagnóstico:**
```
Q1: Quando você recebe sua mesada/salário, o que faz primeiro?
    A) 💸 Gasto logo — o que sobrar eu guardo
    B) 🏦 Guardo uma parte antes de gastar
    C) 🤷 Depende do mês

Q2: Você já ouviu falar em juros compostos?
    A) ✅ Sim e entendo como funciona
    B) 🤔 Já ouvi, mas não sei direito
    C) ❌ Nunca ouvi esse nome

Q3: Você tem algum objetivo financeiro agora?
    A) 🎯 Sim, sei exatamente o que quero
    B) 💭 Quero ter, mas não sei como definir
    C) 😶 Não pensei nisso ainda
```

---

### 2.2 F2 — Motor de Q&A Financeiro

| ID | Requisito | Prioridade |
|---|---|---|
| RF-07 | O bot DEVE responder perguntas sobre finanças pessoais em linguagem acessível para jovens | 🔴 Must |
| RF-08 | O bot DEVE cobrir no mínimo 50 tópicos organizados em 6 categorias | 🔴 Must |
| RF-09 | Respostas DEVEM ter no máximo 150 palavras | 🔴 Must |
| RF-10 | O bot DEVE citar exemplos em reais (R$) e contextualizados para a realidade jovem | 🔴 Must |
| RF-11 | O bot DEVE terminar respostas com uma pergunta reflexiva ou mini-desafio | 🟡 Should |
| RF-12 | O bot NÃO DEVE recomendar ações, FIIs ou produtos específicos de investimento | 🔴 Must |
| RF-13 | Se não souber responder, o bot DEVE admitir e sugerir fontes confiáveis (Banco Central, ENEF) | 🔴 Must |

**Mapa de Tópicos (50 mínimos):**

| Categoria | Tópicos Básicos | Tópicos Avançados |
|---|---|---|
| 💰 Orçamento Pessoal | Receita x despesa, mesada, controle de gastos | Método 50-30-20, orçamento base zero |
| 🐷 Poupança | Para que poupar, como começar, metas de curto prazo | Fundo de emergência, automatização da poupança |
| 💳 Crédito e Dívida | O que é juro, parcelamento, cartão de crédito | Score de crédito, renegociação, armadilhas do crédito |
| 📈 Investimentos | Poupança x CDB, risco x retorno | Tesouro Direto, fundos, ações (conceito básico) |
| 🛒 Consumo Consciente | Necessidade x desejo, Black Friday, impulso | Marcas x genéricos, impacto ambiental do consumo |
| 🧮 Matemática Financeira | Porcentagem, juros simples, desconto | Juros compostos, inflação, valor do dinheiro no tempo |

---

### 2.3 F3 — Simulador Financeiro

| ID | Requisito | Prioridade |
|---|---|---|
| RF-14 | O comando `/simular` DEVE iniciar o simulador interativo | 🔴 Must |
| RF-15 | O simulador DEVE aceitar quantidade, valor e prazo em linguagem natural ("se eu guardar R$50 por mês por 1 ano") | 🔴 Must |
| RF-16 | O simulador DEVE mostrar três cenários: gastar agora / guardar na poupança / investir no Tesouro Selic | 🔴 Must |
| RF-17 | O simulador DEVE usar taxas reais aproximadas (Selic atual, poupança atual) comunicadas de forma transparente | 🟡 Should |
| RF-18 | O resultado DEVE ser apresentado de forma visual com texto formatado (tabela simples no chat) | 🟡 Should |

---

### 2.4 F4 — Desafios Semanais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-19 | O comando `/desafio` DEVE exibir o desafio da semana para o usuário | 🔴 Must |
| RF-20 | O banco de desafios DEVE conter no mínimo 20 desafios variados | 🔴 Must |
| RF-21 | Desafios DEVEM ter dificuldade categorizada: fácil (50pts) / médio (100pts) / difícil (150pts) | 🟡 Should |
| RF-22 | O usuário DEVE poder marcar um desafio como concluído via InlineKeyboard | 🔴 Must |
| RF-23 | O bot DEVE enviar um lembrete opt-in do desafio durante a semana (uma vez) | 🟢 Could |

**Exemplos de Desafios:**
```
🟢 Fácil: "Anote todos os seus gastos de hoje, por menor que sejam."
🟡 Médio: "Defina 1 meta financeira para os próximos 3 meses e me conta."
🔴 Difícil: "Passe 7 dias sem comprar nada por impulso. Registra tudo que
             você quis comprar mas não comprou."
```

---

### 2.5 F5 — Sistema de Gamificação

| ID | Requisito | Prioridade |
|---|---|---|
| RF-24 | O sistema DEVE atribuir pontos a todas as ações relevantes do usuário | 🔴 Must |
| RF-25 | O sistema DEVE ter 5 níveis com nomes temáticos e thresholds claros | 🔴 Must |
| RF-26 | O bot DEVE notificar o usuário ao subir de nível com mensagem comemorativa | 🔴 Must |
| RF-27 | O comando `/pontos` DEVE exibir pontuação atual, nível e quanto falta para o próximo | 🔴 Must |
| RF-28 | O bot DEVE exibir o nível do usuário em todas as mensagens de progresso | 🟡 Should |

**Tabela de Pontos:**
```
Ação                        │ Pontos
────────────────────────────┼──────────
Completar onboarding        │  +100
Responder quiz corretamente │   +20
Completar desafio fácil     │   +50
Completar desafio médio     │  +100
Completar desafio difícil   │  +150
Definir uma meta financeira │   +30
Streak 7 dias seguidos      │   +80
Convidar amigo (futuro)     │  +200
```

**Níveis:**
```
Nível 1 — 🌱 Aprendiz     (0 pts)
Nível 2 — 📚 Estudante    (200 pts)
Nível 3 — 💡 Consciente   (500 pts)
Nível 4 — 🚀 Investidor   (1.000 pts)
Nível 5 — 🏆 Mestre       (2.000 pts)
```

---

### 2.6 F6 — Metas Financeiras

| ID | Requisito | Prioridade |
|---|---|---|
| RF-29 | O comando `/meta` DEVE permitir criar uma nova meta com título, valor-alvo e prazo | 🔴 Must |
| RF-30 | O bot DEVE armazenar até 5 metas ativas por usuário no MVP | 🟡 Should |
| RF-31 | O usuário DEVE poder atualizar o valor atual de uma meta | 🔴 Must |
| RF-32 | Ao atingir 100% da meta, o bot DEVE enviar mensagem comemorativa e dar +50 pts bônus | 🟡 Should |
| RF-33 | O comando `/metas` DEVE listar todas as metas ativas com barra de progresso em texto | 🔴 Must |

---

### 2.7 F7 — Relatório Mensal

| ID | Requisito | Prioridade |
|---|---|---|
| RF-34 | No 1º dia de cada mês, o bot DEVE enviar ao usuário um resumo do mês anterior | 🟡 Should |
| RF-35 | O relatório DEVE incluir: pontos ganhos, desafios completados, metas atingidas, perguntas feitas e resumo de receitas/despesas do mês | 🟡 Should |
| RF-36 | O usuário DEVE poder opt-out do relatório mensal | 🟡 Should |

---

### 2.8 F8 — Menu de Ajuda

| ID | Requisito | Prioridade |
|---|---|---|
| RF-37 | O comando `/ajuda` DEVE exibir um menu com todos os comandos disponíveis | 🔴 Must |
| RF-38 | O menu DEVE usar InlineKeyboard para facilitar a navegação | 🟡 Should |

**Menu `/ajuda`:**
```
🤖 Fini — Comandos disponíveis:

/start      — Apresentação e onboarding
/simular    — Simulador financeiro
/desafio    — Desafio da semana
/meta       — Criar nova meta
/metas      — Ver suas metas
/gastos     — Registrar ou consultar receitas e gastos
/pontos     — Ver pontuação e nível
/ajuda      — Este menu

💬 Ou é só me mandar uma pergunta sobre finanças!
```

---

### 2.9 F9 — Controle de Receitas e Gastos

| ID | Requisito | Prioridade |
|---|---|---|
| RF-39 | O usuário DEVE poder registrar receitas e despesas por mensagem em linguagem natural | 🔴 Must |
| RF-40 | O bot DEVE identificar automaticamente valor, tipo (receita/despesa), categoria, data e descrição quando possível | 🔴 Must |
| RF-41 | O bot DEVE pedir confirmação antes de salvar um lançamento inferido automaticamente | 🔴 Must |
| RF-42 | O bot DEVE permitir corrigir valor, categoria, data ou descrição antes do salvamento | 🔴 Must |
| RF-43 | O usuário DEVE poder enviar foto de nota fiscal/cupom para extração automática dos dados do gasto | 🟡 Should |
| RF-44 | O bot DEVE descartar a imagem após processar a nota fiscal/cupom, armazenando apenas os dados estruturados do lançamento | 🔴 Must |
| RF-45 | O usuário DEVE poder consultar gastos do mês atual por categoria | 🔴 Must |
| RF-46 | O usuário DEVE poder solicitar um resumo mensal de receitas, despesas, saldo e principais categorias | 🟡 Should |
| RF-47 | O usuário DEVE poder exportar seus lançamentos para uma planilha `.xlsx` | 🟡 Should |

**Exemplos de Registro por Conversa:**
```
"Gastei R$18,50 num lanche hoje"
→ Despesa | R$18,50 | Alimentação | Hoje | Lanche

"Recebi R$200 de mesada"
→ Receita | R$200,00 | Mesada | Hoje | Mesada

"Paguei R$12 no ônibus ontem"
→ Despesa | R$12,00 | Transporte | Ontem | Ônibus
```

**Categorias Iniciais:**
```
Alimentação
Transporte
Educação
Lazer
Compras
Saúde
Moradia
Mesada/Salário
Presente
Outros
```

**Fluxo com Foto de Nota Fiscal/Cupom:**
```
1. Usuário envia uma foto da nota fiscal/cupom
2. Bot extrai valor, data e possíveis itens via OCR
3. Bot infere a categoria do gasto
4. Bot mostra um resumo para confirmação
5. Usuário confirma ou corrige
6. Bot salva apenas os dados estruturados e descarta a imagem
```

---

## 3. Requisitos Não-Funcionais

### 3.1 Performance

| ID | Requisito | Meta |
|---|---|---|
| RNF-01 | Tempo de resposta para perguntas simples (templates) | < 1 segundo |
| RNF-02 | Tempo de resposta para perguntas que envolvem LLM | < 3 segundos (p95) |
| RNF-03 | Tempo de resposta para simulações | < 5 segundos |
| RNF-04 | Disponibilidade em horário escolar (7h–22h BRT) | ≥ 99% uptime |

### 3.2 Escalabilidade

| ID | Requisito | Meta |
|---|---|---|
| RNF-05 | Suportar usuários simultâneos no MVP | 200 usuários |
| RNF-06 | Rate limiting por usuário | 30 mensagens/hora |
| RNF-07 | Graceful degradation quando LLM primário (Groq) estiver indisponível | Fallback para Ollama em < 2s |

### 3.3 Segurança e Privacidade (LGPD)

| ID | Requisito |
|---|---|
| RNF-08 | O sistema NÃO DEVE coletar dados sensíveis (CPF, RG, dados bancários, senha) |
| RNF-09 | O sistema DEVE autenticar webhooks do Telegram via `X-Telegram-Bot-Api-Secret-Token` |
| RNF-10 | Endpoints de admin DEVEM exigir API Key no header |
| RNF-11 | Dados de usuários menores (< 18 anos) DEVEM poder ser deletados sob solicitação |
| RNF-12 | O sistema NÃO DEVE armazenar histórico de mensagens por mais de 90 dias (mensagens antigas purgadas por job semanal) |
| RNF-13 | Toda comunicação DEVE usar HTTPS (TLS 1.3) |

### 3.4 Qualidade e Manutenibilidade

| ID | Requisito |
|---|---|
| RNF-14 | Cobertura de testes unitários ≥ 80% dos módulos críticos (gamificação, LLM gateway, fluxos) |
| RNF-15 | O sistema DEVE logar erros com stack trace em GlitchTip (ou similar) |
| RNF-16 | O código DEVE seguir PEP-8 + Black formatter |
| RNF-17 | CI/CD via GitHub Actions: lint + testes em todo Pull Request |
| RNF-18 | O system prompt da persona Fini DEVE ser versionado em arquivo separado e testável isoladamente |

### 3.5 Acessibilidade e UX

| ID | Requisito |
|---|---|
| RNF-19 | Mensagens do bot DEVEM ser legíveis em mobile (Telegram) sem scroll excessivo |
| RNF-20 | O bot DEVE usar InlineKeyboard para opções de múltipla escolha (evitar digitação) |
| RNF-21 | Mensagens de erro DEVEM ser amigáveis e nunca expor detalhes técnicos internos |
| RNF-22 | O bot DEVE funcionar com Long Polling em ambiente de desenvolvimento (sem necessidade de HTTPS local) |

---

## 4. Restrições

| # | Restrição |
|---|---|
| C1 | O canal DEVE ser Telegram (decisão confirmada) |
| C2 | O custo operacional DEVE ser < R$50/mês no MVP |
| C3 | O LLM DEVE ser open-source (sem modelos proprietários como GPT-4) |
| C4 | O backend DEVE ser em Python (para compatibilidade com bibliotecas de ML para análise futura) |
| C5 | O sistema NÃO DEVE solicitar login ou senha ao usuário (identificação apenas pelo `telegram_id`) |
| C6 | O bot NÃO DEVE armazenar fotos, áudios ou arquivos enviados pelos usuários |

---

## 5. Regras de Negócio

| ID | Regra |
|---|---|
| RN-01 | Um usuário é identificado exclusivamente pelo seu `telegram_id` (chat_id do Telegram) |
| RN-02 | Pontos nunca diminuem — apenas acumulam |
| RN-03 | Um desafio semanal só pode ser marcado como completado uma vez por semana |
| RN-04 | O bot nunca deve recomendar produtos financeiros específicos ("invista no banco X") |
| RN-05 | Usuários < 14 anos devem ver aviso recomendando conversar com pais/responsáveis |
| RN-06 | O contexto de conversa do LLM é limitado às últimas 10 mensagens (janela deslizante) para controlar custo de tokens |
| RN-07 | Se o usuário enviar mais de 30 mensagens/hora, o bot responde com mensagem amigável de pausa |

---

*Fini — Seu Parceiro Financeiro | spec.md v1.0 | 2026-04-04*
