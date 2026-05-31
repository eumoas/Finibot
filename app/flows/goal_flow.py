"""Flow de Metas Financeiras — criar, listar e atualizar progresso."""
from __future__ import annotations

import logging
import re
import unicodedata
import uuid
from decimal import Decimal, InvalidOperation
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.goal import Goal
from app.repositories.goal_repo import GoalRepository
from app.repositories.user_repo import UserRepository
from app.services.gamification import GamificationEngine

logger = logging.getLogger(__name__)

CREATE_GOAL_HELP = """🎯 *Nova Meta Financeira*

Me conta sua meta no formato:
*[objetivo] - R$[valor]*

Exemplos:
• "Comprar um fone - R$150"
• "Reserva emergência - R$500"
• "Viagem com a galera - R$800"

Pode mandar! 👇"""

GOAL_INTENT_WORDS = {
    "economizar",
    "economiza",
    "economizando",
    "guardar",
    "guarda",
    "guardando",
    "juntar",
    "junta",
    "juntando",
    "meta",
    "objetivo",
    "poupar",
    "poupando",
    "reserva",
    "role",
    "rolé",
    "rolê",
    "viagem",
    "viajem",
    "viage",
    "viajar",
}
FINANCE_ACTION_WORDS = {
    "comprei",
    "compra",
    "gastei",
    "gasto",
    "paguei",
    "pagamento",
    "recebi",
    "ganhei",
}
GOAL_CALLBACK_ADD_PREFIX = "goal_add_"
GOAL_CALLBACK_DONE_PREFIX = "goal_done_"
GOAL_CALLBACK_REFRESH_PREFIX = "goal_view_"


def _money(value: Decimal | float | int) -> str:
    normalized = Decimal(str(value)).quantize(Decimal("0.01"))
    return f"R${normalized:.2f}".replace(".", ",")


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _parse_money_input(text: str) -> Decimal | None:
    match = re.search(r"(?:R\$\s*)?(\d+(?:[.,]\d{1,2})?)", text, flags=re.I)
    if not match:
        return None
    try:
        amount = Decimal(match.group(1).replace(",", ".")).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None
    if amount <= 0:
        return None
    return amount


def looks_like_goal_intent(text: str) -> bool:
    normalized = _normalize(text)
    has_goal_word = any(re.search(rf"\b{word}\b", normalized, flags=re.I) for word in GOAL_INTENT_WORDS)
    has_finance_action = any(re.search(rf"\b{word}\b", normalized, flags=re.I) for word in FINANCE_ACTION_WORDS)
    if has_finance_action and not re.search(r"\b(meta|objetivo|juntar|guardar|poupar)\b", normalized, flags=re.I):
        return False
    return has_goal_word


def _clean_goal_title(title: str) -> str:
    replacements = {
        r"\bc\b": "com",
        r"\bglr\b": "galera",
        r"\bviajem\b": "viagem",
        r"\bviage\b": "viagem",
        r"\brole\b": "rolê",
    }
    cleaned = title.strip()
    for pattern, replacement in replacements.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.I)
    cleaned = re.sub(
        r"\b(economizar|economiza|economizando|guardar|guarda|guardando|juntar|junta|juntando|poupar|poupando)\b",
        "",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" -–")


