# 📋 spec.md — Especificação de Requisitos
## Fini: Seu Parceiro Financeiro
**Versão:** 2.1 | **Data:** 2026-06-24 | **Revisão de:** spec v2.0

---

## 0. Filosofia de Produto (o que mudou na v2)

A v1 desenhava o Fini como "um bot de Q&A com gamificação que também registra gastos".
A v2 inverte isso: **o Fini é um registrador de gastos que educa pelo reflexo**.

O ciclo educativo central é:

```
REGISTRAR GASTO → VER O PADRÃO → RECEBER INSIGHT → REFLETIR → MUDAR COMPORTAMENTO
```

Todos os outros módulos (Q&A, simulador, desafios, gamificação) existem para
**dar sentido** a esse ciclo — não como fins em si mesmos.

Motivação: o endividamento jovem no Brasil não é causado por falta de informação
sobre juros compostos. É causado pela falta de consciência do próprio padrão de
consumo. Um estudante que registra R$18,50 de lanche, vê que gastou R$180 em
lanches no mês e recebe "você poderia ter pago seu curso de inglês com isso" —
esse estudante aprende mais do que qualquer explicação teórica sobre o método
50-30-20.

---

## 1. Convenções

| Sigla | Significado |
|---|---|
| RF | Requisito Funcional |
| RNF | Requisito Não-Funcional |
| Obrigatório | Obrigatório para o MVP |
| Importante | Importante, mas pode ser diferido |
| Desejável | Desejável se houver tempo |

---

## 2. Requisitos Funcionais

### 2.1 F1 — Onboarding Conversacional

**Propósito pedagógico:** calibrar a linguagem e os exemplos do bot para a
realidade específica do estudante (mesada vs. estágio, mora com pais vs. divide
apartamento, etc.). Coletar, desde o início, a renda mensal esperada — o ponto
de partida de todo planejamento financeiro.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | O bot DEVE detectar se o usuário é novo (sem cadastro no banco) e iniciar o onboarding automaticamente ao primeiro `/start` | Obrigatório |
| RF-02 | O onboarding DEVE coletar: nome, idade e **fonte de renda principal** (mesada / estágio / freelas / trabalho formal / outras) via InlineKeyboard | Obrigatório |
| RF-03 | O onboarding DEVE coletar o valor aproximado de renda mensal via texto livre — com instrução clara de que pode ser fictício | Obrigatório |
| RF-04 | O onboarding DEVE aplicar quiz diagnóstico de 3 perguntas via InlineKeyboard | Obrigatório |
| RF-05 | As respostas do quiz DEVEM categorizar o usuário em perfil: **Iniciante / Em Desenvolvimento / Avançado** — e ajustar o tom das mensagens subsequentes | Obrigatório |
| RF-06 | Ao concluir o onboarding, o bot DEVE: (a) mostrar o perfil diagnosticado, (b) sugerir imediatamente o primeiro registro de gasto como próximo passo, (c) conceder +100 pts | Obrigatório |
| RF-07 | O usuário DEVE poder refazer o onboarding com `/recomecar` (apaga histórico e pontos) | Desejável |

**Quiz diagnóstico (perguntas e lógica de pontuação):**

```
Q1: Quando você recebe sua mesada/salário, o que faz primeiro?
    A) 💸 Gasto logo — o que sobrar eu guardo       → perfil: iniciante
    B) 🏦 Guardo uma parte antes de gastar           → perfil: avançado
    C) 🤷 Depende do mês                             → perfil: em desenvolvimento

Q2: Você já ouviu falar em juros compostos?
    A) ✅ Sim e entendo como funciona                → perfil: avançado
    B) 🤔 Já ouvi, mas não sei direito               → perfil: em desenvolvimento
    C) ❌ Nunca ouvi esse nome                       → perfil: iniciante

Q3: Você tem algum objetivo financeiro agora?
    A) 🎯 Sim, sei exatamente o que quero            → perfil: avançado
    B) 💭 Quero ter, mas não sei como definir        → perfil: em desenvolvimento
    C) 😶 Não pensei nisso ainda                     → perfil: iniciante

Lógica de classificação:
- Maioria A (nas Q1/Q3) + C (Q2) → Iniciante
- Mistura                        → Em Desenvolvimento
- Maioria B (Q1) + A (Q2) + A (Q3) → Avançado
```

**Perfis e impacto no comportamento do bot:**

| Perfil | Tom das respostas | Exemplos usados | Complexidade |
|---|---|---|---|
| Iniciante | Muito simples, encorajador | "tipo assim: se você guardar R$5 por dia..." | Conceitos básicos apenas |
| Em Desenvolvimento | Direto, com contexto | Exemplos com metas concretas | Básico + introdução ao intermediário |
| Avançado | Colega de igual, desafiador | Comparações de rendimento, planejamento por objetivos | Básico + intermediário + avançado |

---

### 2.2 F2 — Motor de Q&A Financeiro

