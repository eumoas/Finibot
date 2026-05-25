"""Simulador Financeiro — Guardar vs. Gastar vs. Investir."""
import logging
from telegram import Update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.llm_service import llm_gateway

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


async def handle_simulator_command(update: Update, db: AsyncSession, user: User):
    """Exibe instruções do simulador."""
    await update.message.reply_text(SIMULATOR_HELP, parse_mode="Markdown")


async def handle_simulator_input(
    update: Update, db: AsyncSession, user: User, text: str
):
    """Processa uma entrada de simulação e retorna os 3 cenários."""
    await update.message.chat.send_action("typing")
    messages = [{"role": "user", "content": f"Simule: {text}"}]
    response = await llm_gateway.chat(messages, SIMULATOR_SYSTEM)
    await update.message.reply_text(response, parse_mode="Markdown")
