"""Respostas educativas locais para temas financeiros de risco."""
from __future__ import annotations

import re

BETTING_PATTERNS = [
    r"\bbet(s)?\b",
    r"\baposta(s|r|ndo)?\b",
    r"\bapostei\b",
    r"\bjogo do tigrinho\b",
    r"\btigrinho\b",
    r"\bcassino\b",
    r"\bblaze\b",
    r"\broleta\b",
]


def is_betting_topic(text: str) -> bool:
    normalized = text.lower()
    return any(re.search(pattern, normalized) for pattern in BETTING_PATTERNS)


def betting_education_response() -> str:
    return (
        "Entendo a vontade, principalmente quando parece uma chance de ganhar dinheiro rápido. "
        "Mas bets têm risco alto e podem virar perda recorrente.\n\n"
        "Antes de apostar, combina 3 regras: nunca use dinheiro de conta, comida, transporte ou meta; "
        "defina um limite pequeno que você aceita perder; e se a ideia for recuperar prejuízo, pare ali.\n\n"
        "Mini-desafio: quer comparar esse valor guardado por 30 dias em vez de apostado?"
    )