**Propósito pedagógico:** responder dúvidas que surgem naturalmente do uso do
controlador financeiro. Quando o estudante vê "gastei R$120 em assinaturas" no
resumo, ele pode perguntar "isso é muito?" — o Q&A dá o contexto educativo.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-08 | O bot DEVE responder perguntas sobre finanças pessoais em linguagem acessível para jovens | Obrigatório |
| RF-09 | O bot DEVE cobrir no mínimo 50 tópicos em 6 categorias (ver mapa abaixo) | Obrigatório |
| RF-10 | Respostas DEVEM ter no máximo 150 palavras | Obrigatório |
| RF-11 | O bot DEVE usar exemplos contextualizados para a faixa etária (mesada, lanche, streaming, transporte escolar) | Obrigatório |
| RF-12 | O bot DEVE terminar respostas do Q&A com pergunta reflexiva ou mini-desafio conectado ao contexto financeiro atual do usuário | Importante |
| RF-13 | O bot NÃO DEVE recomendar ações, FIIs, criptomoedas ou produtos específicos | Obrigatório |
| RF-14 | Se não souber responder, o bot DEVE admitir e sugerir fontes confiáveis (Banco Central, ENEF, Consumidor.gov.br) | Obrigatório |
| RF-15 | O Q&A DEVE usar o contexto financeiro do usuário para personalizar a resposta quando relevante (ex: "você gastou R$X em lazer esse mês, então...") | Importante |

**Mapa de Tópicos (50 mínimos):**

| Categoria | Tópicos Básicos | Tópicos Avançados |
|---|---|---|
| 💰 Orçamento Pessoal | Receita x despesa, mesada, controle de gastos, diferença entre querer e precisar | Método 50-30-20, orçamento base zero, orçamento por envelope |
| 🐷 Poupança | Para que poupar, como começar, metas de curto prazo, "pagar a si mesmo primeiro" | Fundo de emergência (3–6 meses), automatização, diferença poupança x investimento |
| 💳 Crédito e Dívida | O que é juro, parcelamento, cartão de crédito, crédito rotativo | Score de crédito, renegociação de dívidas, armadilhas do parcelamento sem juros |
| 📈 Investimentos | Poupança x CDB, risco x retorno, o que é rentabilidade | Tesouro Direto, fundos de índice, ações (conceito básico), inflação e poder de compra |
| 🛒 Consumo Consciente | Necessidade x desejo, compra por impulso, Black Friday, comparação de preços | Custo real de uma dívida, marcas x genéricos, impacto ambiental do consumo excessivo |
| 🧮 Matemática Financeira | Porcentagem, juros simples, desconto, regra de três | Juros compostos, inflação, valor do dinheiro no tempo, taxa mensal x anual |

---

### 2.3 F3 — Simulador Financeiro

**Propósito pedagógico:** mostrar concretamente o custo de oportunidade de cada
escolha de consumo. "Se eu não comprar esse tênis agora e guardar R$300 por 6
meses, o que eu consigo?" é mais poderoso do que qualquer explicação teórica.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-16 | O comando `/simular` DEVE iniciar o simulador interativo | Obrigatório |
| RF-17 | O simulador DEVE aceitar parâmetros em linguagem natural ("se eu guardar R$50 por mês por 1 ano") | Obrigatório |
| RF-18 | O simulador DEVE mostrar três cenários comparativos: **gastar agora** / **guardar na poupança** / **investir no Tesouro Selic** | Obrigatório |
| RF-19 | O simulador DEVE usar taxas reais aproximadas (Selic atual, poupança atual) com nota de transparência sobre a fonte e data | Importante |
| RF-20 | O resultado DEVE ser apresentado como tabela de texto formatada no Telegram (sem imagem) | Importante |
| RF-21 | O simulador DEVE conectar o resultado com uma meta ativa do usuário, se houver ("isso pagaria X% da sua meta 'Celular novo'") | Importante |

**Formato de saída esperado do simulador:**

```
💡 Simulando: R$50/mês por 12 meses

Opção           │ Após 12 meses
────────────────┼──────────────
💸 Gastar agora │ R$ 0,00
🏦 Poupança     │ R$ 613,40 (+2,2%)
📈 Tesouro Selic│ R$ 631,20 (+5,2%)

👉 Isso equivale a 3 meses de vale-transporte
ou quase 100% da sua meta "Curso de inglês" 🎯
```

---

### 2.4 F4 — Desafios Semanais

**Propósito pedagógico:** criar hábitos por meio de ação prática semanal, não
apenas leitura passiva. O desafio mais efetivo é aquele que faz o estudante
observar o próprio comportamento.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-22 | O comando `/desafio` DEVE exibir o desafio da semana atual | Obrigatório |
| RF-23 | O banco de desafios DEVE conter no mínimo 20 desafios variados | Obrigatório |
| RF-24 | Desafios DEVEM ter dificuldade categorizada: fácil (50pts) / médio (100pts) / difícil (150pts) | Importante |
| RF-25 | O usuário DEVE poder marcar um desafio como concluído via InlineKeyboard | Obrigatório |
| RF-26 | Desafios DEVEM estar conectados ao módulo de controle financeiro sempre que possível (ex: "registre todos os gastos de hoje") | Obrigatório |
| RF-27 | O bot DEVE enviar lembrete opt-in do desafio (uma vez por semana via scheduled job) | Desejável |

