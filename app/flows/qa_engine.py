"""QA Engine — Responde perguntas financeiras via LLM."""
from __future__ import annotations
import logging
from telegram import Update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.message_log_repo import MessageLogRepository
from app.services.llm_service import llm_gateway
from app.flows.risk_education import betting_education_response, is_betting_topic

logger = logging.getLogger(__name__)


async def handle_question(
    update: Update,
    db: AsyncSession,
    user: User,
    context_messages: list[dict],
    month_summary: dict | None = None,
):
    """Responde uma pergunta financeira com o LLM e persiste a troca."""
    msg_repo = MessageLogRepository(db)
    text = update.message.text.strip()

    # Persiste a pergunta do usuário
    await msg_repo.add(user.id, "user", text)

    # Chama o LLM
    await update.message.chat.send_action("typing")
    response = await llm_gateway.qa_answer(text, context_messages, user, month_summary)
    if is_betting_topic(text) and "problema técnico" in response.lower():
        response = betting_education_response()

    # Persiste a resposta
    await msg_repo.add(user.id, "assistant", response)

    await update.message.reply_text(response, parse_mode="Markdown")
