"""Command Router — roteamento de comandos e mensagens do Telegram."""
from __future__ import annotations
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.repositories.challenge_repo import ChallengeRepository
from app.repositories.transaction_repo import TransactionRepository
from app.services.gamification import GamificationEngine, get_level_name, points_to_next_level
from app.flows import onboarding, qa_engine, simulator, goal_flow, finance_flow, learning_flow
from app.flows.risk_education import is_betting_topic
from app.prompts import templates

logger = logging.getLogger(__name__)

DIFFICULTY_EMOJI = {"facil": "🟢 Fácil", "medio": "🟡 Médio", "dificil": "🔴 Difícil"}
DIFFICULTY_ACTION = {"facil": "challenge_easy", "medio": "challenge_medium", "dificil": "challenge_hard"}


async def _build_month_summary(db: AsyncSession, user: User) -> dict | None:
    """Monta contexto financeiro do mês para personalizar respostas de Q&A."""
    if not user.onboarded:
        return None

    repo = TransactionRepository(db)
    start, end = finance_flow._month_range()
    transactions = await repo.list_by_period(user.id, start, end)
    if not transactions:
        return None

    summary = finance_flow._summarize(transactions)
    top_category = next(iter(summary["by_category"]), None)
    return {
        "income": float(summary["income"]),
        "expenses": float(summary["expenses"]),
        "balance": float(summary["balance"]),
        "top_category": top_category,
    }


async def route_message(update: Update, db: AsyncSession, user: User, context_messages: list[dict]):
    """Roteia mensagem de texto para o flow correto."""
    text = update.message.text or ""

    # Usuário em fluxo ativo de onboarding
    if user.current_flow == "onboarding" and user.flow_step:
        step = user.flow_step.split("|")[0] if "|" in user.flow_step else user.flow_step
        await onboarding.handle_onboarding_step(update, db, step, user)
        return

    if user.current_flow == "finance_correction" and user.flow_step:
        await finance_flow.handle_correction_step(update, db, user)
        return

    if user.current_flow == "goal_progress" and user.flow_step:
        handled = await goal_flow.handle_goal_progress_step(update, db, user)
        if handled:
            return

    if is_betting_topic(text):
        month_summary = await _build_month_summary(db, user)
        await qa_engine.handle_question(update, db, user, context_messages, month_summary)
        return

    if user.onboarded and simulator.looks_like_simulation_intent(text):
        await simulator.handle_simulator_input(update, db, user, text)
        return

    # Tenta parsear como meta antes de gastos quando houver intenção clara.
    if user.onboarded and (
        ("-" in text and ("R$" in text or "r$" in text))
        or goal_flow.looks_like_goal_intent(text)
    ):
        created = await goal_flow.parse_and_create_goal(update, db, user, text)
        if created:
            return

    # Lançamentos financeiros em linguagem natural: LLM primeiro, parser regex como fallback no finance_flow.
    if user.onboarded:
        created_transaction = await finance_flow.maybe_handle_natural_transaction(update, db, user, text)
        if created_transaction:
            return

    # Conversa livre → QA Engine (LLM)
    month_summary = await _build_month_summary(db, user)
    await qa_engine.handle_question(update, db, user, context_messages, month_summary)


async def cmd_start(update: Update, db: AsyncSession, user: User):
    if not user.onboarded:
        await onboarding.start_onboarding(update, db)
    else:
        name = user.first_name or "amigo"
        await update.message.reply_text(
            f"👋 Ei, {name}! Já nos conhecemos 😄\n\n"
            "Pode me mandar qualquer pergunta sobre finanças, ou usa /ajuda para ver os comandos!",
            parse_mode="Markdown",
        )


async def cmd_ajuda(update: Update, db: AsyncSession, user: User):
    await update.message.reply_text(templates.HELP_MENU, parse_mode="Markdown")


async def cmd_pontos(update: Update, db: AsyncSession, user: User):
    level_name = get_level_name(user.level)
    next_pts = points_to_next_level(user.points, user.level)
    msg = templates.POINTS_STATUS(user.first_name or "amigo", user.points, level_name, next_pts)
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_simular(update: Update, db: AsyncSession, user: User):
    await simulator.handle_simulator_command(update, db, user)


