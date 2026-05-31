"""Simulador Financeiro — Guardar vs. Gastar vs. Investir."""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from telegram import Update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

logger = logging.getLogger(__name__)

SIMULATOR_SYSTEM = """Você é um assistente de simulação financeira para jovens brasileiros.
Dado um valor e prazo, calcule e compare 3 cenários em formato claro:
1. Gastar agora (custo de oportunidade)
2. Guardar na Caderneta de Poupança (~6% ao ano)
3. Investir no Tesouro Selic (~10.5% ao ano — use esse valor fixo e avise que pode variar)

Use valores em reais, seja direto e mostre diferenças de forma motivadora.
Máximo 200 palavras. Use tabela simples em texto."""

SIMULATOR_HELP = """💡 *Simulador Financeiro*

Me diz quanto você quer guardar e por quanto tempo!

Exemplos:
• "Se eu guardar R$50 por mês por 1 ano"
• "R$200 reais por 6 meses"
• "R$10 por semana durante 2 anos"

Pode me mandar assim! 👇"""


@dataclass(frozen=True)
class SimulationInput:
    amount: Decimal
    months: int
    frequency: str = "monthly"


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _money(value: Decimal | float | int) -> str:
    normalized = Decimal(str(value)).quantize(Decimal("0.01"))
    return f"R${normalized:.2f}".replace(".", ",")


def looks_like_simulation_intent(text: str) -> bool:
    normalized = _normalize(text)
    has_amount = re.search(r"(?:r\$\s*)?\d+(?:[.,]\d{1,2})?", normalized)
    has_time = re.search(r"\b\d+\s*(mes|meses|ano|anos|semana|semanas|dia|dias)\b", normalized)
    has_sim_word = re.search(
        r"\b(simula|simular|simulador|quanto|guardar|guarda|guarrdar|juntar|junta|poupar|economizar|investir)\b",
        normalized,
    )
    return bool(has_amount and has_time and has_sim_word)


def parse_simulation_input(text: str) -> SimulationInput | None:
    normalized = _normalize(text)
    amount_match = re.search(r"(?:r\$\s*)?(\d+(?:[.,]\d{1,2})?)", normalized)
    if not amount_match:
        return None
    try:
        amount = Decimal(amount_match.group(1).replace(",", ".")).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None
    if amount <= 0:
        return None

    months = None
    time_match = re.search(r"\b(\d+)\s*(mes|meses|ano|anos|semana|semanas|dia|dias)\b", normalized)
    if time_match:
        qty = int(time_match.group(1))
        unit = time_match.group(2)
        if unit.startswith("ano"):
            months = qty * 12
        elif unit.startswith("semana"):
            months = max(1, round(qty / 4))
        elif unit.startswith("dia"):
            months = max(1, round(qty / 30))
        else:
            months = qty
    if not months or months <= 0:
        return None

    frequency = "weekly" if re.search(r"\b(por|cada)?\s*semana\b", normalized) else "monthly"
    if re.search(r"\bpor\s+dia\b|\bdiario\b|\bdiaria\b", normalized):
        frequency = "daily"
    return SimulationInput(amount=amount, months=months, frequency=frequency)


def build_simulation_response(simulation: SimulationInput) -> str:
    periods = simulation.months
    monthly_amount = simulation.amount
    label = "por mês"
    if simulation.frequency == "weekly":
        periods = simulation.months * 4
        monthly_amount = simulation.amount * Decimal("4")
        label = "por semana"
    elif simulation.frequency == "daily":
        periods = simulation.months * 30
        monthly_amount = simulation.amount * Decimal("30")
        label = "por dia"

    total_saved = monthly_amount * simulation.months
    savings_monthly_rate = Decimal("0.06") / Decimal("12")
    selic_monthly_rate = Decimal("0.105") / Decimal("12")

    savings_total = _future_value(monthly_amount, simulation.months, savings_monthly_rate)
    selic_total = _future_value(monthly_amount, simulation.months, selic_monthly_rate)

    return (
        "💡 *Simulação rápida*\n\n"
        f"Guardando *{_money(simulation.amount)} {label}* por *{simulation.months} meses*:\n\n"
        f"• Gastar agora: *{_money(0)}* guardado\n"
        f"• Guardar sem render: *{_money(total_saved)}*\n"
        f"• Poupança ~6% ao ano: *{_money(savings_total)}*\n"
        f"• Tesouro Selic ~10,5% ao ano: *{_money(selic_total)}*\n\n"
        f"Diferença entre só guardar e Selic: *{_money(selic_total - total_saved)}*.\n"
        "Valores são uma estimativa; taxas podem mudar."
    )


def _future_value(monthly_amount: Decimal, months: int, monthly_rate: Decimal) -> Decimal:
    total = Decimal("0")
    for _ in range(months):
        total = (total + monthly_amount) * (Decimal("1") + monthly_rate)
    return total.quantize(Decimal("0.01"))


async def handle_simulator_command(update: Update, db: AsyncSession, user: User):
    """Exibe instruções do simulador."""
    text = update.message.text or ""
    if len(text.split()) > 1:
        await handle_simulator_input(update, db, user, text)
        return
    await update.message.reply_text(SIMULATOR_HELP, parse_mode="Markdown")


async def handle_simulator_input(
    update: Update, db: AsyncSession, user: User, text: str
):
    """Processa uma entrada de simulação e retorna os 3 cenários."""
    await update.message.chat.send_action("typing")
    simulation = parse_simulation_input(text)
    if not simulation:
        await update.message.reply_text(SIMULATOR_HELP, parse_mode="Markdown")
        return
    await update.message.reply_text(build_simulation_response(simulation), parse_mode="Markdown")
