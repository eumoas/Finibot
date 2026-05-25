"""Testes unitários: módulo Aprender BNCC."""
from decimal import Decimal
from unittest.mock import MagicMock

from app.content.bncc_learning import LEARNING_TOPICS, get_topic
from app.flows.learning_flow import parse_learning_callback, render_learning_card


def test_learning_topics_l01_to_l09_exist():
    codes = [topic.code for topic in LEARNING_TOPICS]

    assert codes == [f"L{number:02d}" for number in range(1, 10)]
    assert len({topic.slug for topic in LEARNING_TOPICS}) == 9


def test_each_topic_has_valid_quiz_answer():
    for topic in LEARNING_TOPICS:
        assert topic.correct_option in topic.quiz_options
        assert topic.mini_challenge
        assert topic.related_commands


def test_parse_learning_callbacks():
    assert parse_learning_callback("learn_menu") == ("menu", None, None)
    assert parse_learning_callback("learn_topic:saldo") == ("topic", "saldo", None)
    assert parse_learning_callback("learn_quiz:saldo:A") == ("quiz", "saldo", "A")
    assert parse_learning_callback("learn_challenge:saldo") == ("challenge", "saldo", None)


def test_render_learning_card_uses_month_summary_for_percentage():
    user = MagicMock()
    user.monthly_income = Decimal("500")
    topic = get_topic("porcentagem")
    summary = {
        "top_category": "Alimentação",
        "by_category": {"Alimentação": Decimal("150")},
    }

    card = render_learning_card(topic, summary=summary, user=user)

    assert "Alimentação" in card
    assert "30%" in card


def test_bets_topic_is_present():
    topic = get_topic("bets-apostas")

    assert topic is not None
    assert "risco" in topic.content.lower()
