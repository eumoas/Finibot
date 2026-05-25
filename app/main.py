"""FastAPI + Telegram Application — Entrypoint principal."""
from __future__ import annotations
import logging
import sys
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request, Response, Header, HTTPException
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.redis_client import close_redis
from app.api.telegram_handler import handle_message, handle_photo_message, handle_callback_query

# Logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Telegam Application (singleton)
PTB_APP: Application | None = None


async def build_telegram_app() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown do FastAPI."""
    global PTB_APP
    logger.info("🚀 Iniciando Fini Bot...")

    # Cria tabelas (em produção use Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Banco de dados pronto")

    # Popula desafios iniciais se o banco estiver vazio
    from app.db.seed_challenges import seed_challenges
    async with AsyncSessionLocal() as db:
        await seed_challenges(db)
        logger.info("✅ Seed de desafios verificado")

    PTB_APP = await build_telegram_app()
    await PTB_APP.initialize()

    if settings.use_webhook:
        # Modo produção: registra webhook
        webhook_url = f"{settings.webhook_url}/telegram/webhook"
        await PTB_APP.bot.set_webhook(
            url=webhook_url,
            secret_token=settings.telegram_secret_token,
        )
        logger.info(f"✅ Webhook registrado: {webhook_url}")
    else:
        # Modo dev: long polling em background
        await PTB_APP.start()
        await PTB_APP.updater.start_polling(drop_pending_updates=True)
        logger.info("✅ Long polling ativo (modo desenvolvimento)")

    logger.info("🤖 Fini Bot está online!")
    yield

    # Shutdown
    logger.info("🛑 Desligando Fini Bot...")
    if PTB_APP:
        if settings.use_webhook:
            await PTB_APP.bot.delete_webhook()
        else:
            await PTB_APP.updater.stop()
        await PTB_APP.stop()
        await PTB_APP.shutdown()
    await close_redis()
    await engine.dispose()
    logger.info("✅ Shutdown completo")


app = FastAPI(
    title="Fini — Seu Parceiro Financeiro",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok", "bot": "Fini", "env": settings.environment}


@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Optional[str] = Header(default=None),
):
    """Recebe updates do Telegram em modo webhook (produção)."""
    if x_telegram_bot_api_secret_token != settings.telegram_secret_token:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    data = await request.json()
    update = Update.de_json(data, PTB_APP.bot)
    await PTB_APP.process_update(update)
    return Response(status_code=200)


@app.get("/admin/stats")
async def admin_stats(x_api_key: Optional[str] = Header(default=None)):
    """Estatísticas básicas do piloto."""
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    from sqlalchemy import text, func, select
    from app.core.database import AsyncSessionLocal
    from app.models.user import User
    async with AsyncSessionLocal() as db:
        total = await db.scalar(select(func.count(User.id)))
        onboarded = await db.scalar(
            select(func.count(User.id)).where(User.onboarded == True)
        )
    return {"total_users": total, "onboarded": onboarded}
