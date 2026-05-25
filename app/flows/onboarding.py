"""Flow de Onboarding — máquina de estado para novos usuários."""
import logging
from decimal import Decimal, InvalidOperation
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.services.gamification import GamificationEngine
from app.prompts import templates

logger = logging.getLogger(__name__)

# Perfis baseados no quiz
QUIZ_PROFILES = {
    # (q1, q2, q3) → profile_type
    ("A", "C", "C"): "iniciante",
    ("A", "B", "C"): "iniciante",
    ("C", "C", "C"): "iniciante",
    ("B", "A", "A"): "avancado",
    ("B", "A", "B"): "em_desenvolvimento",
}

PROFILE_DESCRIPTIONS = {
    "iniciante": "🌱 *Iniciante Financeiro* — Você está começando a jornada. Perfeito, todo mundo começa do zero!",
    "em_desenvolvimento": "📈 *Em Desenvolvimento* — Você já sabe o básico. Agora é hora de aprofundar!",
    "avancado": "🚀 *Perfil Avançado* — Você já pensa em finanças! Vamos explorar coisas mais elaboradas?",
}

INCOME_SOURCE_BUTTONS = [
    [InlineKeyboardButton("Mesada", callback_data="onb_income_mesada")],
    [InlineKeyboardButton("Estágio", callback_data="onb_income_estagio")],
    [InlineKeyboardButton("Freelas", callback_data="onb_income_freelas")],
    [InlineKeyboardButton("Trabalho", callback_data="onb_income_trabalho")],
    [InlineKeyboardButton("Outros", callback_data="onb_income_outros")],
]

INCOME_SOURCE_LABELS = {
    "mesada": "Mesada",
    "estagio": "Estágio",
    "freelas": "Freelas",
    "trabalho": "Trabalho",
    "outros": "Outros",
}

QUIZ_Q1_BUTTONS = [
    [InlineKeyboardButton("💸 Gasto logo", callback_data="onb_q1_A")],
    [InlineKeyboardButton("🏦 Guardo uma parte primeiro", callback_data="onb_q1_B")],
    [InlineKeyboardButton("🤷 Depende do mês", callback_data="onb_q1_C")],
]

QUIZ_Q2_BUTTONS = [
    [InlineKeyboardButton("✅ Sim, entendo como funciona", callback_data="onb_q2_A")],
    [InlineKeyboardButton("🤔 Já ouvi, mas não sei direito", callback_data="onb_q2_B")],
    [InlineKeyboardButton("❌ Nunca ouvi esse nome", callback_data="onb_q2_C")],
]

QUIZ_Q3_BUTTONS = [
    [InlineKeyboardButton("🎯 Sim, sei o que quero", callback_data="onb_q3_A")],
    [InlineKeyboardButton("💭 Quero ter, mas não sei como", callback_data="onb_q3_B")],
    [InlineKeyboardButton("😶 Não pensei nisso ainda", callback_data="onb_q3_C")],
]


def _parse_money(text: str) -> Decimal | None:
    clean = (
        text.strip()
        .lower()
        .replace("r$", "")
        .replace("reais", "")
        .replace("real", "")
        .replace(" ", "")
    )
    if "," in clean and "." in clean:
        clean = clean.replace(".", "").replace(",", ".")
    else:
        clean = clean.replace(",", ".")
    try:
        value = Decimal(clean)
    except (InvalidOperation, ValueError):
        return None
    return value if value >= 0 else None


async def start_onboarding(update: Update, db: AsyncSession):
    """Inicia o onboarding para novos usuários."""
    user_repo = UserRepository(db)
    tg_user = update.effective_user
    user, _ = await user_repo.get_or_create(
        telegram_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
    )
    await user_repo.update(user, current_flow="onboarding", flow_step="ask_name")
    await update.message.reply_text(templates.WELCOME_NEW, parse_mode="Markdown")