**Banco de desafios mínimo (20 desafios):**

```
🟢 FÁCEIS (50 pts) — foco em observação e registro:
D01: Anote todos os gastos de hoje, por menor que sejam. Qual foi o maior?
D02: Olhe o resumo do mês e identifique a categoria onde você mais gastou.
D03: Registre todos os lançamentos dos últimos 3 dias (pode reconstruir da memória).
D04: Encontre 1 gasto do mês que, pensando agora, você não faria de novo.
D05: Envie /resumo e me diga: seu saldo ficou positivo ou negativo? Por quê?

🟡 MÉDIOS (100 pts) — foco em planejamento e reflexão:
D06: Defina 1 meta financeira para os próximos 3 meses usando /meta.
D07: Passe uma semana registrando TODOS os gastos com alimentação fora de casa.
D08: Identifique uma assinatura que você paga mas usa pouco. Vale manter?
D09: Calcule: quanto você gasta por mês em transporte? É proporcional à sua renda?
D10: Liste 3 gastos recorrentes seus. Qual deles você poderia reduzir sem perder qualidade de vida?
D11: Compare seus gastos de lazer dos últimos 2 meses. Aumentou ou diminuiu? Por quê?
D12: Use /simular para descobrir quanto teria ao final de 6 meses guardando 10% da sua renda.

🔴 DIFÍCEIS (150 pts) — foco em mudança de comportamento:
D13: Passe 7 dias sem comprar nada por impulso. Registre tudo que quis mas não comprou.
D14: Durante 1 semana, antes de qualquer compra acima de R$30, espere 24h e só compre se ainda quiser.
D15: Crie um plano de economia para os próximos 2 meses com meta, valor mensal e o que pretende cortar.
D16: Pesquise o preço de algo que quer comprar em 3 lugares diferentes antes de decidir.
D17: Calcule quanto você gastou com algo que "só ia custar R$X" mas acabou saindo mais caro.
D18: Encontre uma forma de gerar renda extra (mesmo que pequena) esse mês. Registre quando chegar.
D19: Converta seu maior gasto do mês para horas de trabalho: "quantas horas eu trabalhei pra pagar isso?"
D20: Feche o mês com saldo positivo. Use /resumo para acompanhar ao longo do mês.
```

---

### 2.5 F5 — Sistema de Gamificação

**Propósito pedagógico:** gamificação a serviço do hábito de registro, não de
métricas de engajamento vazias. A tabela de pontos prioriza explicitamente as
ações ligadas ao controle financeiro, que é o coração do produto.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-28 | O sistema DEVE atribuir pontos a todas as ações relevantes do usuário | Obrigatório |
| RF-29 | O sistema DEVE ter 5 níveis com nomes temáticos e thresholds claros | Obrigatório |
| RF-30 | O bot DEVE notificar o usuário ao subir de nível com mensagem comemorativa e sugestão do que fazer em seguida | Obrigatório |
| RF-31 | O comando `/pontos` DEVE exibir: pontuação atual, nível, quanto falta para o próximo e um resumo das últimas ações pontuadas | Obrigatório |
| RF-32 | O bot DEVE exibir o nível do usuário em todas as mensagens de progresso | Importante |
| RF-33 | O sistema de pontos DEVE dar peso maior a ações de registro financeiro do que a perguntas ao Q&A | Obrigatório |

**Tabela de pontos revisada (F9 tem a maior densidade de pontos):**

```
Ação                                    │ Pontos │ Módulo
────────────────────────────────────────┼────────┼──────────
Completar onboarding                    │  +100  │ F1
Responder quiz diagnóstico              │   +20  │ F1
── REGISTRO FINANCEIRO (F9) ────────────┼────────┼──────────
Registrar primeiro gasto do dia         │   +10  │ F9
Registrar receita                       │   +10  │ F9
Fechar mês com saldo positivo           │   +80  │ F9
7 dias com registro (constância)        │   +80  │ F9 constância
15 dias com registro (constância)       │  +120  │ F9 constância
30 dias com registro (constância)       │  +180  │ F9 constância
60 dias com registro (constância)       │  +250  │ F9 constância
Exportar planilha /planilha             │   +20  │ F9
── METAS (F6) ──────────────────────────┼────────┼──────────
Criar uma meta financeira               │   +30  │ F6
Atualizar progresso de uma meta         │   +15  │ F6
Atingir 100% de uma meta                │   +80  │ F6
── DESAFIOS (F4) ───────────────────────┼────────┼──────────
Completar desafio fácil                 │   +50  │ F4
Completar desafio médio                 │  +100  │ F4
Completar desafio difícil               │  +150  │ F4
── Q&A / SIMULADOR ─────────────────────┼────────┼──────────
Usar /simular pela primeira vez         │   +20  │ F3
Fazer pergunta ao Q&A (1x/dia máx)     │   +5   │ F2
```