async def cmd_desafio(update: Update, db: AsyncSession, user: User):
    challenge_repo = ChallengeRepository(db)
    user_repo = UserRepository(db)
    gamification = GamificationEngine(user_repo)

    existing = await challenge_repo.get_user_challenge_this_week(user.id)
    if existing:
        if existing.completed_at:
            await update.message.reply_text(
                "✅ Você já completou o desafio desta semana! Parabéns 🎉\n"
                "Volte na próxima semana para um novo desafio!",
                parse_mode="Markdown",
            )
        else:
            challenge = await challenge_repo.get_challenge_by_id(existing.challenge_id)
            diff = DIFFICULTY_EMOJI.get(challenge.difficulty, "⚪")
            keyboard = [[InlineKeyboardButton("✅ Completei!", callback_data=f"challenge_done_{existing.id}")]]
            code = f"{challenge.code} — " if getattr(challenge, "code", None) else ""
            await update.message.reply_text(
                f"🏆 *Seu desafio da semana:*\n\n*{code}{challenge.title}*\n{challenge.description}\n\n*Dificuldade:* {diff}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return

    challenge = await challenge_repo.get_random_active()
    if not challenge:
        await update.message.reply_text("😅 Sem desafios disponíveis no momento. Volta em breve!")
        return

    uc = await challenge_repo.accept_challenge(user.id, challenge.id)
    diff = DIFFICULTY_EMOJI.get(challenge.difficulty, "⚪")
    keyboard = [[InlineKeyboardButton("✅ Completei!", callback_data=f"challenge_done_{uc.id}")]]
    code = f"{challenge.code} — " if getattr(challenge, "code", None) else ""
    await update.message.reply_text(
        f"🎯 *Desafio da Semana Aceito!*\n\n*{code}{challenge.title}*\n{challenge.description}\n\n*Dificuldade:* {diff}\n\nBoa sorte! 💪",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_meta(update: Update, db: AsyncSession, user: User):
    await goal_flow.handle_create_goal_command(update, db, user)


async def cmd_metas(update: Update, db: AsyncSession, user: User):
    await goal_flow.handle_list_goals(update, db, user)


async def cmd_receita(update: Update, db: AsyncSession, user: User):
    await finance_flow.handle_income_command(update, db, user)


async def cmd_gasto(update: Update, db: AsyncSession, user: User):
    await finance_flow.handle_expense_command(update, db, user)


async def cmd_gastos(update: Update, db: AsyncSession, user: User):
    await finance_flow.handle_gastos_command(update, db, user)


async def cmd_resumo(update: Update, db: AsyncSession, user: User):
    await finance_flow.handle_summary_command(update, db, user)


async def cmd_planilha(update: Update, db: AsyncSession, user: User):
    await finance_flow.handle_spreadsheet_command(update, db, user)


async def cmd_corrigir(update: Update, db: AsyncSession, user: User):
    await finance_flow.handle_correct_command(update, db, user)


async def cmd_restart(update: Update, db: AsyncSession, user: User):
    await finance_flow.handle_restart_command(update, db, user)


async def cmd_aprender(update: Update, db: AsyncSession, user: User):
    await learning_flow.handle_learning_command(update, db, user)


async def handle_callback(update: Update, db: AsyncSession, user: User):
    """Processa callbacks de InlineKeyboard."""
    query = update.callback_query
    data = query.data

    handled_learning = await learning_flow.handle_learning_callback(update, db, user, data)
    if handled_learning:
        return

    handled_goal = await goal_flow.handle_goal_callback(update, db, user)
    if handled_goal:
        return

    handled_transaction = await finance_flow.handle_transaction_callback(update, db, user)
    if handled_transaction:
        return

    user_repo = UserRepository(db)
    challenge_repo = ChallengeRepository(db)
    gamification = GamificationEngine(user_repo)

    # Callbacks do onboarding
    if data.startswith("onb_"):
        done = await onboarding.handle_quiz_callback(update, db, user, data)
        if done:
            # level_up check após onboarding
            result = None  # já foi concedido dentro do handle_quiz_callback
        return

    # Callback de desafio completo
    if data.startswith("challenge_done_"):
        import uuid as _uuid
        uc_id = _uuid.UUID(data.replace("challenge_done_", ""))
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.models.challenge import UserChallenge, Challenge

        result_row = await db.execute(
            select(UserChallenge).where(UserChallenge.id == uc_id)
        )
        uc = result_row.scalar_one_or_none()
        if not uc or uc.completed_at:
            await query.answer("Já foi registrado! 🎉")
            return

        challenge_row = await db.execute(
            select(Challenge).where(Challenge.id == uc.challenge_id)
        )
        challenge = challenge_row.scalar_one_or_none()
        action = DIFFICULTY_ACTION.get(challenge.difficulty if challenge else "facil", "challenge_easy")

        await challenge_repo.complete_challenge(uc)
        result = await gamification.award(user, action)
        await query.answer("Incrível! 🔥")

        level_msg = ""
        if result.leveled_up:
            level_msg = f"\n\n{templates.LEVEL_UP(result.level_name)}"

        await query.edit_message_text(
            f"🎉 *Desafio Concluído!*\n\n"
            f"Você ganhou *+{result.points_gained} pontos*!\n"
            f"Total: {result.new_total} pontos | Nível: {result.level_name}"
            f"{level_msg}",
            parse_mode="Markdown",
        )
