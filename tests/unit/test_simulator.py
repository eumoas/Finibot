"""Testes unitarios: simulador financeiro."""
from decimal import Decimal

from app.flows.simulator import (
    build_simulation_response,
    looks_like_simulation_intent,
    parse_simulation_input,
)


def test_simulator_intent_accepts_typo():
    assert looks_like_simulation_intent("se eu guarrdar 50 reais em 12 meses")


def test_parse_simulation_input_monthly_amount_and_months():
    parsed = parse_simulation_input("se eu guarrdar 50 reais em 12 meses")

    assert parsed.amount == Decimal("50.00")
    assert parsed.months == 12
    assert parsed.frequency == "monthly"


def test_parse_simulation_input_years():
    parsed = parse_simulation_input("guardar R$50 por mes por 1 ano")

    assert parsed.amount == Decimal("50.00")
    assert parsed.months == 12


def test_build_simulation_response_has_no_technical_error():
    parsed = parse_simulation_input("se eu guardar 50 reais em 12 meses")

    response = build_simulation_response(parsed)

    assert "problema" not in response.lower()
    assert "R$50,00" in response
    assert "12 meses" in response
    assert "Tesouro Selic" in response
