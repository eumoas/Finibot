"""Seed dos desafios D01-D20 do spec v2."""
from sqlalchemy import or_, select
from app.models.challenge import Challenge

CHALLENGES = [
    {
        "code": "D01",
        "title": "Gastos de Hoje",
        "description": "Anote todos os gastos de hoje, por menor que sejam. Qual foi o maior?",
        "points_reward": 50,
        "category": "registro",
        "difficulty": "facil",
    },
    {
        "code": "D02",
        "title": "Maior Categoria",
        "description": "Olhe o resumo do mês e identifique a categoria onde você mais gastou.",
        "points_reward": 50,
        "category": "registro",
        "difficulty": "facil",
    },
    {
        "code": "D03",
        "title": "Últimos 3 Dias",
        "description": "Registre todos os lançamentos dos últimos 3 dias (pode reconstruir da memória).",
        "points_reward": 50,
        "category": "registro",
        "difficulty": "facil",
    },
    {
        "code": "D04",
        "title": "Gasto Repensado",
        "description": "Encontre 1 gasto do mês que, pensando agora, você não faria de novo.",
        "points_reward": 50,
        "category": "reflexao",
        "difficulty": "facil",
    },
    {
        "code": "D05",
        "title": "Saldo do Mês",
        "description": "Envie /resumo e me diga: seu saldo ficou positivo ou negativo? Por quê?",
        "points_reward": 50,
        "category": "resumo",
        "difficulty": "facil",
    },
    {
        "code": "D06",
        "title": "Meta de 3 Meses",
        "description": "Defina 1 meta financeira para os próximos 3 meses usando /meta.",
        "points_reward": 100,
        "category": "metas",
        "difficulty": "medio",
    },
    {
        "code": "D07",
        "title": "Alimentação Fora",
        "description": "Passe uma semana registrando TODOS os gastos com alimentação fora de casa.",
        "points_reward": 100,
        "category": "registro",
        "difficulty": "medio",
    },
    {
        "code": "D08",
        "title": "Assinatura Pouco Usada",
        "description": "Identifique uma assinatura que você paga mas usa pouco. Vale manter?",
        "points_reward": 100,
        "category": "assinaturas",
        "difficulty": "medio",
    },
    {
        "code": "D09",
        "title": "Transporte e Renda",
        "description": "Calcule: quanto você gasta por mês em transporte? É proporcional à sua renda?",
        "points_reward": 100,
        "category": "registro",
        "difficulty": "medio",
    },
    {
        "code": "D10",
        "title": "Gastos Recorrentes",
        "description": "Liste 3 gastos recorrentes seus. Qual deles você poderia reduzir sem perder qualidade de vida?",
        "points_reward": 100,
        "category": "planejamento",
        "difficulty": "medio",
    },
    {
        "code": "D11",
        "title": "Lazer em 2 Meses",
        "description": "Compare seus gastos de lazer dos últimos 2 meses. Aumentou ou diminuiu? Por quê?",
        "points_reward": 100,
        "category": "comparacao",
        "difficulty": "medio",
    },
    {
        "code": "D12",
        "title": "Simulação de 10%",
        "description": "Use /simular para descobrir quanto teria ao final de 6 meses guardando 10% da sua renda.",
        "points_reward": 100,
        "category": "simulador",
        "difficulty": "medio",
    },
    {
        "code": "D13",
        "title": "7 Dias Sem Impulso",
        "description": "Passe 7 dias sem comprar nada por impulso. Registre tudo que quis mas não comprou.",
        "points_reward": 150,
        "category": "comportamento",
        "difficulty": "dificil",
    },
    {
        "code": "D14",
        "title": "Regra das 24h",
        "description": "Durante 1 semana, antes de qualquer compra acima de R$30, espere 24h e só compre se ainda quiser.",
        "points_reward": 150,
        "category": "comportamento",
        "difficulty": "dificil",
    },
    {
        "code": "D15",
        "title": "Plano de Economia",
        "description": "Crie um plano de economia para os próximos 2 meses com meta, valor mensal e o que pretende cortar.",
        "points_reward": 150,
        "category": "planejamento",
        "difficulty": "dificil",
    },
    {
        "code": "D16",
        "title": "Pesquisa em 3 Lugares",
        "description": "Pesquise o preço de algo que quer comprar em 3 lugares diferentes antes de decidir.",
        "points_reward": 150,
        "category": "consumo",
        "difficulty": "dificil",
    },
    {
        "code": "D17",
        "title": "Custou Mais Caro",
        "description": 'Calcule quanto você gastou com algo que "só ia custar R$X" mas acabou saindo mais caro.',
        "points_reward": 150,
        "category": "reflexao",
        "difficulty": "dificil",
    },
    {
        "code": "D18",
        "title": "Renda Extra",
        "description": "Encontre uma forma de gerar renda extra (mesmo que pequena) esse mês. Registre quando chegar.",
        "points_reward": 150,
        "category": "renda",
        "difficulty": "dificil",
    },
    {
        "code": "D19",
        "title": "Gasto em Horas",
        "description": 'Converta seu maior gasto do mês para horas de trabalho: "quantas horas eu trabalhei pra pagar isso?"',
        "points_reward": 150,
        "category": "reflexao",
        "difficulty": "dificil",
    },
    {
        "code": "D20",
        "title": "Mês Positivo",
        "description": "Feche o mês com saldo positivo. Use /resumo para acompanhar ao longo do mês.",
        "points_reward": 150,
        "category": "resumo",
        "difficulty": "dificil",
    },
]


async def seed_challenges(db):
    """Insere/atualiza D01-D20 e desativa desafios antigos."""
    codes = {item["code"] for item in CHALLENGES}

    for data in CHALLENGES:
        result = await db.execute(select(Challenge).where(Challenge.code == data["code"]))
        challenge = result.scalar_one_or_none()
        if challenge:
            for key, value in data.items():
                setattr(challenge, key, value)
            challenge.active = True
        else:
            db.add(Challenge(**data, active=True))

    result = await db.execute(
        select(Challenge).where(or_(Challenge.code.is_(None), Challenge.code.notin_(codes)))
    )
    for challenge in result.scalars():
        challenge.active = False

    await db.commit()
    print(f"✅ {len(CHALLENGES)} desafios D01-D20 sincronizados")