def _parse_goal_text(text: str) -> tuple[str, Decimal] | None:
    original = text.strip()
    cleaned = re.sub(r"^/meta\s*", "", original, flags=re.I).strip()
    cleaned = re.sub(
        r"^(quero|qro|queria|preciso|vou|pretendo|bora)\s+(criar\s+)?(uma\s+)?(meta\s+)?(para\s+|pra\s+|pro\s+)?",
        "",
        cleaned,
        flags=re.I,
    ).strip()
    cleaned = re.sub(r"^(meta|objetivo)\s+(para\s+|pra\s+|pro\s+)?", "", cleaned, flags=re.I).strip()

    patterns = [
        r"(.+?)\s*[-–]\s*[Rr]\$?\s*([\d.,]+)",
        r"(.+?)\s+(?:no\s+|na\s+)?valor\s+(?:de\s+)?[Rr]?\$?\s*([\d.,]+)$",
        r"(.+?)\s+(?:de\s+)?[Rr]\$\s*([\d.,]+)",
        r"(.+?)\s+(?:por|para|pra|valor|objetivo)\s+(?:de\s+)?[Rr]?\$?\s*([\d.,]+)$",
        r"(.+?)\s+([\d.,]+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if not match:
            continue
        title = _clean_goal_title(match.group(1))
        amount = _parse_money_input(match.group(2))
        if title and amount:
            return title[:200], amount
    return None


def _goal_card_text(goal: Goal, intro: str | None = None) -> str:
    deadline_str = goal.deadline.strftime("%d/%m/%Y") if goal.deadline else "sem prazo"
    lines = []
    if intro:
        lines.extend([intro, ""])
    lines.extend(
        [
            f"🎯 *{goal.title}*",
            f"{_money(goal.current_amount)} / {_money(goal.target_amount)}",
            f"{goal.progress_bar} | Prazo: {deadline_str}",
        ]
    )
    return "\n".join(lines)


def _goal_keyboard(goal: Goal) -> InlineKeyboardMarkup:
    goal_id = str(goal.id)
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Adicionar valor", callback_data=f"{GOAL_CALLBACK_ADD_PREFIX}{goal_id}")],
            [InlineKeyboardButton("Concluir", callback_data=f"{GOAL_CALLBACK_DONE_PREFIX}{goal_id}")],
        ]
    )