**Níveis e desbloqueios:**

```
Nível 1 — 🌱 Aprendiz     (0 pts)
  → Acesso: todos os comandos básicos

Nível 2 — 📚 Estudante    (200 pts)
  → Desbloqueio: simulador avançado (multi-cenário)
  → Mensagem: "Você começou a entender o jogo. Agora vamos ver quanto você pode acumular."

Nível 3 — 💡 Consciente   (500 pts)
  → Desbloqueio: desafios difíceis (150 pts)
  → Mensagem: "Você já tem consciência dos seus gastos. Isso é mais raro do que parece."

Nível 4 — 🚀 Investidor   (1.000 pts)
  → Desbloqueio: relatório detalhado com análise de tendência (F7 completo)
  → Mensagem: "Você pensa antes de gastar. Isso te coloca na frente da maioria."

Nível 5 — 🏆 Mestre       (2.000 pts)
  → Badge especial exibido em todo resumo
  → Mensagem: "Você dominou o básico que 90% das pessoas nunca aprendem. Ensina alguém?"
```

---

### 2.6 F6 — Metas Financeiras

**Propósito pedagógico:** conectar o sacrifício presente (deixar de gastar) a
um objetivo futuro concreto e desejado pelo próprio estudante. "Guardar dinheiro"
é abstrato; "juntar R$800 pro fone até outubro" é motivador.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-34 | O comando `/meta` DEVE iniciar fluxo conversacional para criar meta com: título, valor-alvo e prazo | Obrigatório |
| RF-35 | O bot DEVE calcular e mostrar automaticamente: valor mensal necessário para atingir a meta no prazo | Obrigatório |
| RF-36 | O bot DEVE alertar se o valor mensal necessário for maior que a renda informada no onboarding | Obrigatório |
| RF-37 | O usuário DEVE poder atualizar o valor atual de uma meta com `/meta atualizar` ou frase em linguagem natural | Obrigatório |
| RF-38 | O bot DEVE armazenar até 5 metas ativas por usuário no MVP | Importante |
| RF-39 | Ao atingir 100%, o bot DEVE enviar mensagem comemorativa personalizada + +80 pts | Importante |
| RF-40 | O comando `/metas` DEVE listar todas as metas ativas com barra de progresso em texto ASCII e dias restantes | Obrigatório |
| RF-41 | O simulador (F3) DEVE referenciar as metas ativas ao exibir resultados | Importante |

**Formato de exibição de metas (`/metas`):**

```
🎯 Suas metas ativas:

1. 📱 Celular novo
   Meta: R$1.200 | Guardado: R$480 (40%)
   [████████░░░░░░░░░░░░] 40%
   Prazo: 4 meses | Precisa guardar: R$180/mês

2. 🎓 Curso de inglês
   Meta: R$600 | Guardado: R$150 (25%)
   [█████░░░░░░░░░░░░░░░] 25%
   Prazo: 3 meses | Precisa guardar: R$150/mês
```

---

### 2.7 F7 — Relatório Mensal

**Propósito pedagógico:** fechamento de ciclo. O estudante vê, em uma mensagem,
o impacto de todos os seus registros e hábitos do mês — esse é o momento de
maior insight e de maior motivação para o próximo mês.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-42 | No 1º dia de cada mês, o bot DEVE enviar ao usuário um resumo do mês anterior (via scheduled job) | Importante |
| RF-43 | O relatório DEVE incluir: total de receitas, total de despesas, saldo, breakdown por categoria, pontos ganhos, desafios completados, metas ativas e evolução de nível | Importante |
| RF-44 | O relatório DEVE incluir um **insight educativo contextualizado**: a categoria com maior gasto recebe um comentário específico (ex: "Você gastou R$X em lazer — isso é Y% da sua renda. A recomendação do método 50-30-20 é no máximo 30%.") | Obrigatório |
| RF-45 | O relatório DEVE incluir a planilha `.xlsx` como anexo | Importante |
| RF-46 | O usuário DEVE poder opt-out do relatório mensal com `/silenciar relatorio` | Importante |
| RF-47 | O usuário DEVE poder solicitar o relatório do mês atual a qualquer hora com `/resumo mes` | Obrigatório |

---

### 2.8 F8 — Menu de Ajuda

| ID | Requisito | Prioridade |
|---|---|---|
| RF-48 | O comando `/ajuda` DEVE exibir menu com todos os comandos, organizados por contexto de uso | Obrigatório |
| RF-49 | O menu DEVE usar InlineKeyboard para navegação entre categorias | Importante |

**Menu `/ajuda` revisado (organizado por fluxo de uso, não por feature):**

