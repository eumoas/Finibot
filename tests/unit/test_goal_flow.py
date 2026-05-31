"""Testes unitarios: metas financeiras."""
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

from app.flows.goal_flow import (
    _goal_card_text,
    _goal_keyboard,
    _parse_goal_text,
    _parse_money_input,
    looks_like_goal_intent,
)


def make_goal():
    goal = MagicMock()
    goal.id = uuid4()
    goal.title = "Comprar notebook"
    goal.current_amount = Decimal("200.00")
    goal.target_amount = Decimal("2500.00")
    goal.deadline = None
    goal.progress_bar = "[░░░░░░░░░░] 8%"
    return goal


def test_parse_money_input_accepts_decimal_comma():
    assert _parse_money_input("R$50,75") == Decimal("50.75")


def test_parse_money_input_rejects_zero():
    assert _parse_money_input("0") is None


def test_parse_goal_text_accepts_travel_goal_without_dash():
    assert _parse_goal_text("viajar com a galera 800") == (
        "viajar com a galera",
        Decimal("800.00"),
    )


def test_parse_goal_text_accepts_meta_command_without_dash():
    assert _parse_goal_text("/meta viajar com a galera R$800") == (
        "viajar com a galera",
        Decimal("800.00"),
    )


def test_parse_goal_text_accepts_young_informal_typing():
    assert _parse_goal_text("qro viajem c glr 800") == (
        "viagem com galera",
        Decimal("800.00"),
    )


def test_parse_goal_text_accepts_no_valor_de_format():
    assert _parse_goal_text("Comprar um tênis no valor de R$ 150") == (
        "Comprar um tênis",
        Decimal("150.00"),
    )


def test_looks_like_goal_intent_for_travel():
    assert looks_like_goal_intent("viajar com a galera 800")


def test_looks_like_goal_intent_accepts_common_typo():
    assert looks_like_goal_intent("qro viajem c glr 800")


def test_looks_like_goal_intent_does_not_steal_travel_expense():
    assert not looks_like_goal_intent("gastei R$300 em viagem com a galera")


def test_goal_card_text_shows_progress():
    goal = make_goal()

    text = _goal_card_text(goal)

    assert "Comprar notebook" in text
    assert "R$200,00 / R$2500,00" in text
    assert "8%" in text


def test_goal_keyboard_has_short_callback_data():
    goal = make_goal()

    keyboard = _goal_keyboard(goal)
    buttons = [button for row in keyboard.inline_keyboard for button in row]

    assert {button.text for button in buttons} == {"Adicionar valor", "Concluir"}
    assert all(len(button.callback_data) <= 64 for button in buttons)
