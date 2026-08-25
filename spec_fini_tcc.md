# Especificação de Requisitos — Fini: Seu Parceiro Financeiro
**Versão:** 2.1 | **Data:** 24/06/2026

---

## 1. Visão Geral

O Fini é um chatbot educacional de finanças pessoais voltado a jovens estudantes (13–21 anos), distribuído via Telegram. Seu objetivo central é criar o hábito de registro financeiro diário e, a partir dos próprios dados do estudante, gerar consciência sobre o padrão de consumo. O ciclo educativo que orienta o produto é:

**Registrar → Ver o padrão → Receber insight → Refletir → Mudar comportamento**

Todos os módulos secundários (perguntas e respostas, simulador, desafios, gamificação) existem para dar sentido a esse ciclo, não como fins em si mesmos.

---

## 2. Convenções

| Sigla | Significado |
|---|---|
| RF | Requisito Funcional |
| RNF | Requisito Não-Funcional |
| Obrigatório | Indispensável para o MVP |
| Importante | Relevante, pode ser diferido |
| Desejável | Bom ter, se houver tempo |

---

## 3. Requisitos Funcionais

### F1 — Onboarding Conversacional

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | O bot deve detectar usuário novo e iniciar onboarding automaticamente no primeiro `/start` | Obrigatório |
| RF-02 | O onboarding deve coletar nome, idade e fonte de renda principal (mesada, estágio, freelas, trabalho formal ou outras) via menu de opções | Obrigatório |
| RF-03 | O onboarding deve coletar o valor aproximado de renda mensal | Obrigatório |
| RF-04 | O onboarding deve aplicar quiz diagnóstico de 3 perguntas para classificar o perfil do estudante | Obrigatório |
| RF-05 | O perfil resultante (Iniciante, Em Desenvolvimento ou Avançado) deve ajustar o tom e a complexidade das respostas do bot | Obrigatório |
| RF-06 | Ao concluir o onboarding, o bot deve exibir o perfil diagnosticado, sugerir o primeiro registro de gasto e conceder 100 pontos | Obrigatório |

### F2 — Motor de Perguntas e Respostas Financeiro

| ID | Requisito | Prioridade |
|---|---|---|
| RF-07 | O bot deve responder perguntas sobre finanças pessoais em linguagem acessível para jovens | Obrigatório |
| RF-08 | As respostas devem ter no máximo 150 palavras e usar exemplos compatíveis com a realidade do estudante | Obrigatório |
| RF-09 | O bot não deve recomendar produtos financeiros específicos (ações, bancos, corretoras) | Obrigatório |
| RF-10 | Quando não souber responder, o bot deve indicar fontes confiáveis: Banco Central, ENEF, Consumidor.gov.br | Obrigatório |
| RF-11 | O bot deve personalizar a resposta usando os dados financeiros do mês do usuário quando relevante | Importante |

### F3 — Simulador Financeiro

| ID | Requisito | Prioridade |
|---|---|---|
| RF-12 | O comando `/simular` deve aceitar parâmetros em linguagem natural e iniciar o simulador | Obrigatório |
| RF-13 | O simulador deve apresentar três cenários comparativos: gastar agora, guardar na poupança e investir no Tesouro Selic | Obrigatório |
| RF-14 | O resultado deve referenciar metas ativas do usuário quando houver | Importante |

### F4 — Desafios Semanais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-15 | O comando `/desafio` deve exibir o desafio da semana atual | Obrigatório |
| RF-16 | O banco de desafios deve conter no mínimo 20 desafios em três níveis: fácil (50 pts), médio (100 pts) e difícil (150 pts) | Obrigatório |
| RF-17 | O usuário deve poder marcar o desafio como concluído por menu de opções | Obrigatório |
| RF-18 | Os desafios devem estar conectados ao módulo de controle financeiro sempre que possível | Obrigatório |

### F5 — Sistema de Gamificação

