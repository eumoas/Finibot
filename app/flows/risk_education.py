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
        "Apostas e bets *não são um caminho financeiro saudável* — especialmente para jovens. "
        "As plataformas são projetadas para que a casa sempre ganhe no longo prazo, e o risco de "
        "perda é muito alto.\n\n"
        "Mais do que isso: apostar pode criar dependência. Se você sente que está perdendo o controle, "
        "procure ajuda numa *Unidade Básica de Saúde (UBS)* ou num *CAPS (Centro de Atenção Psicossocial)* "
        "perto de você — o atendimento é gratuito e sigiloso.\n\n"
        "Se quiser, posso te ajudar a traçar uma meta financeira de verdade. Isso sim funciona. 💪"
    )