```
🤖 Fini — O que você quer fazer?

📊 CONTROLAR MEUS GASTOS
  /gasto     → Registrar um gasto (ex: /gasto 18.50 lanche)
  /receita   → Registrar uma entrada (ex: /receita 300 mesada)
  /resumo    → Ver totais e categorias do mês
  /planilha  → Baixar sua planilha .xlsx

🎯 MINHAS METAS
  /meta      → Criar nova meta
  /metas     → Ver todas as metas ativas

🎮 APRENDER E EVOLUIR
  /simular   → Simular quanto rende guardar dinheiro
  /desafio   → Ver desafio da semana
  /aprender  → Trilha rápida de educação financeira
  /pontos    → Ver sua pontuação e nível

⚙️ CONFIGURAÇÕES
  /start     → Reiniciar apresentação
  /ajuda     → Este menu

💬 Ou só me faz uma pergunta sobre finanças!
```

---

### 2.9 F9 — Controle de Receitas e Gastos ⭐ (módulo central)

**Este é o módulo mais importante do produto.** Todo o resto do sistema
(gamificação, desafios, Q&A, relatórios) existe para dar suporte a este ciclo.

**Propósito pedagógico:** criar o hábito de registro e, por consequência, a
consciência do padrão de consumo. A maior transformação acontece no momento em
que o estudante vê o próprio dado organizado — não quando recebe uma explicação.

#### 2.9.1 Registro por linguagem natural

| ID | Requisito | Prioridade |
|---|---|---|
| RF-50 | O usuário DEVE poder registrar receitas e despesas por mensagem em linguagem natural sem comandos | Obrigatório |
| RF-51 | O bot DEVE identificar automaticamente: valor, tipo (receita/despesa), categoria, data e descrição | Obrigatório |
| RF-52 | O bot DEVE pedir confirmação antes de salvar um lançamento com InlineKeyboard (Confirmar / Corrigir / Cancelar) | Obrigatório |
| RF-53 | O usuário DEVE poder corrigir valor, categoria, data ou descrição antes de confirmar | Obrigatório |
| RF-54 | Após confirmar o lançamento, o bot DEVE exibir o saldo do mês atualizado e um insight rápido quando relevante | Obrigatório |
| RF-55 | O bot DEVE reconhecer expressões de tempo relativas: "hoje", "ontem", "segunda-feira", "semana passada" | Obrigatório |

**Exemplos de parsing esperado:**

```
Input: "Gastei R$18,50 num lanche hoje"
Parse: tipo=despesa | valor=18.50 | categoria=Alimentação | data=hoje | desc="Lanche"

Input: "Recebi R$200 de mesada"
Parse: tipo=receita | valor=200.00 | categoria=Mesada | data=hoje | desc="Mesada"

Input: "Paguei R$12 no ônibus ontem"
Parse: tipo=despesa | valor=12.00 | categoria=Transporte | data=ontem | desc="Ônibus"

Input: "Netflix R$37 mês passado"
Parse: tipo=despesa | valor=37.00 | categoria=Streaming | data=1º do mês passado | desc="Netflix"

Input: "freela de R$150 na semana passada"
Parse: tipo=receita | valor=150.00 | categoria=Freelas | data=segunda da semana passada | desc="Freela"

Input: "Recebi meu salário hoje, R$1.200"
Parse: tipo=receita | valor=1200.00 | categoria=Salário | data=hoje | desc="Salário"
```

**Fluxo completo de confirmação:**

```
Usuário: "Gastei 18,50 num lanche"

Bot: 📝 Confirmando lançamento:
     💸 Despesa • R$18,50 • Alimentação
     📅 Hoje, 23/05/2026
     📌 Lanche

     [✅ Confirmar] [✏️ Corrigir] [❌ Cancelar]

Usuário: [clica Confirmar]

Bot: ✅ Anotado! +10 pts 🌱 Aprendiz

     📊 Maio até agora:
     Receitas: R$300,00
     Gastos:   R$127,30
     Saldo:    R$172,70 ✅

     💡 Você gastou R$42,50 em alimentação esse mês.
     Isso é 14% da sua renda.
```

#### 2.9.2 Categorias de despesas e receitas

```
DESPESAS (16 categorias):
  Alimentação        → lanche, restaurante, delivery, mercado, padaria
  Transporte         → ônibus, metrô, Uber, táxi, combustível, bilhete, passagem
  Streaming          → Netflix, Spotify, Amazon Prime, Disney, YouTube Premium, iCloud
  Cinema e Shows     → cinema, show, teatro, ingresso de filme
  Rolês e Encontros  → passeio, rolê, encontro, date, festa, balada, shopping
  Games              → game, jogo, Steam, PSN, Xbox
  Vestuário          → roupa, tênis, camiseta, look, vestido, boné
  Beleza             → cabelo, corte, unha, maquiagem, perfume, salão
  Educação           → escola, faculdade, curso, livro (estudo), material, apostila
  Saúde              → remédio, consulta, dentista, hospital, farmácia
  Compras            → celular, notebook, eletrônico, fone, acessório
  Viagem             → viagem, hotel, passagem de viagem
  Presentes          → presentes para outras pessoas
  Moradia            → aluguel, energia, água, internet de casa
  Lazer              → qualquer lazer não coberto pelas categorias acima
  Outros             → qualquer coisa não categorizada

RECEITAS (7 categorias):
  Mesada         → valor fixo recebido dos pais/responsáveis
  Salário        → pagamento mensal formal (CLT, autônomo registrado)
  Estágio        → remuneração de estágio ou jovem aprendiz
  Freelas        → trabalhos avulsos, bicos, serviços pontuais
  Presentes      → dinheiro recebido de presente
  Bolsa/Auxílio  → bolsa de estudos, auxílio governamental ou institucional
  Outros         → qualquer outra entrada
```

