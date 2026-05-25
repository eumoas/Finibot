"""Fluxo /aprender — cards BNCC, quiz rápido e mini-desafios."""
from __future__ import annotations

from decimal import Decimal
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.bncc_learning import LEARNING_TOPICS, LearningTopic, get_topic
from app.models.user import User
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.user_repo import UserRepository
from app.services.gamification import GamificationEngine

CALLBACK_MENU = "learn_menu"
CALLBACK_TOPIC_PREFIX = "learn_topic:"
CALLBACK_QUIZ_PREFIX = "learn_quiz:"
CALLBACK_CHALLENGE_PREFIX = "learn_challenge:"


def parse_learning_callback(data: str) -> tuple[str, str | None, str | None]:
    if data == CALLBACK_MENU:
        return "menu", None, None
    if data.startswith(CALLBACK_TOPIC_PREFIX):
        return "topic", data.replace(CALLBACK_TOPIC_PREFIX, "", 1), None
    if data.startswith(CALLBACK_QUIZ_PREFIX):
        _, slug, option = data.split(":", 2)
        return "quiz", slug, option
    if data.startswith(CALLBACK_CHALLENGE_PREFIX):
        return "challenge", data.replace(CALLBACK_CHALLENGE_PREFIX, "", 1), None
    return "unknown", None, None


async def _month_summary(db: AsyncSession, user: User) -> dict | None:
    repo = TransactionRepository(db)
    from app.flows.finance_flow import _month_range, _summarize

    start, end = _month_range()
    transactions = await repo.list_by_period(user.id, start, end)
    if not transactions:
        return None
    summary = _summarize(transactions)
    return {
        "income": summary["income"],
        "expenses": summary["expenses"],
        "balance": summary["balance"],
        "top_category": next(iter(summary["by_category"]), None),
        "by_category": summary["by_category"],
    }


def _money(value: Decimal | float | int) -> str:
    normalized = Decimal(str(value or 0)).quantize(Decimal("0.01"))
    return f"R${normalized:.2f}".replace(".", ",")


def _topic_keyboard(topic: LearningTopic) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(label, callback_data=f"{CALLBACK_QUIZ_PREFIX}{topic.slug}:{option}")
            for option, label in topic.quiz_options.items()
        ],
        [InlineKeyboardButton("Mini-desafio", callback_data=f"{CALLBACK_CHALLENGE_PREFIX}{topic.slug}")],
        [InlineKeyboardButton("Voltar", callback_data=CALLBACK_MENU)],
    ]
    return InlineKeyboardMarkup(rows)


def learning_menu_markup() -> InlineKeyboardMarkup:
    rows = []
    for index in range(0, len(LEARNING_TOPICS), 2):
        rows.append(
            [
                InlineKeyboardButton(
                    f"{topic.code} {topic.title}",
                    callback_data=f"{CALLBACK_TOPIC_PREFIX}{topic.slug}",
                )
                for topic in LEARNING_TOPICS[index : index + 2]
            ]
        )
    return InlineKeyboardMarkup(rows)


def render_learning_menu() -> str:
    return (
        "📚 *Aprender com o Fini*\n\n"
        "Escolha um tema para ver um card curto, responder um quiz e sair com um mini-desafio prático."
    )


def render_learning_card(topic: LearningTopic, summary: dict | None = None, user: User | None = None) -> str:
    example = topic.example

    if topic.slug == "saldo" and summary:
        example = (
            f"No seu mês atual: entradas {_money(summary['income'])}, "
            f"saídas {_money(summary['expenses'])}, saldo {_money(summary['balance'])}."
        )
    elif topic.slug == "porcentagem" and summary and user and user.monthly_income:
        top_category = summary.get("top_category")
        by_category = summary.get("by_category", {})
        if top_category and top_category in by_category:
            pct = Decimal(str(by_category[top_category])) / Decimal(str(user.monthly_income)) * 100
            example = f"Sua maior categoria é {top_category}: {_money(by_category[top_category])}, cerca de {pct:.0f}% da sua renda."
    elif topic.slug == "planejamento" and user and user.monthly_income:
        income = Decimal(str(user.monthly_income))
        example = f"Com renda de {_money(income)}, 10% para uma meta seria {_money(income * Decimal('0.10'))}."

    commands = ", ".join(topic.related_commands)
    return (
        f"*{topic.code} — {topic.title}*\n\n"
        f"{topic.content}\n\n"
        f"*Exemplo:* {example}\n\n"
        f"*Quiz:* {topic.quiz_question}\n\n"
        f"Comandos úteis: {commands}"
    )


async def handle_learning_command(update: Update, db: AsyncSession, user: User):
    await update.message.reply_text(
        render_learning_menu(),
        parse_mode="Markdown",
        reply_markup=learning_menu_markup(),
    )


async def handle_learning_callback(update: Update, db: AsyncSession, user: User, data: str) -> bool:
    action, slug, option = parse_learning_callback(data)
    if action == "unknown":
        return False

    query = update.callback_query
    await query.answer()

    if action == "menu":
        await query.edit_message_text(
            render_learning_menu(),
            parse_mode="Markdown",
            reply_markup=learning_menu_markup(),
        )
        return True

    topic = get_topic(slug or "")
    if not topic:
        await query.edit_message_text("Não encontrei esse tema. Use /aprender para abrir o menu.")
        return True

    user_repo = UserRepository(db)
    gamification = GamificationEngine(user_repo)

    if action == "topic":
        await gamification.award(user, "learning_topic_viewed")
        summary = await _month_summary(db, user)
        await query.edit_message_text(
            render_learning_card(topic, summary=summary, user=user),
            parse_mode="Markdown",
            reply_markup=_topic_keyboard(topic),
        )
        return True

    if action == "quiz":
        correct = option == topic.correct_option
        if correct:
            await gamification.award(user, "learning_quiz_correct")
        feedback = topic.feedback_correct if correct else topic.feedback_wrong
        await query.edit_message_text(
            f"*{topic.title}*\n\n{feedback}\n\n*Mini-desafio:* {topic.mini_challenge}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Ver card de novo", callback_data=f"{CALLBACK_TOPIC_PREFIX}{topic.slug}")],
                    [InlineKeyboardButton("Voltar", callback_data=CALLBACK_MENU)],
                ]
            ),
        )
        return True

    if action == "challenge":
        result = await gamification.award(user, "learning_challenge_done")
        await query.edit_message_text(
            f"🎯 *Mini-desafio aceito*\n\n{topic.mini_challenge}\n\nVocê ganhou +{result.points_gained} pontos por aprender praticando.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data=CALLBACK_MENU)]]),
        )
        return True

    return False
