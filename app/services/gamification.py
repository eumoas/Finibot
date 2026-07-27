"""Gamification Engine — pontos, níveis e conquistas.

Critério de design: nenhuma mecânica do Fini pode operar por aversão à perda
ou por recompensa incerta. Pontos, níveis, constância e desafios só somam;
nada é retirado do usuário por inatividade.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import date
from app.models.user import User
from app.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

CONSTANCIA_MARCOS = (7, 15, 30, 60)

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
    "constancia_7_dias": 80,
    "constancia_15_dias": 120,
    "constancia_30_dias": 180,
    "constancia_60_dias": 250,
    "learning_topic_viewed": 5,
    "learning_quiz_correct": 15,
    "learning_challenge_done": 25,
}

POINTS_ALIASES = {
    "quiz_correct": "qa_question",
}

MARCO_ACTIONS = {
    7: "constancia_7_dias",
    15: "constancia_15_dias",
    30: "constancia_30_dias",
    60: "constancia_60_dias",
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


@dataclass
class ConstanciaResult:
    mes_atual: int
    total: int
    marcos_novos: list[int] = field(default_factory=list)


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

    async def update_constancia(self, user: User, today: date | None = None) -> ConstanciaResult:
        """Atualiza os contadores de constância e retorna o resultado.

        Os contadores só aumentam: não há reset por inatividade. A contagem
        mensal reinicia na virada do mês, mas o total acumulado nunca zera.
        Marcos (7/15/30/60 dias) são concedidos uma única vez e não se perdem.
        """
        current = today or date.today()
        last_entry = user.last_entry_date
        total = user.constancia_total or 0
        mes_atual = user.constancia_mes_atual or 0
        mes_referencia = user.constancia_mes_referencia
        marcos_atingidos = list(user.constancia_marcos_atingidos or [])

        if last_entry == current:
            return ConstanciaResult(mes_atual=mes_atual, total=total, marcos_novos=[])

        novo_total = total + 1
        mesmo_mes = mes_referencia is not None and (
            mes_referencia.year,
            mes_referencia.month,
        ) == (current.year, current.month)
        novo_mes_atual = mes_atual + 1 if mesmo_mes else 1

        marcos_novos = [
            marco
            for marco in CONSTANCIA_MARCOS
            if novo_total >= marco and marco not in marcos_atingidos
        ]
        novos_marcos_atingidos = marcos_atingidos + marcos_novos

        updated_user = await self.user_repo.update(
            user,
            last_entry_date=current,
            constancia_total=novo_total,
            constancia_mes_atual=novo_mes_atual,
            constancia_mes_referencia=current.replace(day=1),
            constancia_marcos_atingidos=novos_marcos_atingidos,
        )
        return ConstanciaResult(
            mes_atual=updated_user.constancia_mes_atual,
            total=updated_user.constancia_total,
            marcos_novos=marcos_novos,
        )