#### 2.9.3 Resumo mensal (`/resumo`)

| ID | Requisito | Prioridade |
|---|---|---|
| RF-56 | O comando `/resumo` DEVE exibir: total de receitas, total de despesas, saldo, e breakdown por categoria (valor + % da renda) | Obrigatório |
| RF-57 | O resumo DEVE destacar visualmente a categoria com maior gasto | Obrigatório |
| RF-58 | O resumo DEVE incluir comparação com o mês anterior quando houver dados | Importante |
| RF-59 | O resumo DEVE incluir um insight do Fini contextualizado com os dados reais do usuário | Obrigatório |
| RF-60 | O resumo DEVE mostrar o progresso das metas ativas | Importante |

**Formato esperado do `/resumo`:**

```
📊 Resumo de Maio/2026 — João 🌱 Aprendiz

💚 RECEITAS: R$300,00
  Mesada............. R$300,00

❤️ GASTOS: R$247,30 (82% da renda)
  🍔 Alimentação..... R$89,00  (30%) ← MAIOR GASTO
  🚌 Transporte...... R$68,00  (23%)
  📱 Streaming....... R$37,00  (12%)
  🛍️ Compras......... R$31,30  (10%)
  🎮 Lazer........... R$22,00  ( 7%)

💰 SALDO: R$52,70 ✅ positivo

📈 vs. mês anterior: gastos ↓ R$18,20 (melhorou!)

💡 Fini diz:
  Alimentação foi seu maior gasto — R$89 em 18 dias.
  Faltam 13 dias no mês. Se mantiver esse ritmo, vai
  gastar ~R$148 em alimentação no total.
  O método 50-30-20 sugere no máximo R$90 nessa categoria.
  Tá perto! Vale ficar de olho 👀

🎯 Metas: Celular (40%) | Inglês (25%)
```

#### 2.9.4 Exportação de planilha (`.xlsx`)

| ID | Requisito | Prioridade |
|---|---|---|
| RF-61 | O comando `/planilha` DEVE gerar e enviar arquivo `.xlsx` diretamente no chat do Telegram | Obrigatório |
| RF-62 | A planilha DEVE conter duas abas: **Lançamentos** e **Resumo** | Obrigatório |
| RF-63 | A aba Lançamentos DEVE ter colunas: Data, Tipo, Categoria, Descrição, Valor | Obrigatório |
| RF-64 | A aba Resumo DEVE ter: total de receitas, total de despesas, saldo, tabela de gastos por categoria com valor e % e gráfico de barras (se suportado pelo openpyxl) | Obrigatório |
| RF-65 | A planilha DEVE ter cabeçalhos com visual jovem: cores verde (receita) / vermelho (despesa) / azul (neutro), fonte Arial 11 | Importante |
| RF-66 | A planilha DEVE ter filtros automáticos na aba Lançamentos | Importante |
| RF-67 | O bot DEVE descartar o arquivo `.xlsx` do servidor após o envio — armazena apenas os dados estruturados no banco | Obrigatório |
| RF-68 | O usuário DEVE receber +20 pts ao exportar a planilha pela primeira vez no mês | Importante |

**Estrutura detalhada da planilha exportada:**

```
ABA 1 — Lançamentos
┌────────────┬──────────┬───────────────┬──────────────┬──────────┐
│ Data       │ Tipo     │ Categoria     │ Descrição    │ Valor    │
├────────────┼──────────┼───────────────┼──────────────┼──────────┤
│ 01/05/2026 │ Receita  │ Mesada        │ Mesada maio  │ R$300,00 │
│ 02/05/2026 │ Despesa  │ Alimentação   │ Lanche       │ R$18,50  │
│ 03/05/2026 │ Despesa  │ Transporte    │ Ônibus       │ R$12,00  │
│ ...        │ ...      │ ...           │ ...          │ ...      │
└────────────┴──────────┴───────────────┴──────────────┴──────────┘
Linha de rodapé com total (fórmula Excel)

ABA 2 — Resumo (mês/ano do relatório)
┌──────────────────────────────┬──────────────┬──────────┐
│ Indicador                    │ Valor        │ % Renda  │
├──────────────────────────────┼──────────────┼──────────┤
│ Total de Receitas            │ R$300,00     │ 100%     │
│ Total de Despesas            │ R$247,30     │  82%     │
│ Saldo do Mês                 │ R$52,70      │  18%     │
├──────────────────────────────┼──────────────┼──────────┤
│ DESPESAS POR CATEGORIA       │              │          │
│ Alimentação                  │ R$89,00      │  30%     │
│ Transporte                   │ R$68,00      │  23%     │
│ Streaming                     │ R$37,00      │  12%     │
│ Compras                      │ R$31,30      │  10%     │
│ Lazer                        │ R$22,00      │   7%     │
└──────────────────────────────┴──────────────┴──────────┘
+ Gráfico de barras horizontais com categorias de despesa
```

