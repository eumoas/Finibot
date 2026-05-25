"""Testes unitários: system prompt."""
from app.prompts.system_prompt import build_system_prompt, DEFAULT_SYSTEM_PROMPT
from unittest.mock import MagicMock


def make_user(name="Lucas", level=1, points=100, profile="iniciante"):
    user = MagicMock()
    user.first_name = name
    user.level = level
    user.points = points
    user.profile_type = profile
    user.monthly_income = None
    user.income_source = None
    return user


def test_system_prompt_contains_username():
    user = make_user(name="Ana")
    prompt = build_system_prompt(user)
    assert "Ana" in prompt


def test_system_prompt_contains_level():
    user = make_user(level=3, points=500)
    prompt = build_system_prompt(user)
    assert "Consciente" in prompt  # nome do nível 3
    assert "500" in prompt


def test_system_prompt_no_forbidden_terms():
    """O system prompt deve instruir o bot a NÃO usar jargão bancário."""
    user = make_user()
    prompt = build_system_prompt(user)
    # O prompt menciona esses termos como exemplos do que NÃO usar,
    # então verificamos que eles aparecem em contexto de proibição
    assert "NUNCA use" in prompt or "nunca use" in prompt.lower()
    forbidden = ["hedge", "portfólio", "alavancagem"]
    for term in forbidden:
        assert term in prompt.lower(), f"Termo proibido deveria estar listado nas regras: {term}"


def test_system_prompt_has_rules():
    user = make_user()
    prompt = build_system_prompt(user)
    assert "150 palavras" in prompt
    assert "emojis" in prompt.lower()
    assert "exemplos com valores em reais" in prompt.lower()


def test_default_prompt_not_empty():
    assert len(DEFAULT_SYSTEM_PROMPT) > 50