| ID | Requisito | Prioridade |
|---|---|---|
| RF-19 | O sistema deve atribuir pontos a todas as ações relevantes do usuário, com peso maior para ações de registro financeiro | Obrigatório |
| RF-20 | O sistema deve ter 5 níveis: Aprendiz (0 pts), Estudante (200 pts), Consciente (500 pts), Investidor (1.000 pts) e Mestre (2.000 pts) | Obrigatório |
| RF-21 | O bot deve notificar o usuário ao subir de nível com mensagem comemorativa | Obrigatório |
| RF-22 | O comando `/pontos` deve exibir pontuação atual, nível e quanto falta para o próximo | Obrigatório |

### F6 — Metas Financeiras

| ID | Requisito | Prioridade |
|---|---|---|
| RF-23 | O comando `/meta` deve iniciar fluxo para criar meta com título, valor-alvo e prazo | Obrigatório |
| RF-24 | O bot deve calcular e exibir automaticamente o valor mensal necessário para atingir a meta no prazo | Obrigatório |
| RF-25 | O bot deve alertar se o valor mensal necessário for superior à renda informada no onboarding | Obrigatório |
| RF-26 | O comando `/metas` deve listar todas as metas ativas com percentual de progresso e dias restantes | Obrigatório |
| RF-27 | Ao atingir 100%, o bot deve enviar mensagem comemorativa e conceder 80 pontos | Importante |

### F7 — Relatório Mensal

| ID | Requisito | Prioridade |
|---|---|---|
| RF-28 | No primeiro dia de cada mês, o bot deve enviar automaticamente o resumo do mês anterior | Importante |
| RF-29 | O relatório deve incluir: receitas, despesas, saldo, breakdown por categoria, pontos ganhos e metas ativas | Importante |
| RF-30 | O relatório deve incluir um insight educativo contextualizado com os dados reais do usuário | Obrigatório |
| RF-31 | O usuário deve poder solicitar o resumo a qualquer momento com `/resumo` | Obrigatório |

### F9 — Controle de Receitas e Gastos (módulo central)

| ID | Requisito | Prioridade |
|---|---|---|
| RF-32 | O usuário deve poder registrar receitas e despesas por mensagem em linguagem natural, sem necessidade de comandos | Obrigatório |
| RF-33 | O bot deve identificar automaticamente: valor, tipo (receita ou despesa), categoria, data e descrição | Obrigatório |
| RF-34 | O bot deve solicitar confirmação antes de salvar o lançamento, com opções de confirmar, corrigir ou cancelar | Obrigatório |
| RF-35 | O usuário deve poder corrigir valor, categoria, data ou descrição antes de confirmar | Obrigatório |
| RF-36 | Após confirmar, o bot deve exibir o saldo do mês atualizado e um insight rápido quando relevante | Obrigatório |
| RF-37 | O bot deve reconhecer expressões de tempo relativas: "hoje", "ontem", "semana passada" | Obrigatório |
| RF-38 | O comando `/planilha` deve gerar e enviar arquivo `.xlsx` com abas de Lançamentos e Resumo, incluindo gráfico de gastos por categoria | Obrigatório |
| RF-39 | O arquivo gerado deve ser descartado do servidor após o envio; apenas os dados estruturados são armazenados | Obrigatório |
| RF-40 | O usuário deve poder enviar foto de cupom fiscal para extração automática dos dados via visão computacional do modelo de linguagem | Importante |

**Categorias de receita (7):** Mesada, Salário, Estágio, Freelas, Presentes, Bolsa/Auxílio, Outros.

**Categorias de despesa (9):** Alimentação, Transporte, Lazer, Assinaturas, Educação, Saúde, Compras, Presentes, Outros.

### F10 — Módulo Aprender

