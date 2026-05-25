"""Prompt para geração de insights financeiros contextualizados."""

INSIGHT_SYSTEM_PROMPT = """
Você é o Fini, parceiro financeiro de jovens brasileiros.
Gere um insight curto (máx. 2 frases) sobre o padrão de gastos do usuário.
Use os dados fornecidos. Seja específico, use os valores reais.
Tom: amigável e direto, como um amigo que entende de dinheiro.
Termine com uma observação útil ou pergunta reflexiva.
Não use linguagem de banco ou termos formais.
Use no máximo 2 emojis.
"""

# Lógica de quando disparar insight:
# - Quando o gasto de uma categoria ultrapassa 30% da renda mensal
# - Quando o saldo mensal fica negativo pela primeira vez no mês
# - Quando o usuário fecha o 7º dia consecutivo de registros (streak)
# - Quando uma categoria tem >5 lançamentos no mês
# - No 20º dia do mês (projeção de fechamento)


def should_generate_insight(
    category_total: float,
    monthly_income: float,
    category_count: int,
    balance: float,
    streak_days: int,
) -> bool:
    """Decide se deve gerar insight após um lançamento."""
    if monthly_income > 0 and category_total / monthly_income > 0.30:
        return True
    if balance < 0:
        return True
    if streak_days == 7:
        return True
    if category_count > 5:
        return True
    return False


def build_insight_context(
    user_name: str,
    category: str,
    category_total: float,
    monthly_income: float,
    balance: float,
    total_expenses: float,
    streak_days: int,
) -> str:
    """Constrói contexto para o LLM gerar insight."""
    income_pct = (
        f"{category_total / monthly_income * 100:.0f}% da renda"
        if monthly_income > 0
        else "sem renda informada"
    )
    return (
        f"Usuário: {user_name}\n"
        f"Categoria do lançamento: {category}\n"
        f"Total gasto em {category} este mês: R${category_total:.2f} ({income_pct})\n"
        f"Total de gastos do mês: R${total_expenses:.2f}\n"
        f"Saldo do mês: R${balance:.2f}\n"
        f"Renda mensal informada: R${monthly_income:.2f}\n"
        f"Streak de registros: {streak_days} dias consecutivos"
    )
