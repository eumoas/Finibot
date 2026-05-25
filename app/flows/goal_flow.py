"""Flow de Metas Financeiras — criar, listar e atualizar progresso."""
import logging
from telegram import Update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
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

    lines = ["🎯 *Suas Metas Ativas:*\n"]
    for i, g in enumerate(goals, 1):
        deadline_str = g.deadline.strftime("%d/%m/%Y") if g.deadline else "sem prazo"
        lines.append(
            f"*{i}. {g.title}*\n"
            f"   R${float(g.current_amount):.2f} / R${float(g.target_amount):.2f}\n"
            f"   {g.progress_bar} | Prazo: {deadline_str}\n"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_create_goal_command(update: Update, db: AsyncSession, user: User):
    """Instrui o usuário sobre como criar uma meta."""
    await update.message.reply_text(CREATE_GOAL_HELP, parse_mode="Markdown")


async def parse_and_create_goal(
    update: Update, db: AsyncSession, user: User, text: str
) -> bool:
    """
    Tenta parsear uma meta do texto livre.
    Formato esperado: 'Título - R$Valor'
    Retorna True se criou a meta, False se não reconheceu o padrão.
    """
    import re

    pattern = r"(.+?)\s*[-–]\s*[Rr]\$?\s*([\d.,]+)"
    match = re.search(pattern, text)
    if not match:
        return False

    title = match.group(1).strip()[:200]
    amount_str = match.group(2).replace(",", ".")
    try:
        amount = float(amount_str)
    except ValueError:
        return False

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

    goal = await goal_repo.create(user.id, title, amount)
    result = await gamification.award(user, "goal_created")

    await update.message.reply_text(
        f"✅ *Meta criada!*\n\n"
        f"🎯 {goal.title}\n"
        f"💰 Objetivo: R${amount:.2f}\n\n"
        f"Você ganhou *+{result.points_gained} pontos*! "
        f"Use /metas para acompanhar. 🚀",
        parse_mode="Markdown",
    )
    return True
