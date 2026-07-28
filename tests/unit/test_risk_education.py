"""Testes unitários: educação de risco financeiro."""
from app.flows.risk_education import betting_education_response, is_betting_topic


def test_detects_betting_topic():
    assert is_betting_topic("eu queria jogar em bets")
    assert is_betting_topic("aposta no tigrinho vale a pena?")


def test_betting_response_is_educational():
    response = betting_education_response()

    assert "risco" in response.lower()
    assert "não são um caminho financeiro saudável" in response.lower()
    assert "caps" in response.lower()
    assert "ubs" in response.lower()