#### 2.9.5 Foto de nota fiscal / cupom fiscal

| ID | Requisito | Prioridade |
|---|---|---|
| RF-69 | O usuário DEVE poder enviar foto de nota fiscal ou cupom para extração automática via visão do LLM | Importante |
| RF-70 | O bot DEVE inferir valor total, estabelecimento e data da nota | Importante |
| RF-71 | O bot DEVE seguir o mesmo fluxo de confirmação (RF-52) após extrair os dados | Obrigatório |
| RF-72 | O bot DEVE descartar a imagem imediatamente após o processamento — nunca armazenar a foto | Obrigatório |

---

### 2.10 F10 — Módulo Aprender BNCC (Fase 9 de implementação)

**Propósito pedagógico:** oferecer uma trilha curta de educação financeira
alinhada à BNCC, conectando conceitos matemáticos e tomada de decisão ao uso
real do controle financeiro do estudante. O módulo não substitui o Q&A: ele
organiza conteúdos essenciais em cards, quizzes rápidos e mini-desafios.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-73 | O comando `/aprender` DEVE abrir um menu de tópicos educativos de educação financeira | Obrigatório |
| RF-74 | O módulo DEVE conter, no MVP, os tópicos: receita/despesa, saldo, porcentagem, juros simples, juros compostos, metas, planejamento, consumo consciente e bets/apostas | Obrigatório |
| RF-75 | Cada tópico DEVE exibir um card curto com conceito, exemplo em reais, quiz e mini-desafio prático | Obrigatório |
| RF-76 | Os quizzes DEVEM usar InlineKeyboard e retornar feedback imediato para resposta certa ou errada | Obrigatório |
| RF-77 | Os mini-desafios DEVEM conectar o aprendizado aos comandos do bot quando possível (`/gasto`, `/receita`, `/resumo`, `/meta`, `/simular`) | Importante |
| RF-78 | O conteúdo DEVE usar dados reais do mês quando disponíveis, especialmente em saldo, porcentagem e planejamento | Importante |
| RF-79 | O tópico bets/apostas DEVE deixar claro que apostas **não são um caminho financeiro saudável**, especialmente para jovens; NÃO deve ensinar "regras para apostar com segurança"; em caso de sinais de dependência, DEVE indicar busca de ajuda em UBS ou CAPS (atendimento gratuito e sigiloso) | Obrigatório |
| RF-80 | A interação com o módulo Aprender DEVE pontuar ações educativas: visualizar tópico, acertar quiz e aceitar mini-desafio | Importante |

**Tópicos iniciais:**

```
L01 Receita e despesa
L02 Saldo
L03 Porcentagem
L04 Juros simples
L05 Juros compostos
L06 Metas financeiras
L07 Planejamento mensal
L08 Consumo consciente
L09 Bets e apostas
```

**Alinhamento pedagógico BNCC:**

- Operações com números racionais, porcentagens, acréscimos e comparação de cenários.
- Organização e interpretação de dados financeiros pessoais.
- Planejamento, projeto de vida, tomada de decisão e consumo consciente.
- Apostas/bets como tema de proteção financeira e saúde: plataformas projetadas para que o usuário perca; encaminhamento para UBS/CAPS em caso de dependência.

---

## 3. Requisitos Não-Funcionais

### 3.1 Performance

| ID | Requisito | Meta |
|---|---|---|
| RNF-01 | Tempo de resposta — registro de gasto (sem LLM) | < 1 segundo |
| RNF-02 | Tempo de resposta — Q&A com LLM | < 3 segundos (p95) |
| RNF-03 | Tempo de geração da planilha `.xlsx` | < 5 segundos |
| RNF-04 | Disponibilidade em horário escolar (7h–22h BRT) | ≥ 99% uptime |

### 3.2 Escalabilidade

| ID | Requisito | Meta |
|---|---|---|
| RNF-05 | Usuários simultâneos no MVP | 200 usuários |
| RNF-06 | Rate limiting por usuário | 30 mensagens/hora |
| RNF-07 | Fallback automático quando Groq estiver indisponível | Ollama em < 2s |

### 3.3 Segurança e Privacidade (LGPD)