async def handle_list_goals(update: Update, db: AsyncSession, user: User):
    """Lista metas ativas do usuário."""
    goal_repo = GoalRepository(db)
    goals = await goal_repo.get_active_by_user(user.id)

    if not goals:
        await update.message.reply_text(
            "📭 Você ainda não tem metas! Use /meta para criar sua primeira 🎯",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text("🎯 *Suas Metas Ativas:*", parse_mode="Markdown")
    for goal in goals:
        await update.message.reply_text(
            _goal_card_text(goal),
            parse_mode="Markdown",
            reply_markup=_goal_keyboard(goal),
        )


async def handle_create_goal_command(update: Update, db: AsyncSession, user: User):
    """Instrui o usuário sobre como criar uma meta."""
    text = update.message.text or ""
    if len(text.split()) > 1:
        created = await parse_and_create_goal(update, db, user, text)
        if created:
            return

    await UserRepository(db).update(user, current_flow="goal_create", flow_step="goal_create")
    await update.message.reply_text(CREATE_GOAL_HELP, parse_mode="Markdown")


async def handle_goal_create_step(update: Update, db: AsyncSession, user: User) -> bool:
    """Recebe a descricao da meta após o usuário chamar /meta."""
    user_repo = UserRepository(db)
    text = (update.message.text or "").strip()
    if text.lower() in {"cancelar", "cancela", "cancel"}:
        await user_repo.update(user, current_flow=None, flow_step=None)
        await update.message.reply_text("Tudo bem, não criei nenhuma meta.")
        return True

    created = await parse_and_create_goal(update, db, user, text)
    if created:
        await user_repo.update(user, current_flow=None, flow_step=None)
        return True

    await user_repo.update(user, current_flow="goal_create", flow_step="goal_create")
    await update.message.reply_text(
        "Quase! Me manda a meta com objetivo e valor, tipo `Comprar um tênis - R$150`.",
        parse_mode="Markdown",
    )
    return True


async def parse_and_create_goal(
    update: Update, db: AsyncSession, user: User, text: str
) -> bool:
    """
    Tenta parsear uma meta do texto livre.
    Formato esperado: 'Título - R$Valor'
    Retorna True se criou a meta, False se não reconheceu o padrão.
    """
    parsed = _parse_goal_text(text)
    if not parsed:
        return False

    title, amount = parsed

    goal_repo = GoalRepository(db)
    user_repo = UserRepository(db)
    gamification = GamificationEngine(user_repo)

    # Verifica limite de 5 metas ativas
    existing = await goal_repo.get_active_by_user(user.id)
    if len(existing) >= 5:
        await update.message.reply_text(
            "⚠️ Você já tem 5 metas ativas — o máximo por enquanto.\n"
            "Complete ou abandone uma para criar outra! Use /metas para ver.",
            parse_mode="Markdown",
        )
        return True

    goal = await goal_repo.create(user.id, title, float(amount))
    result = await gamification.award(user, "goal_created")

    await update.message.reply_text(
        f"✅ *Meta criada!*\n\n"
        f"🎯 {goal.title}\n"
        f"💰 Objetivo: {_money(amount)}\n\n"
        f"Você ganhou *+{result.points_gained} pontos*! "
        f"Use /metas para acompanhar. 🚀",
        parse_mode="Markdown",
    )
    return True


async def handle_goal_progress_step(update: Update, db: AsyncSession, user: User) -> bool:
    """Recebe o valor informado após o usuário tocar em Adicionar valor."""
    step = user.flow_step or ""
    if not step.startswith("goal_add:"):
        return False

    user_repo = UserRepository(db)
    await user_repo.update(user, current_flow=None, flow_step=None)

    text = (update.message.text or "").strip()
    if text.lower() in {"cancelar", "cancela", "cancel"}:
        await update.message.reply_text("Tudo bem, não alterei a meta.")
        return True

    amount = _parse_money_input(text)
    if not amount:
        await user_repo.update(user, current_flow="goal_progress", flow_step=step)
        await update.message.reply_text("Manda um valor válido, tipo `50` ou `R$50,00`.", parse_mode="Markdown")
        return True

    try:
        goal_id = uuid.UUID(step.split(":", 1)[1])
    except (ValueError, IndexError):
        await update.message.reply_text("Não consegui identificar essa meta. Usa /metas e tenta de novo.")
        return True

    goal_repo = GoalRepository(db)
    goal = await goal_repo.get_active_by_id(user.id, goal_id)
    if not goal:
        await update.message.reply_text("Essa meta não está mais ativa. Usa /metas para ver as atuais.")
        return True

    was_completed = goal.completed
    goal = await goal_repo.add_progress(goal, amount)

    gamification = GamificationEngine(user_repo)
    progress_result = await gamification.award(user, "goal_progress_updated")
    points = [f"+{progress_result.points_gained} progresso em meta"]

    if goal.completed and not was_completed:
        complete_result = await gamification.award(user, "goal_completed")
        points.append(f"+{complete_result.points_gained} meta concluída")

    await update.message.reply_text(
        _goal_card_text(goal, f"✅ Somei {_money(amount)} nessa meta.")
        + "\n\nPontos: "
        + " | ".join(points),
        parse_mode="Markdown",
    )
    return True


async def handle_goal_callback(update: Update, db: AsyncSession, user: User) -> bool:
    """Processa botões das metas."""
    query = update.callback_query
    data = query.data if query else ""
    prefixes = (GOAL_CALLBACK_ADD_PREFIX, GOAL_CALLBACK_DONE_PREFIX, GOAL_CALLBACK_REFRESH_PREFIX)
    if not query or not data.startswith(prefixes):
        return False

    if data.startswith(GOAL_CALLBACK_ADD_PREFIX):
        raw_id = data.replace(GOAL_CALLBACK_ADD_PREFIX, "", 1)
        try:
            goal_id = uuid.UUID(raw_id)
        except ValueError:
            await query.answer("Meta inválida")
            return True

        goal = await GoalRepository(db).get_active_by_id(user.id, goal_id)
        if not goal:
            await query.answer("Meta não encontrada")
            await query.edit_message_text("Essa meta não está mais ativa. Usa /metas para ver as atuais.")
            return True

        await UserRepository(db).update(
            user,
            current_flow="goal_progress",
            flow_step=f"goal_add:{goal_id}",
        )
        await query.answer("Pode mandar o valor")
        await query.edit_message_text(
            _goal_card_text(goal, "Quanto você quer adicionar? Manda um valor, tipo `50`."),
            parse_mode="Markdown",
        )
        return True

    if data.startswith(GOAL_CALLBACK_DONE_PREFIX):
        raw_id = data.replace(GOAL_CALLBACK_DONE_PREFIX, "", 1)
        try:
            goal_id = uuid.UUID(raw_id)
        except ValueError:
            await query.answer("Meta inválida")
            return True

        goal_repo = GoalRepository(db)
        goal = await goal_repo.get_active_by_id(user.id, goal_id)
        if not goal:
            await query.answer("Meta não encontrada")
            await query.edit_message_text("Essa meta não está mais ativa. Usa /metas para ver as atuais.")
            return True

        goal = await goal_repo.complete(goal)
        result = await GamificationEngine(UserRepository(db)).award(user, "goal_completed")
        await query.answer("Meta concluída")
        await query.edit_message_text(
            _goal_card_text(goal, "🎉 Meta concluída!")
            + f"\n\nVocê ganhou *+{result.points_gained} pontos*.",
            parse_mode="Markdown",
        )
        return True

    return False
