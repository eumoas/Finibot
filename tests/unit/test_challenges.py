"""Testes unitários: desafios D01-D20."""
from app.db.seed_challenges import CHALLENGES


def test_seed_has_d01_to_d20_codes():
    codes = [challenge["code"] for challenge in CHALLENGES]

    assert len(codes) == 20
    assert codes == [f"D{number:02d}" for number in range(1, 21)]
    assert len(set(codes)) == 20


def test_challenge_points_match_difficulty():
    expected_points = {"facil": 50, "medio": 100, "dificil": 150}

    for challenge in CHALLENGES:
        assert challenge["points_reward"] == expected_points[challenge["difficulty"]]


def test_challenges_focus_on_financial_registration():
    descriptions = " ".join(challenge["description"].lower() for challenge in CHALLENGES)

    assert "registre" in descriptions or "anote" in descriptions
    assert "/resumo" in descriptions