| ID | Requisito |
|---|---|
| RNF-08 | O sistema NÃO DEVE coletar: CPF, RG, dados bancários, senhas, extratos |
| RNF-09 | O sistema DEVE autenticar webhooks do Telegram via `X-Telegram-Bot-Api-Secret-Token` |
| RNF-10 | Endpoints de admin DEVEM exigir API Key no header |
| RNF-11 | Dados de usuários menores (< 18 anos) DEVEM poder ser deletados sob solicitação em < 48h |
| RNF-12 | O sistema NÃO DEVE armazenar histórico de mensagens por mais de 90 dias (job semanal de purge) |
| RNF-13 | Toda comunicação DEVE usar HTTPS (TLS 1.3) |
| RNF-14 | Fotos de notas fiscais DEVEM ser descartadas após processamento — nunca persistidas em disco ou banco |

### 3.4 Qualidade e Manutenibilidade

| ID | Requisito |
|---|---|
| RNF-15 | Cobertura de testes unitários ≥ 80% dos módulos críticos (gamificação, parser F9, geração de planilha, fluxos) |
| RNF-16 | Logging de erros com stack trace (GlitchTip ou equivalente) |
| RNF-17 | Código Python seguindo PEP-8 + Black formatter |
| RNF-18 | CI/CD via GitHub Actions: lint + testes em todo Pull Request |
| RNF-19 | System prompt da persona Fini versionado em arquivo separado e testável isoladamente |
| RNF-20 | O parser de linguagem natural (RF-51) DEVE ter testes unitários com pelo menos 30 casos de entrada |

### 3.5 Acessibilidade e UX

| ID | Requisito |
|---|---|
| RNF-21 | Mensagens DEVEM ser legíveis em mobile sem scroll excessivo (máx. ~20 linhas por mensagem) |
| RNF-22 | O bot DEVE usar InlineKeyboard para toda escolha múltipla (evitar digitação manual de opções) |
| RNF-23 | Mensagens de erro DEVEM ser amigáveis e nunca expor detalhes técnicos |
| RNF-24 | O bot DEVE funcionar com Long Polling em ambiente de desenvolvimento |
| RNF-25 | O formato de valores monetários DEVE ser sempre "R$X,XX" — sem ambiguidade |

---

## 4. Restrições

| # | Restrição |
|---|---|
| C1 | Canal: Telegram (confirmado) |
| C2 | Custo operacional < R$50/mês no MVP |
| C3 | LLM open-source (sem modelos proprietários pagos) |
| C4 | Backend em Python 3.12 |
| C5 | Identificação apenas pelo `telegram_id` — sem login/senha |
| C6 | Fotos, áudios e arquivos NÃO são armazenados |

---

## 5. Regras de Negócio

| ID | Regra |
|---|---|
| RN-01 | Usuário identificado exclusivamente pelo `telegram_id` |
| RN-02 | Pontos nunca diminuem — apenas acumulam |
| RN-03 | Constância: contador de dias com registro no mês corrente e contador de total acumulado desde o início do uso. Nenhum dos dois diminui por inatividade — a virada de mês reinicia apenas a contagem mensal. Marcos cumulativos (7, 15, 30 e 60 dias) são concedidos uma única vez e não são perdidos |
| RN-04 | Um desafio semanal só pode ser marcado como completado uma vez por semana |
| RN-05 | O bot nunca recomenda produtos financeiros específicos |
| RN-06 | Usuários < 14 anos recebem aviso recomendando conversar com pais/responsáveis |
| RN-07 | Contexto LLM limitado às últimas 10 mensagens (janela deslizante) |
| RN-08 | Mensagens > 30/hora recebem resposta amigável de pausa |
| RN-09 | Registros financeiros ficam disponíveis por no mínimo 12 meses antes de purge |
| RN-10 | A renda mensal informada no onboarding é usada como referência para % nos resumos — não como dado bancário |
| RN-11 | Se o usuário não informar a data de um lançamento, assume-se a data atual |
| RN-12 | Valores negativos não são aceitos — bot pede correção |
| RN-13 | Lançamentos podem ser editados dentro de 24h da criação; após isso, apenas exclusão |

---

## 6. Prioridade de Implementação (ordem sugerida para MVP)

```
Sprint 1 (base):
  ✅ F1 — Onboarding com coleta de renda
  ✅ F9.1 — Registro de gastos e receitas (parsing + confirmação)
  ✅ F9.3 — Resumo mensal (/resumo)

Sprint 2 (loop completo):
  ✅ F9.4 — Exportação /planilha .xlsx
  ✅ F5 — Gamificação (pontos + níveis)
  ✅ F6 — Metas financeiras

Sprint 3 (enriquecimento):
  ✅ F2 — Q&A financeiro
  ✅ F4 — Desafios semanais
  ✅ F3 — Simulador financeiro

Sprint 4 (fechamento):
  ✅ F7 — Relatório mensal automático
  ✅ F8 — Menu de ajuda completo
  ✅ F9.5 — Foto de nota fiscal (Should)
```

---

*Fini — Seu Parceiro Financeiro | spec.md v2.1 | 2026-06-24*
*Revisão de: spec v2.0 (2026-05-23)*
