"""Telegram Handler — ponto de entrada de todas as mensagens e callbacks."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.redis_client import get_redis
from app.repositories.user_repo import UserRepository
from app.services.session_service import SessionService
from app.prompts import templates
from app.api import command_router
from app.flows import finance_flow

logger = logging.getLogger(__name__)

COMMANDS = {
    "/start": command_router.cmd_start,
    "/ajuda": command_router.cmd_ajuda,
    "/help": command_router.cmd_ajuda,
    "/pontos": command_router.cmd_pontos,
    "/simular": command_router.cmd_simular,
    "/desafio": command_router.cmd_desafio,
    "/metas": command_router.cmd_metas,
    "/meta": command_router.cmd_meta,
    "/receita": command_router.cmd_receita,
    "/gasto": command_router.cmd_gasto,
    "/gastos": command_router.cmd_gastos,
    "/resumo": command_router.cmd_resumo,
    "/planilha": command_router.cmd_planilha,
    "/corrigir": command_router.cmd_corrigir,
    "/restart": command_router.cmd_restart,
    "/aprender": command_router.cmd_aprender,
}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para mensagens de texto."""
    if not update.message or not update.effective_user:
        return

    tg_user = update.effective_user
    telegram_id = tg_user.id

    async with AsyncSessionLocal() as db:
        redis = await get_redis()
        session_svc = SessionService(redis)

        # Rate limiting
        within_limit = await session_svc.check_rate_limit(telegram_id)
        if not within_limit:
            await update.message.reply_text(templates.RATE_LIMIT_MSG)
            return

        # Get or create user
        user_repo = UserRepository(db)
        user, is_new = await user_repo.get_or_create(
            telegram_id=telegram_id,
            username=tg_user.username,
            first_name=tg_user.first_name,
        )

        text = update.message.text or ""

        # Rota para comando explícito
        command = text.split(maxsplit=1)[0].lower() if text.startswith("/") else ""
        for cmd, handler in COMMANDS.items():
            if command == cmd:
                try:
                    await handler(update, db, user)
                except Exception as e:
                    logger.error(f"Erro no comando {cmd}: {e}", exc_info=True)
                    await update.message.reply_text(templates.ERROR_MSG)
                return

        # Usuário novo → inicia onboarding
        if not user.onboarded and not user.current_flow:
            from app.flows.onboarding import start_onboarding
            await start_onboarding(update, db)
            return

        # Mensagem dentro de fluxo ativo OU conversa livre
        context_messages = await session_svc.get_context(telegram_id)
        try:
            await command_router.route_message(update, db, user, context_messages)
            # Atualiza contexto Redis após resposta
            if text:
                await session_svc.add_message(telegram_id, "user", text)
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            await update.message.reply_text(templates.ERROR_MSG)


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para fotos de cupom/nota fiscal sem armazenar o arquivo."""
    if not update.message or not update.effective_user:
        logger.warning("handle_photo_message: update.message ou effective_user vazio")
        return

    tg_user = update.effective_user
    telegram_id = tg_user.id
    
    logger.info(f"📸 Foto recebida de {tg_user.username} (ID: {telegram_id})")
    caption = update.message.caption or ""
    logger.info(f"   Caption: '{caption}'")

    async with AsyncSessionLocal() as db:
        redis = await get_redis()
        session_svc = SessionService(redis)

        within_limit = await session_svc.check_rate_limit(telegram_id)
        if not within_limit:
            await update.message.reply_text(templates.RATE_LIMIT_MSG)
            return

        user_repo = UserRepository(db)
        user, _ = await user_repo.get_or_create(
            telegram_id=telegram_id,
            username=tg_user.username,
            first_name=tg_user.first_name,
        )

        if not user.onboarded and not user.current_flow:
            from app.flows.onboarding import start_onboarding
            await start_onboarding(update, db)
            return

        try:
            await finance_flow.handle_photo_receipt(update, db, user)
        except Exception as e:
            logger.error(f"❌ Erro ao processar foto: {e}", exc_info=True)
            try:
                await update.message.reply_text(templates.ERROR_MSG)
            except Exception as reply_error:
                logger.error(f"❌ Erro ao enviar mensagem de erro: {reply_error}", exc_info=True)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para callbacks de InlineKeyboard."""
    if not update.callback_query or not update.effective_user:
        return

    tg_user = update.effective_user

    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        user, _ = await user_repo.get_or_create(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
        )
        try:
            await command_router.handle_callback(update, db, user)
        except Exception as e:
            logger.error(f"Erro no callback: {e}", exc_info=True)
            await update.callback_query.answer("Algo deu errado. Tenta de novo!")