async def handle_onboarding_step(
    update: Update, db: AsyncSession, user_step: str, user
) -> bool:
    """
    Processa cada passo do onboarding.
    Retorna True se o fluxo está completo, False se ainda está em andamento.
    """
    user_repo = UserRepository(db)
    text = (update.message.text if update.message else "").strip()

    if user_step == "ask_name":
        name = text[:100] if text else user.first_name or "amigo"
        await user_repo.update(user, first_name=name, flow_step="ask_age")
        await update.message.reply_text(
            templates.ONBOARDING_ASK_AGE(name), parse_mode="Markdown"
        )
        return False

    if user_step == "ask_age":
        try:
            age = int(text)
            if age < 10:
                await update.message.reply_text(
                    templates.ONBOARDING_TOO_YOUNG, parse_mode="Markdown"
                )
                await user_repo.update(user, age=age, flow_step="ask_age")
                return False
        except ValueError:
            age = None

        await user_repo.update(user, age=age, flow_step="ask_income_source")
        await update.message.reply_text(
            templates.ONBOARDING_ASK_INCOME_SOURCE,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(INCOME_SOURCE_BUTTONS),
        )
        return False

    if user_step == "ask_income_source":
        await update.message.reply_text(
            "Escolhe uma das opções acima pra eu entender sua fonte de renda principal.",
        )
        return False

    if user_step == "ask_monthly_income":
        monthly_income = _parse_money(text)
        if monthly_income is None:
            await update.message.reply_text(
                templates.ONBOARDING_INVALID_INCOME,
                parse_mode="Markdown",
            )
            return False

        await user_repo.update(user, monthly_income=monthly_income, flow_step="quiz_q1")
        await update.message.reply_text(
            templates.ONBOARDING_ASK_Q1,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(QUIZ_Q1_BUTTONS),
        )
        return False
    # Passos de quiz — o usuário precisa clicar nos botões
    if user_step.startswith("quiz_"):
        await update.message.reply_text(
            "👆 Clica em uma das opções acima pra responder! 😊",
        )
        return False

    return False  # outros passos são tratados por callback_query


async def handle_quiz_callback(
    update: Update, db: AsyncSession, user, data: str
) -> bool:
    """Processa respostas do quiz via InlineKeyboard. Retorna True ao finalizar."""
    query = update.callback_query
    await query.answer()

    user_repo = UserRepository(db)
    gamification = GamificationEngine(user_repo)

    if data.startswith("onb_income_"):
        source_key = data.replace("onb_income_", "", 1)
        source = INCOME_SOURCE_LABELS.get(source_key, "Outros")
        await user_repo.update(
            user,
            income_source=source,
            flow_step="ask_monthly_income",
        )
        await query.edit_message_text(
            templates.ONBOARDING_ASK_MONTHLY_INCOME(source),
            parse_mode="Markdown",
        )
        return False

    # data: "onb_q1_A", "onb_q2_B", etc.
    parts = data.split("_")  # ["onb", "q1", "A"]
    question, answer = parts[1], parts[2]

    # Salva resposta no flow_step temporariamente
    current_answers = {}
    if user.flow_step and "|" in user.flow_step:
        for pair in user.flow_step.split("|"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                current_answers[k] = v
    current_answers[question] = answer

    if question == "q1":
        step_data = "|".join(f"{k}={v}" for k, v in current_answers.items())
        await user_repo.update(user, flow_step=f"quiz_q2|{step_data}")
        await query.edit_message_text(
            templates.ONBOARDING_ASK_Q2,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(QUIZ_Q2_BUTTONS),
        )
        return False

    if question == "q2":
        step_data = "|".join(f"{k}={v}" for k, v in current_answers.items())
        await user_repo.update(user, flow_step=f"quiz_q3|{step_data}")
        await query.edit_message_text(
            templates.ONBOARDING_ASK_Q3,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(QUIZ_Q3_BUTTONS),
        )
        return False

    if question == "q3":
        # Quiz completo — determina perfil
        q1 = current_answers.get("q1", "C")
        q2 = current_answers.get("q2", "C")
        q3 = current_answers.get("q3", "C")
        profile = QUIZ_PROFILES.get((q1, q2, q3), "iniciante")

        result = await gamification.award(user, "onboarding_complete")
        await user_repo.update(
            user,
            profile_type=profile,
            onboarded=True,
            current_flow=None,
            flow_step=None,
        )

        profile_desc = PROFILE_DESCRIPTIONS.get(profile, PROFILE_DESCRIPTIONS["iniciante"])
        completion_msg = (
            templates.ONBOARDING_COMPLETE(
                user.first_name or "amigo", profile_desc, result.points_gained
            )
        )
        await query.edit_message_text(completion_msg, parse_mode="Markdown")
        return True

    return False