| ID | Requisito | Prioridade |
|---|---|---|
| RF-41 | O comando `/aprender` deve abrir menu com trilha de educação financeira alinhada à BNCC | Obrigatório |
| RF-42 | A trilha deve conter 9 tópicos: receita e despesa, saldo, porcentagem, juros simples, juros compostos, metas, planejamento mensal, consumo consciente e apostas/bets | Obrigatório |
| RF-43 | Cada tópico deve apresentar conceito, exemplo em reais, quiz de múltipla escolha e mini-desafio prático | Obrigatório |
| RF-44 | O tópico sobre apostas/bets deve deixar explícito que não se trata de um caminho financeiro saudável, especialmente para jovens; em sinais de dependência, deve indicar busca de atendimento em Unidade Básica de Saúde (UBS) ou Centro de Atenção Psicossocial (CAPS) | Obrigatório |

---

## 4. Requisitos Não-Funcionais

### Desempenho

| ID | Requisito | Meta |
|---|---|---|
| RNF-01 | Tempo de resposta para registro de gasto (sem modelo de linguagem) | Menor que 1 segundo |
| RNF-02 | Tempo de resposta para perguntas com modelo de linguagem | Menor que 3 segundos (p95) |
| RNF-03 | Tempo de geração da planilha `.xlsx` | Menor que 5 segundos |
| RNF-04 | Disponibilidade em horário escolar (7h–22h, horário de Brasília) | Mínimo 99% |

### Escalabilidade e Segurança

| ID | Requisito |
|---|---|
| RNF-05 | Suportar 200 usuários simultâneos no MVP |
| RNF-06 | Aplicar limite de 30 mensagens por hora por usuário |
| RNF-07 | Ativar fallback automático para modelo local (Ollama) quando o serviço principal (Groq) estiver indisponível |
| RNF-08 | Não coletar CPF, RG, dados bancários, senhas ou extratos |
| RNF-09 | Autenticar webhooks do Telegram via token secreto no cabeçalho HTTP |
| RNF-10 | Permitir exclusão de dados de menores de 18 anos em até 48 horas mediante solicitação |
| RNF-11 | Purgar histórico de mensagens com mais de 90 dias semanalmente |
| RNF-12 | Descartar imagens de notas fiscais imediatamente após o processamento |

### Qualidade

| ID | Requisito |
|---|---|
| RNF-13 | Cobertura de testes unitários de no mínimo 80% nos módulos críticos |
| RNF-14 | O parser de linguagem natural deve ter no mínimo 30 casos de teste documentados |
| RNF-15 | Mensagens de erro devem ser amigáveis e nunca expor detalhes técnicos ao usuário |
| RNF-16 | O custo operacional deve ser inferior a R$ 50,00 por mês |

---

## 5. Regras de Negócio

| ID | Regra |
|---|---|
| RN-01 | O usuário é identificado exclusivamente pelo `telegram_id`; não há login ou senha |
| RN-02 | Pontos nunca diminuem — apenas se acumulam |
| RN-03 | A sequência (streak) de 7 dias exige pelo menos 1 lançamento por dia; a interrupção zera o contador |
| RN-04 | Um desafio semanal só pode ser marcado como concluído uma vez por semana |
| RN-05 | O bot nunca recomenda produtos financeiros específicos |
| RN-06 | Valores negativos não são aceitos; o bot solicita correção |
| RN-07 | Lançamentos podem ser editados em até 24 horas da criação; após esse prazo, apenas a exclusão é permitida |
| RN-08 | A renda mensal informada no onboarding serve como referência para cálculo de percentuais; não é tratada como dado bancário |

---

## 6. Prioridade de Implementação

| Sprint | Módulos |
|---|---|
| Sprint 1 | Onboarding (F1), registro de gastos e receitas (F9.1), resumo mensal (F9.3) |
| Sprint 2 | Exportação de planilha (F9.4), gamificação (F5), metas (F6) |
| Sprint 3 | Perguntas e respostas (F2), desafios (F4), simulador (F3) |
| Sprint 4 | Relatório mensal (F7), menu de ajuda, foto de cupom fiscal (F9.5) |

---

*Fini — Seu Parceiro Financeiro | Especificação de Requisitos v2.1 | 24/06/2026*
