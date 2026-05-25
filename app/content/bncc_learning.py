"""Cards educativos de educação financeira alinhados à BNCC."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LearningTopic:
    code: str
    slug: str
    title: str
    bncc_focus: str
    content: str
    example: str
    quiz_question: str
    quiz_options: dict[str, str]
    correct_option: str
    feedback_correct: str
    feedback_wrong: str
    mini_challenge: str
    related_commands: tuple[str, ...]


LEARNING_TOPICS = [
    LearningTopic(
        code="L01",
        slug="receita-despesa",
        title="Receita e despesa",
        bncc_focus="Operações com números racionais, organização de dados e tomada de decisão.",
        content="Receita é dinheiro que entra. Despesa é dinheiro que sai. Separar os dois ajuda a entender seu mês sem chute.",
        example="Se você recebe R$300 de mesada e gasta R$18,50 no lanche, teve uma receita de R$300 e uma despesa de R$18,50.",
        quiz_question="Qual frase descreve uma despesa?",
        quiz_options={"A": "Recebi R$100 de mesada", "B": "Paguei R$12 no transporte", "C": "Meu saldo ficou positivo"},
        correct_option="B",
        feedback_correct="Isso! Despesa é saída de dinheiro.",
        feedback_wrong="Quase. Despesa é quando o dinheiro sai, como pagar transporte, lanche ou assinatura.",
        mini_challenge="Registre uma receita e um gasto hoje. Pode ser aproximado.",
        related_commands=("/receita", "/gasto", "/gastos"),
    ),
    LearningTopic(
        code="L02",
        slug="saldo",
        title="Saldo",
        bncc_focus="Cálculo de diferença, interpretação de resultados e análise de dados pessoais.",
        content="Saldo é o que sobra depois de comparar entradas e saídas. Saldo positivo indica que entrou mais do que saiu.",
        example="Se entraram R$300 e saíram R$80, o saldo é R$220.",
        quiz_question="Se você recebeu R$200 e gastou R$75, qual é o saldo?",
        quiz_options={"A": "R$125", "B": "R$275", "C": "R$75"},
        correct_option="A",
        feedback_correct="Boa! R$200 - R$75 = R$125.",
        feedback_wrong="O saldo é entrada menos saída. Nesse caso: R$200 - R$75 = R$125.",
        mini_challenge="Use /resumo e veja se seu saldo do mês está positivo ou negativo.",
        related_commands=("/resumo",),
    ),
    LearningTopic(
        code="L03",
        slug="porcentagem",
        title="Porcentagem",
        bncc_focus="Razão, proporção, porcentagens, comparação e leitura de dados.",
        content="Porcentagem mostra uma parte de um todo. Em finanças, ajuda a ver quanto uma categoria pesa na renda.",
        example="10% de R$500 é R$50. Se alimentação deu R$150, isso representa 30% de R$500.",
        quiz_question="Quanto é 10% de R$300?",
        quiz_options={"A": "R$3", "B": "R$30", "C": "R$300"},
        correct_option="B",
        feedback_correct="Exato. 10% é dividir por 10: R$300 vira R$30.",
        feedback_wrong="10% é uma parte em dez. R$300 dividido por 10 dá R$30.",
        mini_challenge="Abra /resumo e descubra qual categoria mais pesa na sua renda.",
        related_commands=("/resumo",),
    ),
    LearningTopic(
        code="L04",
        slug="juros-simples",
        title="Juros simples",
        bncc_focus="Porcentagem aplicada, acréscimos e resolução de problemas financeiros.",
        content="Juros simples crescem sempre sobre o valor inicial. É uma forma direta de calcular acréscimos.",
        example="R$100 com 10% de juros simples por mês vira R$110 em 1 mês e R$120 em 2 meses.",
        quiz_question="R$100 com 10% de juros simples por 1 mês vira quanto?",
        quiz_options={"A": "R$101", "B": "R$110", "C": "R$200"},
        correct_option="B",
        feedback_correct="Isso. 10% de R$100 é R$10, então vira R$110.",
        feedback_wrong="10% de R$100 é R$10. Somando ao inicial: R$110.",
        mini_challenge="Use /simular para comparar guardar dinheiro agora ou deixar para depois.",
        related_commands=("/simular",),
    ),
    LearningTopic(
        code="L05",
        slug="juros-compostos",
        title="Juros compostos",
        bncc_focus="Crescimento acumulado, progressões e comparação de cenários.",
        content="Juros compostos são juros sobre juros. Com o tempo, o crescimento acelera.",
        example="R$100 rendendo 10% vira R$110. Depois, 10% sobre R$110 vira R$121.",
        quiz_question="Nos juros compostos, o segundo rendimento calcula sobre qual valor?",
        quiz_options={"A": "Só o valor inicial", "B": "O valor atualizado", "C": "Zero"},
        correct_option="B",
        feedback_correct="Perfeito. O cálculo usa o valor atualizado.",
        feedback_wrong="Nos compostos, cada rodada usa o valor atualizado, por isso cresce mais rápido.",
        mini_challenge="Simule guardar 10% da sua renda por 6 meses.",
        related_commands=("/simular",),
    ),
    LearningTopic(
        code="L06",
        slug="metas",
        title="Metas financeiras",
        bncc_focus="Planejamento, estimativas, divisão proporcional e projeto de vida.",
        content="Meta financeira é transformar um desejo em plano: valor, prazo e quanto guardar por mês.",
        example="Se um curso custa R$240 e você tem 3 meses, precisa guardar R$80 por mês.",
        quiz_question="O que uma boa meta precisa ter?",
        quiz_options={"A": "Valor e prazo", "B": "Só vontade", "C": "Só desconto"},
        correct_option="A",
        feedback_correct="Isso. Valor e prazo transformam desejo em plano.",
        feedback_wrong="Uma meta fica prática quando tem valor e prazo.",
        mini_challenge="Crie uma meta pequena para os próximos 3 meses.",
        related_commands=("/meta", "/metas"),
    ),
    LearningTopic(
        code="L07",
        slug="planejamento",
        title="Planejamento mensal",
        bncc_focus="Organização de dados, previsão, comparação e tomada de decisão.",
        content="Planejar é decidir antes para o dinheiro não sumir sem explicação. Comece separando essenciais, desejos e metas.",
        example="Com R$500, você pode reservar R$300 para essenciais, R$150 para desejos e R$50 para meta.",
        quiz_question="Planejar ajuda principalmente a quê?",
        quiz_options={"A": "Gastar sem olhar", "B": "Decidir prioridades", "C": "Ignorar o saldo"},
        correct_option="B",
        feedback_correct="Boa. Planejamento é escolher prioridades antes.",
        feedback_wrong="Planejar é decidir prioridades e acompanhar o saldo.",
        mini_challenge="Antes do próximo gasto, veja se ele cabe no seu saldo do mês.",
        related_commands=("/resumo", "/meta"),
    ),
    LearningTopic(
        code="L08",
        slug="consumo-consciente",
        title="Consumo consciente",
        bncc_focus="Análise crítica, comparação de preços, necessidade versus desejo e cidadania.",
        content="Consumo consciente é pausar antes de comprar: eu preciso, quero muito ou estou no impulso?",
        example="Antes de comprar algo de R$60, espere 24h e compare com sua meta atual.",
        quiz_question="Qual atitude combina com consumo consciente?",
        quiz_options={"A": "Comprar no impulso", "B": "Comparar preço e necessidade", "C": "Ignorar gastos pequenos"},
        correct_option="B",
        feedback_correct="Exato. Comparar preço e necessidade reduz arrependimento.",
        feedback_wrong="Consumo consciente pede pausa, comparação e decisão com calma.",
        mini_challenge="Escolha um gasto do mês que você não repetiria e anote o motivo.",
        related_commands=("/resumo",),
    ),
    LearningTopic(
        code="L09",
        slug="bets-apostas",
        title="Bets e apostas",
        bncc_focus="Tomada de decisão, risco, probabilidade, consumo consciente e proteção financeira.",
        content="Aposta não é renda. É risco de perda. O cuidado principal é não usar dinheiro essencial nem tentar recuperar prejuízo.",
        example="Se R$20 fariam falta para transporte ou comida, esse dinheiro não pode ser tratado como valor para perder.",
        quiz_question="Qual é um sinal de alerta em apostas?",
        quiz_options={"A": "Parar no limite", "B": "Tentar recuperar prejuízo", "C": "Não usar dinheiro essencial"},
        correct_option="B",
        feedback_correct="Isso. Tentar recuperar prejuízo aumenta o risco de perda recorrente.",
        feedback_wrong="O alerta é tentar recuperar prejuízo. Esse é um momento de parar e pedir apoio se precisar.",
        mini_challenge="Compare apostar R$20 com guardar R$20 por 30 dias. Qual escolha protege melhor sua meta?",
        related_commands=("/resumo", "/meta"),
    ),
]

TOPICS_BY_SLUG = {topic.slug: topic for topic in LEARNING_TOPICS}


def get_topic(slug: str) -> LearningTopic | None:
    return TOPICS_BY_SLUG.get(slug)
