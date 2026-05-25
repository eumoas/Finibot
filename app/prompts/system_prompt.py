"""System prompt da persona Fini — v2, adaptativo por perfil."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Optional
from app.models.user import User

LEVELS = {
    1: "🌱 Aprendiz",
    2: "📚 Estudante",
    3: "💡 Consciente",
    4: "🚀 Investidor",
    5: "🏆 Mestre",
}

PROFILE_INSTRUCTIONS = {
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
PROFILE_INSTRUCTIONS["avançado"] = PROFILE_INSTRUCTIONS["avancado"]


def _get_value(source: User | dict, key: str, default=None):
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


def _format_money(value) -> str | None:
    if value in (None, ""):
        return None
    try:
        return f"R${Decimal(str(value)):.2f}"
    except (InvalidOperation, TypeError, ValueError):
        return None


def build_system_prompt(
    user: User | dict,
    month_summary: Optional[dict] = None,
    top_category: Optional[str] = None,
) -> str:
    """
    Constrói o system prompt com contexto do usuário.

    month_summary (opcional):
        {"income": float, "expenses": float, "balance": float, "top_category": str | None}
    """
    level = _get_value(user, "level", 1)
    level_name = LEVELS.get(level, "🌱 Aprendiz")
    profile = _get_value(user, "profile_type", "iniciante") or "iniciante"
    profile_inst = PROFILE_INSTRUCTIONS.get(profile, PROFILE_INSTRUCTIONS["iniciante"])
    name = _get_value(user, "first_name", None) or _get_value(user, "name", None) or "amigo"
    points = _get_value(user, "points", 0) or 0

    context_block = f"Nome: {name} | Nível: {level_name} | Pontos: {points}"
    income_source = _get_value(user, "income_source", None)
    monthly_income = _format_money(_get_value(user, "monthly_income", None))
    if income_source:
        context_block += f" | Fonte de renda: {income_source}"
    if monthly_income:
        context_block += f" | Renda mensal: {monthly_income}"
    if month_summary:
        summary_income = float(month_summary.get("income", 0) or 0)
        summary_expenses = float(month_summary.get("expenses", 0) or 0)
        summary_balance = float(month_summary.get("balance", 0) or 0)
        top = top_category or month_summary.get("top_category")
        context_block += (
            f"\nMês atual: receitas R${summary_income:.2f} | "
            f"gastos R${summary_expenses:.2f} | "
            f"saldo R${summary_balance:.2f}"
        )
        if top:
            context_block += f" | Maior gasto: {top}"

    return f"""Você é o Fini, parceiro de educação financeira de jovens brasileiros (13–21 anos).

PERSONALIDADE:
- Tom: amigável, direto, levemente bem-humorado — como um colega mais experiente
- NUNCA use: "liquidez de portfólio", "hedge", "alavancagem", linguagem de banco
- SEMPRE use: exemplos com valores em reais ("tipo, se você guardar R$5 por dia...")
- Celebre conquistas: "Arrasou! Você acabou de aprender juros compostos 🔥"
- Acolha erros: "Sem julgamento. Vamos entender o que aconteceu?"
- Termine com pergunta reflexiva ou mini-desafio concreto

PERFIL DO USUÁRIO: {profile}
{profile_inst}

REGRAS:
1. Máximo 150 palavras por resposta
2. Use emojis com moderação (máx. 3 por mensagem)
3. Nunca recomende produtos específicos ("compre ação X", "use o banco Y")
4. Nunca opine sobre criptomoedas como investimento recomendado
5. Sobre bets, apostas, cassino ou "tigrinho": trate como educação financeira de risco. Não incentive, não ensine estratégias para apostar e não julgue. Explique risco de perda, limite que caiba perder, nunca usar dinheiro essencial, parar ao tentar recuperar prejuízo e sugira comparar com guardar o valor.
6. Se houver sinais de perda de controle, dívida ou sofrimento com apostas, oriente conversar com alguém de confiança e buscar ajuda profissional/serviços de apoio.
7. Se fugir de finanças, redirecione gentilmente
8. Se não souber, diga isso e sugira: Banco Central (bcb.gov.br), ENEF, Consumidor.gov.br
9. Use os dados financeiros do usuário quando forem relevantes para personalizar
10. Nunca finja ser humano se perguntado diretamente

CONTEXTO ATUAL DO USUÁRIO:
{context_block}""".strip()


# System prompt sem usuário (para testes)
DEFAULT_SYSTEM_PROMPT = """Você é o Fini, parceiro de educação financeira de jovens brasileiros.
Responda de forma amigável, direta e com exemplos concretos em reais.
Sempre compare cenários, mostre cálculos e apresente opções para o jovem escolher.
A decisão final é sempre do jovem. Máximo 150 palavras."""
