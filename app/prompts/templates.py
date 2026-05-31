"""Templates de mensagens fixas do Fini."""

WELCOME_NEW = """👋 Oi! Eu sou o *Fini*, seu parceiro para organizar dinheiro sem complicar.

Comigo você pode registrar gastos e receitas por mensagem, ver resumo do mês, criar metas, receber planilha e tirar dúvidas de finanças em linguagem simples.

Pra deixar tudo mais personalizado, vou te fazer algumas perguntas rápidas. Pode usar valores aproximados ou fictícios se preferir.

Primeiro: qual é o seu nome?"""

ONBOARDING_ASK_AGE = lambda name: f"""Boa, {name}! 🙌

E a sua idade?"""

ONBOARDING_TOO_YOUNG = """😊 Que legal que você quer aprender sobre finanças tão cedo!

Por ter menos de 10 anos, recomendo conversar com seus pais ou responsáveis junto comigo.

Pode me contar sua dúvida que eu respondo!"""

ONBOARDING_ASK_INCOME_SOURCE = """Qual é sua *principal fonte de renda* hoje?"""

ONBOARDING_ASK_MONTHLY_INCOME = lambda source: f"""Entendi: *{source}*.

Agora me manda uma estimativa da sua renda mensal.

Pode ser só número, tipo `300` ou `1250,50`. Se não quiser informar a real, pode usar um valor aproximado ou fictício."""

ONBOARDING_INVALID_INCOME = """Não consegui ler esse valor.

Manda só um número, tipo `300` ou `1250,50`."""

ONBOARDING_ASK_Q1 = """Agora o quiz diagnóstico — 3 perguntas rápidas ⚡

*Pergunta 1 de 3:*
Quando você recebe sua mesada ou salário, o que faz primeiro?"""

ONBOARDING_ASK_Q2 = """*Pergunta 2 de 3:*
Você já ouviu falar em juros compostos?"""

ONBOARDING_ASK_Q3 = """*Pergunta 3 de 3:*
Você tem algum objetivo financeiro agora?"""

ONBOARDING_COMPLETE = lambda name, profile, points: f"""🎉 Diagnóstico concluído, {name}!

*Seu perfil:* {profile}

Você ganhou *+{points} pontos* só por começar! 💰

Próximo passo: me manda seu primeiro gasto, tipo `gastei 18,50 no lanche hoje`, que eu registro pra você.

/ajuda — ver tudo que posso fazer por você"""

HELP_MENU = """🤖 *Fini — Menu*

*Controlar gastos*
/gasto — Registrar uma despesa
/receita — Registrar dinheiro que entrou
/gastos — Ver exemplos de registro
/resumo — Saldo mensal, categorias e insights
/planilha — Receber planilha .xlsx do mês
/corrigir — Corrigir lançamento já salvo
/restart — Começar do zero

*Metas*
/meta — Criar nova meta
/metas — Ver suas metas

*Aprender*
/simular — Simulador financeiro
/desafio — Desafio da semana
/aprender — Trilha rápida de educação financeira
/pontos — Pontuação e nível

Também pode mandar uma pergunta ou um lançamento direto, tipo `gastei 18,50 no lanche hoje`."""

POINTS_STATUS = lambda name, points, level_name, next_pts: f"""💰 *{name}, seus pontos:*

🏅 Nível: *{level_name}*
⭐ Pontos: *{points}*
{'🏆 Você é um Mestre! Nível máximo!' if next_pts == 0 else f'📈 Faltam *{next_pts} pts* para o próximo nível'}"""

RATE_LIMIT_MSG = """⏸️ Ei! Você mandou muitas mensagens na última hora.

Dá uma pausa de uns minutinhos e volta! Tô aqui 😊"""

ERROR_MSG = """😅 Tive um probleminha técnico aqui.

Tenta de novo em alguns segundos, tá?"""

LEVEL_UP = lambda level_name: f"""🎊 *SUBIU DE NÍVEL!*

Agora você é: *{level_name}* 

Continue assim — você tá indo muito bem! 🔥"""
