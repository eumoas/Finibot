"""Testes unitários: Gamification Engine."""
import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from app.services.gamification import (
    GamificationEngine,
    LEVELS,
    LEVEL_UP_MESSAGES,
    POINTS_MAP,
    get_level_name,
    get_level_up_message,
    points_to_next_level,
)


def make_user(points=0, level=1):
    user = MagicMock()
    user.points = points
    user.level = level
    user.last_entry_date = None
    user.constancia_total = 0
    user.constancia_mes_atual = 0
    user.constancia_mes_referencia = None
    user.constancia_marcos_atingidos = []
    return user


@pytest.mark.asyncio
async def test_award_onboarding_complete():
    """Onboarding deve conceder 100 pontos."""
    user = make_user(points=0, level=1)
    user_repo = AsyncMock()
    updated_user = make_user(points=100, level=1)
    user_repo.add_points.return_value = updated_user

    engine = GamificationEngine(user_repo)
    result = await engine.award(user, "onboarding_complete")

    assert result.points_gained == 100
    assert result.new_total == 100
    assert not result.leveled_up
    user_repo.add_points.assert_called_once_with(user, 100)


@pytest.mark.asyncio
async def test_award_level_up():
    """Deve detectar subida de nível."""
    user = make_user(points=190, level=1)
    user_repo = AsyncMock()
    updated_user = make_user(points=210, level=2)
    user_repo.add_points.return_value = updated_user

    engine = GamificationEngine(user_repo)
    result = await engine.award(user, "onboarding_complete")

    assert result.leveled_up
    assert result.new_level == 2
    assert result.level_name == LEVELS[2]["name"]
    assert result.level_up_message == LEVEL_UP_MESSAGES[2]


@pytest.mark.asyncio
async def test_award_unknown_action():
    """Ação desconhecida deve conceder 0 pontos."""
    user = make_user(points=100, level=1)
    user_repo = AsyncMock()
    updated_user = make_user(points=100, level=1)
    user_repo.add_points.return_value = updated_user

    engine = GamificationEngine(user_repo)
    result = await engine.award(user, "acao_inexistente")

    assert result.points_gained == 0


def test_points_to_next_level():
    assert points_to_next_level(0, 1) == 200
    assert points_to_next_level(100, 1) == 100
    assert points_to_next_level(200, 2) == 300
    assert points_to_next_level(2000, 5) == 0  # nível máximo


def test_get_level_name():
    assert "Aprendiz" in get_level_name(1)
    assert "Mestre" in get_level_name(5)


def test_get_level_up_message():
    assert "Estudante" in get_level_up_message(2)
    assert "Mestre" in get_level_up_message(5)


def test_points_map_has_expected_actions():
    assert len(POINTS_MAP) == 20
    for action in [
        "first_entry_of_day",
        "income_registered",
        "positive_month_close",
        "xlsx_export",
        "goal_progress_updated",
        "goal_completed",
        "simulator_first_use",
        "qa_question",
        "constancia_7_dias",
        "constancia_15_dias",
        "constancia_30_dias",
        "constancia_60_dias",
        "learning_topic_viewed",
        "learning_quiz_correct",
        "learning_challenge_done",
    ]:
        assert action in POINTS_MAP


@pytest.mark.asyncio
async def test_update_constancia_first_entry():
    user = make_user()
    user_repo = AsyncMock()
    updated_user = make_user()
    updated_user.constancia_total = 1
    updated_user.constancia_mes_atual = 1
    user_repo.update.return_value = updated_user

    engine = GamificationEngine(user_repo)
    result = await engine.update_constancia(user, today=date(2026, 5, 24))

    assert result.total == 1
    assert result.mes_atual == 1
    assert result.marcos_novos == []
    user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_constancia_same_day_does_not_update():
    user = make_user()
    user.last_entry_date = date(2026, 5, 24)
    user.constancia_total = 3
    user.constancia_mes_atual = 3
    user_repo = AsyncMock()

    engine = GamificationEngine(user_repo)
    result = await engine.update_constancia(user, today=date(2026, 5, 24))

    assert result.total == 3
    assert result.mes_atual == 3
    user_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_constancia_never_decreases_after_gap():
    """Uma lacuna de vários dias sem registro não zera a constância."""
    user = make_user()
    user.last_entry_date = date(2026, 5, 1)
    user.constancia_total = 6
    user.constancia_mes_atual = 6
    user.constancia_mes_referencia = date(2026, 5, 1)
    user_repo = AsyncMock()
    updated_user = make_user()
    updated_user.constancia_total = 7
    updated_user.constancia_mes_atual = 7
    user_repo.update.return_value = updated_user

    engine = GamificationEngine(user_repo)
    result = await engine.update_constancia(user, today=date(2026, 5, 20))

    assert result.total == 7
    assert result.marcos_novos == [7]
    _, kwargs = user_repo.update.call_args
    assert kwargs["constancia_total"] == 7
    assert kwargs["constancia_mes_atual"] == 7


@pytest.mark.asyncio
async def test_update_constancia_resets_only_monthly_counter_on_new_month():
    user = make_user()
    user.last_entry_date = date(2026, 5, 30)
    user.constancia_total = 10
    user.constancia_mes_atual = 10
    user.constancia_mes_referencia = date(2026, 5, 1)
    user_repo = AsyncMock()
    updated_user = make_user()
    updated_user.constancia_total = 11
    updated_user.constancia_mes_atual = 1
    user_repo.update.return_value = updated_user

    engine = GamificationEngine(user_repo)
    result = await engine.update_constancia(user, today=date(2026, 6, 1))

    assert result.total == 11
    assert result.mes_atual == 1
    _, kwargs = user_repo.update.call_args
    assert kwargs["constancia_total"] == 11
    assert kwargs["constancia_mes_atual"] == 1


@pytest.mark.asyncio
async def test_update_constancia_does_not_regrant_achieved_marco():
    user = make_user()
    user.last_entry_date = date(2026, 5, 6)
    user.constancia_total = 7
    user.constancia_mes_atual = 7
    user.constancia_mes_referencia = date(2026, 5, 1)
    user.constancia_marcos_atingidos = [7]
    user_repo = AsyncMock()
    updated_user = make_user()
    updated_user.constancia_total = 8
    user_repo.update.return_value = updated_user

    engine = GamificationEngine(user_repo)
    result = await engine.update_constancia(user, today=date(2026, 5, 7))

    assert result.marcos_novos == []
    _, kwargs = user_repo.update.call_args
    assert kwargs["constancia_marcos_atingidos"] == [7]


def test_all_levels_defined():
    """Todos os 5 níveis devem estar definidos."""
    assert len(LEVELS) == 5
    for level_num, data in LEVELS.items():
        assert "name" in data
        assert "min_points" in data
