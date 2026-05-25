"""Gamification Engine — pontos, níveis e conquistas."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import date, timedelta
from app.models.user import User
from app.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

LEVELS = {
    1: {"name": "🌱 Aprendiz", "min_points": 0},
    2: {"name": "📚 Estudante", "min_points": 200},
    3: {"name": "💡 Consciente", "min_points": 500},
    4: {"name": "🚀 Investidor", "min_points": 1000},
    5: {"name": "🏆 Mestre", "min_points": 2000},
}

POINTS_MAP = {
    "onboarding_complete": 100,
    "first_entry_of_day": 10,
    "income_registered": 10,
    "positive_month_close": 50,
    "xlsx_export": 20,
    "challenge_easy": 50,
    "challenge_medium": 100,
    "challenge_hard": 150,
    "goal_created": 30,
    "goal_progress_updated": 20,
    "goal_completed": 50,
    "simulator_first_use": 30,
    "qa_question": 5,
    "seven_day_streak": 80,
    "learning_topic_viewed": 5,
    "learning_quiz_correct": 15,
    "learning_challenge_done": 25,
}

POINTS_ALIASES = {
    "streak_7days": "seven_day_streak",
    "quiz_correct": "qa_question",
}

LEVEL_UP_MESSAGES = {
    2: (
        "📚 Subiu para Estudante! Você já saiu do básico e está criando "
        "constância com seu dinheiro."
    ),
    3: (
        "💡 Agora você é Consciente! Suas escolhas financeiras já têm mais "
        "clareza e intenção."
    ),
    4: (
        "🚀 Nível Investidor desbloqueado! Hora de pensar em metas maiores "
        "e decisões com mais estratégia."
    ),
    5: (
        "🏆 Mestre financeiro! Você construiu uma rotina forte de atenção "
        "ao dinheiro."
    ),
}


@dataclass
class AwardResult:
    points_gained: int
    new_total: int
    old_level: int
    new_level: int
    level_name: str
    level_up_message: str | None
    leveled_up: bool


def get_level_name(level: int) -> str:
    return LEVELS.get(level, LEVELS[1])["name"]


def get_level_up_message(level: int) -> str:
    return LEVEL_UP_MESSAGES.get(
        level,
        f"🎊 Subiu de nível! Agora você é {get_level_name(level)}.",
    )


def points_to_next_level(current_points: int, current_level: int) -> int:
    """Retorna quantos pontos faltam para o próximo nível. 0 se já é nível 5."""
    if current_level >= 5:
        return 0
    next_min = LEVELS[current_level + 1]["min_points"]
    return max(0, next_min - current_points)


class GamificationEngine:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def award(self, user: User, action: str) -> AwardResult:
        """Concede pontos por uma ação e retorna o resultado."""
        canonical_action = POINTS_ALIASES.get(action, action)
        pts = POINTS_MAP.get(canonical_action, 0)
        if pts == 0:
            logger.warning(f"Ação desconhecida na gamificação: {action!r}")

        old_level = user.level
        updated_user = await self.user_repo.add_points(user, pts)
        new_level = updated_user.level

        return AwardResult(
            points_gained=pts,
            new_total=updated_user.points,
            old_level=old_level,
            new_level=new_level,
            level_name=get_level_name(new_level),
            level_up_message=get_level_up_message(new_level) if new_level > old_level else None,
            leveled_up=(new_level > old_level),
        )

    async def update_streak(self, user: User, today: date | None = None) -> int:
        """Atualiza streak diário de lançamentos e retorna o streak atual."""
        current = today or date.today()
        last_entry = user.last_entry_date
        current_streak = user.streak_days or 0

        if last_entry == current:
            return current_streak
        if last_entry == current - timedelta(days=1):
            streak_days = current_streak + 1
        else:
            streak_days = 1

        updated_user = await self.user_repo.update(
            user,
            last_entry_date=current,
            streak_days=streak_days,
        )
        return updated_user.streak_days
