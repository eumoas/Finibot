"""Flow de controle financeiro — receitas, gastos, resumo e planilha."""
from __future__ import annotations

import re
import asyncio
import logging
import unicodedata
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.transaction import EXPENSE_CATEGORIES, INCOME_CATEGORIES, Transaction
from app.repositories.goal_repo import GoalRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.user_repo import UserRepository
from app.services.gamification import MARCO_ACTIONS, GamificationEngine
from app.services.llm_service import llm_gateway
from app.prompts.insight_prompt import build_insight_context, should_generate_insight

logger = logging.getLogger(__name__)

INCOME_HELP = """💰 *Registrar receita*

Use assim:
`/receita 200 mesada`
`/receita 1200 salario`
`/receita 450 estagio abril`
`/receita 80 freela design`"""

EXPENSE_HELP = """🧾 *Registrar gasto*

Use assim:
`/gasto 18.50 alimentacao lanche`
`/gasto 4,80 transporte onibus`
`/gasto 29.90 streaming spotify`
`/gasto 42 cinema com o crush`"""

GASTOS_HELP = """🧾 *Controle de gastos*

Pode me mandar frases como:
`gastei R$18,50 num lanche hoje`
`recebi R$200 de mesada`
`paguei R$12 no ônibus ontem`

Comandos úteis:
/resumo — ver o mês atual
/planilha — receber uma planilha .xlsx
/corrigir — ajustar um lançamento já salvo
/restart — começar do zero
/gasto — registrar uma despesa
/receita — registrar uma entrada"""

CATEGORY_HINT = (
    "Categorias boas para comecar: alimentacao, transporte, streaming, cinema, "
    "role, crush, games, vestuario, estudos, mesada, estagio, freela."
)

TRANSACTION_CALLBACK_CONFIRM = "tx_confirm"
TRANSACTION_CALLBACK_CANCEL = "tx_cancel"
TRANSACTION_CALLBACK_EDIT = "tx_edit"
TRANSACTION_CALLBACK_EDIT_PREFIX = "tx_edit_"
SAVED_TRANSACTION_CALLBACK_PREFIX = "tx_saved_"
RESTART_CALLBACK_CONFIRM = "finance_restart_confirm"
RESTART_CALLBACK_CANCEL = "finance_restart_cancel"

STOPWORDS = {
    "a",
    "as",
    "com",
    "da",
    "de",
    "do",
    "dos",
    "em",
    "c",
    "hoje",
    "meu",
    "meus",
    "minha",
    "minhas",
    "na",
    "no",
    "nos",
    "num",
    "numa",
    "o",
    "ontem",
    "por",
    "pra",
    "primeira",
    "primeiro",
    "pro",
    "real",
    "reais",
    "rs",
    "conto",
    "contos",
    "um",
    "uma",
    "uns",
    "umas",
}

CATEGORY_KEYWORDS = {
    "alimentacao": {
        "almoco",
        "cafe",
        "comida",
        "hamburguer",
        "janta",
        "lanche",
        "mercado",
        "pizza",
        "refri",
        "restaurante",
        "rango",
        "salgado",
        "snack",
    },
    "transporte": {
        "99",
        "bus",
        "busao",
        "metro",
        "moto",
        "onibus",
        "passagem",
        "trem",
        "transporte",
        "uber",
    },
    "educacao": {"apostila", "curso", "escola", "estudo", "faculdade", "livro"},
    "streaming": {
        "amazon",
        "apple",
        "deezer",
        "disney",
        "globoplay",
        "hbo",
        "max",
        "netflix",
        "prime",
        "spotify",
        "streaming",
        "youtube",
    },
    "cinema_shows": {"cinema", "filme", "ingresso", "show", "teatro"},
    "roles_encontros": {
        "balada",
        "crush",
        "date",
        "encontro",
        "festa",
        "lazer",
        "passeio",
        "role",
        "rolê",
        "shopping",
    },
    "games": {"game", "games", "jogo", "jogos", "psn", "steam", "xbox"},
    "vestuario": {"blusa", "bone", "calca", "camisa", "camiseta", "look", "roupa", "tenis", "vestido"},
    "beleza": {"barba", "cabelo", "corte", "cosmetico", "maquiagem", "manicure", "perfume", "salão", "salao", "unha"},
    "compras": {"acessorio", "celular", "compra", "comprei", "eletronico", "fone", "loja", "notebook"},
    "viagem": {"galera", "glr", "hotel", "passagem", "pousada", "viajar", "viage", "viagem", "viajem"},
    "saude": {"dentista", "farmacia", "medico", "remedio", "saude"},
    "moradia": {"agua", "aluguel", "condominio", "energia", "internet", "luz"},
    "mesada": {"mesada"},
    "salario": {"pagamento", "salario"},
    "presente": {"presente", "presentes", "pix"},
    "bolsa_auxilio": {"auxilio", "auxílio", "bolsa"},
}


@dataclass(frozen=True)
class TransactionDraft:
    transaction_type: str
    amount: Decimal
    category: str
    description: str | None = None
    happened_on: date | None = None

    def to_payload(self) -> dict:
        return {
            "transaction_type": self.transaction_type,
            "amount": str(self.amount),
            "category": self.category,
            "description": self.description,
            "happened_on": (self.happened_on or date.today()).isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict) -> "TransactionDraft":
        return cls(
            transaction_type=payload["transaction_type"],
            amount=Decimal(payload["amount"]).quantize(Decimal("0.01")),
            category=payload["category"],
            description=payload.get("description"),
            happened_on=date.fromisoformat(payload["happened_on"]),
        )


def _month_range(today: date | None = None) -> tuple[date, date]:
    current = today or date.today()
    start = current.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def _previous_month_range(today: date | None = None) -> tuple[date, date]:
    start, _ = _month_range(today)
    previous_day = start - timedelta(days=1)
    return _month_range(previous_day)


def _money(value: Decimal | float | int) -> str:
    normalized = Decimal(str(value)).quantize(Decimal("0.01"))
    return f"R${normalized:.2f}".replace(".", ",")


def _date_pt(value: date | None) -> str:
    return (value or date.today()).strftime("%d/%m/%Y")


async def _get_session_service():
    from app.core.redis_client import get_redis
    from app.services.session_service import SessionService

    redis = await get_redis()
    return SessionService(redis)


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


async def _generate_optional_insight(context: dict | str) -> str | None:
    try:
        insight = await asyncio.wait_for(llm_gateway.generate_insight(context), timeout=8)
    except asyncio.TimeoutError:
        logger.warning("Insight indisponivel por timeout; seguindo sem insight")
        return None
    except Exception as exc:
        logger.warning("Insight indisponivel; seguindo sem insight: %s", exc)
        return None

    if not insight:
        return None

    normalized = _normalize(insight)
    if "problema tecnico" in normalized or "probleminha tecnico" in normalized:
        logger.warning("Insight omitido porque o LLM retornou mensagem tecnica: %r", insight)
        return None

    return insight


def _plain_text_from_markdown(text: str) -> str:
    return text.replace("*", "").replace("`", "")


async def _reply_markdown_safe(message, text: str):
    try:
        await message.reply_text(text, parse_mode="Markdown")
    except Exception as exc:
        logger.warning("Falha ao enviar Markdown; reenviando como texto simples: %s", exc)
        await message.reply_text(_plain_text_from_markdown(text))


EXPENSE_CATEGORY_OPTIONS = {
    _normalize(category): category for category in EXPENSE_CATEGORIES
}
INCOME_CATEGORY_OPTIONS = {
    _normalize(category): category for category in INCOME_CATEGORIES
}
CATEGORY_ALIASES = {
    "alimentacao": "Alimentação",
    "estudos": "Educação",
    "educacao": "Educação",
    "saude": "Saúde",
    "transporte": "Transporte",
    "streaming": "Streaming",
    "assinatura": "Streaming",
    "assinaturas": "Streaming",
    "netflix": "Streaming",
    "spotify": "Streaming",
    "cinema": "Cinema e Shows",
    "show": "Cinema e Shows",
    "shows": "Cinema e Shows",
    "cinema_shows": "Cinema e Shows",
    "cinema e shows": "Cinema e Shows",
    "role": "Rolês e Encontros",
    "roles": "Rolês e Encontros",
    "rolê": "Rolês e Encontros",
    "rolês": "Rolês e Encontros",
    "encontro": "Rolês e Encontros",
    "encontros": "Rolês e Encontros",
    "crush": "Rolês e Encontros",
    "roles_encontros": "Rolês e Encontros",
    "rolês e encontros": "Rolês e Encontros",
    "lazer": "Rolês e Encontros",
    "games": "Games",
    "game": "Games",
    "jogos": "Games",
    "vestuario": "Vestuário",
    "vestuário": "Vestuário",
    "roupa": "Vestuário",
    "roupas": "Vestuário",
    "tenis": "Vestuário",
    "tênis": "Vestuário",
    "beleza": "Beleza",
    "viagem": "Viagem",
    "viajem": "Viagem",
    "viage": "Viagem",
    "viajar": "Viagem",
    "compras": "Compras",
    "moradia": "Moradia",
    "presente": "Presentes",
    "presentes": "Presentes",
    "mesada": "Mesada",
    "estagio": "Estágio",
    "salario": "Salário",
    "bolsa": "Bolsa/Auxílio",
    "bolsa_auxilio": "Bolsa/Auxílio",
    "auxilio": "Bolsa/Auxílio",
    "auxílio": "Bolsa/Auxílio",
    "freela": "Freelas",
    "freelas": "Freelas",
    "outros": "Outros",
}


def _canonical_category(category: str | None, transaction_type: str) -> str:
    options = INCOME_CATEGORY_OPTIONS if transaction_type == "income" else EXPENSE_CATEGORY_OPTIONS
    normalized = _normalize(category or "")
    candidate = CATEGORY_ALIASES.get(normalized) or options.get(normalized)
    if candidate in options.values():
        return candidate
    return "Outros"


class ParsedTransaction(BaseModel):
    """Saída validada do LLM para um lançamento financeiro."""

    model_config = ConfigDict(extra="ignore")

    found: bool = False
    transaction_type: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    date_offset: int = 0

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if value not in {"income", "expense"}:
            raise ValueError("transaction_type inválido")
        return value

    def to_draft(self, today: date | None = None) -> "TransactionDraft" | None:
        if not self.found or not self.transaction_type or self.amount is None:
            return None
        current = today or date.today()
        category = _canonical_category(self.category, self.transaction_type)
        description = _clean_llm_description(self.description, category)
        return TransactionDraft(
            transaction_type=self.transaction_type,
            amount=self.amount.quantize(Decimal("0.01")),
            category=category,
            description=description,
            happened_on=current + timedelta(days=self.date_offset or 0),
        )


def _extract_date(text: str, today: date | None = None) -> date:
    current = today or date.today()
    normalized = _normalize(text)
    if re.search(r"\bontem\b", normalized):
        return current - timedelta(days=1)

    match = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", normalized)
    if not match:
        return current

    day = int(match.group(1))
    month = int(match.group(2))
    year = int(match.group(3)) if match.group(3) else current.year
    if year < 100:
        year += 2000

    try:
        return date(year, month, day)
    except ValueError:
        return current


def _infer_category(words: list[str], fallback: str | None = None) -> str:
    explicit = fallback if fallback and fallback not in STOPWORDS else None
    if explicit and explicit in CATEGORY_KEYWORDS:
        return explicit

    word_set = set(words)
    for category, keywords in CATEGORY_KEYWORDS.items():
        if word_set & keywords:
            return category
    return explicit or "outros"


def _clean_description(words: list[str], category: str) -> str | None:
    useful = [word for word in words if word not in STOPWORDS]
    if useful == [category]:
        return None
    if category in useful and len(useful) > 1:
        useful.remove(category)
    if category == "viagem":
        useful = [word for word in useful if word not in {"viage", "viagem", "viajem"}]
    description = " ".join(useful).strip()
    return description or None


def _clean_llm_description(description: str | None, category: str) -> str | None:
    if not description:
        return None

    normalized_category = _normalize(category)
    category_words = set(re.findall(r"[\w]+", normalized_category))
    words = re.findall(r"[\w]+", _normalize(description))
    useful = [word for word in words if word not in STOPWORDS]
    if not useful or set(useful) <= category_words:
        return None

    return " ".join(useful)[:100] or None


def parse_transaction_draft(
    text: str,
    transaction_type: str | None = None,
    today: date | None = None,
) -> TransactionDraft | None:
    """Extrai um rascunho de lancamento a partir de comando ou linguagem natural."""
    original = text.strip()
    text = re.sub(r"^/\w+\s*", "", original)

    lowered = _normalize(text)
    if transaction_type is None:
        if re.search(r"\b(recebi|recebe|ganhei|receber|salario|mesada)\b", lowered):
            transaction_type = "income"
        elif re.search(r"\b(gastei|gasto|paguei|pagamento|comprei|compra|comprar|foi|pago)\b", lowered):
            transaction_type = "expense"
        else:
            # Se não conseguir identificar o tipo, mas há um valor, assume gasto
            if re.search(r"(?:R\$\s*)?(\d+(?:[.,]\d{1,2})?)", text, flags=re.I):
                transaction_type = "expense"
            else:
                return None

    text = re.sub(
        r"^(gastei|gasto|paguei|pagamento|comprei|compra|comprar|recebi|recebe|ganhei|receber|foi|pago)\s+",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"^/\w+\s*", "", text.strip())
    match = re.search(r"(?:R\$\s*)?(\d+(?:[.,]\d{1,2})?)", text, flags=re.I)
    if not match:
        return None

    amount_raw = match.group(1).replace(",", ".")
    try:
        amount = Decimal(amount_raw).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None
    if amount <= 0:
        return None

    remainder = (text[: match.start()] + text[match.end() :]).strip()
    normalized_remainder = _normalize(remainder)
    parts = re.findall(r"[\w]+", normalized_remainder)
    while parts and parts[0] in STOPWORDS:
        parts.pop(0)

    explicit_category = parts[0] if parts else None
    raw_category = _infer_category(parts, explicit_category)
    category = _canonical_category(raw_category, transaction_type)
    description = _clean_description(parts, raw_category)
    return TransactionDraft(
        transaction_type=transaction_type,
        amount=amount,
        category=category,
        description=description,
        happened_on=_extract_date(original, today),
    )


def parse_transaction_args(text: str) -> tuple[Decimal, str, str | None] | None:
    """Extrai valor, categoria e descricao de um comando de lancamento."""
    transaction_type = "income" if text.strip().lower().startswith("/receita") else None
    if text.strip().lower().startswith("/gasto"):
        transaction_type = "expense"
    draft = parse_transaction_draft(text, transaction_type=transaction_type)
    if not draft:
        return None
    return draft.amount, draft.category, draft.description


async def parse_transaction_draft_v2(
    text: str,
    transaction_type: str | None = None,
    today: date | None = None,
) -> TransactionDraft | None:
    """Extrai lançamento via LLM e usa o parser regex como fallback."""
    try:
        parsed = ParsedTransaction.model_validate(await llm_gateway.parse_transaction(text))
        draft = parsed.to_draft(today=today)
    except (ValidationError, ValueError, TypeError) as exc:
        import logging
        logging.getLogger(__name__).warning("Parser LLM inválido, usando fallback: %s", exc)
        draft = None
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Parser LLM indisponível, usando fallback: %s", exc)
        draft = None

    if draft:
        if transaction_type and draft.transaction_type != transaction_type:
            draft = TransactionDraft(
                transaction_type=transaction_type,
                amount=draft.amount,
                category=_canonical_category(draft.category, transaction_type),
                description=draft.description,
                happened_on=draft.happened_on,
            )
        return draft

    return parse_transaction_draft(text, transaction_type=transaction_type, today=today)


def _summarize(transactions: list[Transaction]) -> dict:
    income = Decimal("0")
    expenses = Decimal("0")
    by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for item in transactions:
        if item.transaction_type == "income":
            income += item.amount
        else:
            expenses += item.amount
            by_category[item.category] += item.amount

    return {
        "income": income,
        "expenses": expenses,
        "balance": income - expenses,
        "by_category": dict(sorted(by_category.items(), key=lambda row: row[1], reverse=True)),
    }


async def handle_income_command(update: Update, db: AsyncSession, user: User):
    await _handle_transaction(update, db, user, "income")


async def handle_expense_command(update: Update, db: AsyncSession, user: User):
    await _handle_transaction(update, db, user, "expense")


async def _handle_transaction(
    update: Update,
    db: AsyncSession,
    user: User,
    transaction_type: str,
):
    draft = await parse_transaction_draft_v2(update.message.text or "", transaction_type=transaction_type)
    if not draft:
        await update.message.reply_text(
            INCOME_HELP if transaction_type == "income" else EXPENSE_HELP,
            parse_mode="Markdown",
        )
        return

    await _ask_transaction_confirmation(update, user, draft)


async def _ask_transaction_confirmation(
    update: Update,
    user: User,
    draft: TransactionDraft,
):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        session_svc = await _get_session_service()
        await session_svc.set_pending_transaction(user.telegram_id, draft.to_payload())
        logger.info(f"✅ Draft salvo em Redis para confirmação: {user.telegram_id}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar draft em Redis: {e}", exc_info=True)
        raise

    try:
        await update.message.reply_text(
            _draft_confirmation_text(draft),
            parse_mode="Markdown",
            reply_markup=_confirmation_keyboard(),
        )
        logger.info(f"✅ Mensagem de confirmação enviada para {user.telegram_id}")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem de confirmação: {e}", exc_info=True)
        raise


async def _save_transaction_draft(
    db: AsyncSession,
    user: User,
    draft: TransactionDraft,
) -> Transaction:
    repo = TransactionRepository(db)
    return await repo.create(
        user_id=user.id,
        transaction_type=draft.transaction_type,
        amount=draft.amount,
        category=draft.category,
        description=draft.description,
        happened_on=draft.happened_on,
    )


async def _month_transactions(db: AsyncSession, user: User, today: date | None = None) -> list[Transaction]:
    repo = TransactionRepository(db)
    start, end = _month_range(today)
    return await repo.list_by_period(user.id, start, end)


def _transaction_saved_message(transaction: Transaction) -> str:
    label = "receita" if transaction.transaction_type == "income" else "gasto"
    extra = f"\nObs.: {transaction.description}" if transaction.description else ""
    return (
        f"✅ Anotei {label}: *{_money(transaction.amount)}* em "
        f"*{transaction.category}* no dia {_date_pt(transaction.happened_on)}.{extra}"
    )


def _expense_mini_insight(
    transaction: Transaction,
    category_total: Decimal,
    total_expenses: Decimal,
    monthly_income: Decimal,
) -> str:
    """Gera um insight educativo simples sem depender do LLM."""
    parts = [
        f"Esse gasto deixou *{transaction.category}* em {_money(category_total)} no mês."
    ]

    if monthly_income > 0:
        income_pct = category_total / monthly_income * 100
        parts.append(f"Isso dá cerca de *{income_pct:.0f}%* da sua renda mensal.")
    elif total_expenses > 0:
        expense_pct = category_total / total_expenses * 100
        parts.append(f"Essa categoria representa *{expense_pct:.0f}%* dos seus gastos até agora.")
    else:
        parts.append("Acompanhar isso desde o começo ajuda a não descobrir o excesso só no fim do mês.")

    return "💡 " + " ".join(parts)


def _transaction_line(transaction: Transaction) -> str:
    label = "receita" if transaction.transaction_type == "income" else "gasto"
    description = f" - {transaction.description}" if transaction.description else ""
    return (
        f"{_date_pt(transaction.happened_on)} | {label} | "
        f"{_money(transaction.amount)} | {transaction.category}{description}"
    )


def _saved_transaction_list_keyboard(transactions: list[Transaction]) -> InlineKeyboardMarkup:
    rows = []
    for index, transaction in enumerate(transactions, start=1):
        rows.append(
            [
                InlineKeyboardButton(
                    f"{index}. {_money(transaction.amount)} - {transaction.category}",
                    callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}pick:{transaction.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton("Cancelar", callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}cancel")])
    return InlineKeyboardMarkup(rows)


def _saved_transaction_edit_keyboard(transaction: Transaction) -> InlineKeyboardMarkup:
    categories = INCOME_CATEGORIES if transaction.transaction_type == "income" else EXPENSE_CATEGORIES
    category_rows = []
    for start in range(0, min(len(categories), 12), 2):
        row = []
        for index in range(start, min(start + 2, len(categories))):
            row.append(
                InlineKeyboardButton(
                    categories[index],
                    callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}category:{transaction.id}:{index}",
                )
            )
        category_rows.append(row)

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Tipo", callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}type:{transaction.id}"),
                InlineKeyboardButton("Valor", callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}amount:{transaction.id}"),
                InlineKeyboardButton("Descrição", callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}description:{transaction.id}"),
            ],
            *category_rows,
            [
                InlineKeyboardButton("Hoje", callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}date_today:{transaction.id}"),
                InlineKeyboardButton("Ontem", callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}date_yesterday:{transaction.id}"),
            ],
            [InlineKeyboardButton("Cancelar", callback_data=f"{SAVED_TRANSACTION_CALLBACK_PREFIX}cancel")],
        ]
    )


async def _after_transaction_message(
    db: AsyncSession,
    user: User,
    transaction: Transaction,
    points_messages: list[str] | None = None,
) -> str:
    transactions = await _month_transactions(db, user, transaction.happened_on)
    summary = _summarize(transactions)
    lines = [
        _transaction_saved_message(transaction),
        "",
        f"Saldo do mês: *{_money(summary['balance'])}*",
    ]
    if points_messages:
        lines.append("Pontos: " + " | ".join(points_messages))

    if transaction.transaction_type == "expense":
        category_total = summary["by_category"].get(transaction.category, Decimal("0"))
        category_count = sum(
            1
            for item in transactions
            if item.transaction_type == "expense" and item.category == transaction.category
        )
        monthly_income = Decimal(str(user.monthly_income or 0))
        lines.extend(
            [
                "",
                _expense_mini_insight(
                    transaction,
                    category_total,
                    summary["expenses"],
                    monthly_income,
                ),
            ]
        )
        if should_generate_insight(
            float(category_total),
            float(monthly_income),
            category_count,
            float(summary["balance"]),
            user.constancia_mes_atual,
        ):
            context = build_insight_context(
                user.first_name or "amigo",
                transaction.category,
                float(category_total),
                float(monthly_income),
                float(summary["balance"]),
                float(summary["expenses"]),
                user.constancia_mes_atual,
            )
            insight = await _generate_optional_insight(context)
            if insight:
                lines.extend(["", f"✨ {insight}"])

    return "\n".join(lines)


def _edit_transaction_keyboard(draft: TransactionDraft) -> InlineKeyboardMarkup:
    categories = INCOME_CATEGORIES if draft.transaction_type == "income" else EXPENSE_CATEGORIES
    category_rows = []
    for start in range(0, min(len(categories), 12), 2):
        category_rows.append(
            [
                InlineKeyboardButton(
                    category,
                    callback_data=f"{TRANSACTION_CALLBACK_EDIT_PREFIX}category:{category}",
                )
                for category in categories[start:start + 2]
            ]
        )
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Tipo", callback_data=f"{TRANSACTION_CALLBACK_EDIT_PREFIX}type"),
                InlineKeyboardButton("Valor", callback_data=f"{TRANSACTION_CALLBACK_EDIT_PREFIX}amount"),
                InlineKeyboardButton("Descrição", callback_data=f"{TRANSACTION_CALLBACK_EDIT_PREFIX}description"),
            ],
            *category_rows,
            [
                InlineKeyboardButton("Hoje", callback_data=f"{TRANSACTION_CALLBACK_EDIT_PREFIX}date:today"),
                InlineKeyboardButton("Ontem", callback_data=f"{TRANSACTION_CALLBACK_EDIT_PREFIX}date:yesterday"),
            ],
            [InlineKeyboardButton("Voltar", callback_data="tx_edit_back")],
        ]
    )


def _confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=TRANSACTION_CALLBACK_CONFIRM),
                InlineKeyboardButton("✏️ Corrigir", callback_data=TRANSACTION_CALLBACK_EDIT),
            ],
            [InlineKeyboardButton("Cancelar", callback_data=TRANSACTION_CALLBACK_CANCEL)],
        ]
    )


def _draft_confirmation_text(draft: TransactionDraft, intro: str = "Conferindo antes de salvar:") -> str:
    label = "receita" if draft.transaction_type == "income" else "gasto"
    return (
        f"{intro}\n\n"
        f"*Tipo:* {label}\n"
        f"*Valor:* {_money(draft.amount)}\n"
        f"*Categoria:* {draft.category}\n"
        f"*Data:* {_date_pt(draft.happened_on)}\n"
        f"*Descricao:* {draft.description or 'sem descricao'}"
    )


async def maybe_handle_natural_transaction(
    update: Update,
    db: AsyncSession,
    user: User,
    text: str,
) -> bool:
    draft = await parse_transaction_draft_v2(text)
    if draft:
        await _ask_transaction_confirmation(update, user, draft)
        return True
    return False


async def handle_correction_step(update: Update, db: AsyncSession, user: User) -> bool:
    """Atualiza o rascunho pendente com a próxima mensagem do usuário."""
    session_svc = await _get_session_service()
    user_repo = UserRepository(db)
    step = user.flow_step or ""
    await user_repo.update(user, current_flow=None, flow_step=None)
    text = (update.message.text or "").strip()

    if step.startswith("saved_tx_") and "|" in step:
        field, transaction_id_raw = step.split("|", 1)
        try:
            transaction_id = uuid.UUID(transaction_id_raw)
        except ValueError:
            await update.message.reply_text("Não consegui identificar esse lançamento. Usa /corrigir de novo.")
            return True

        repo = TransactionRepository(db)
        transaction = await repo.get_by_id(user.id, transaction_id)
        if not transaction:
            await update.message.reply_text("Esse lançamento não foi encontrado. Usa /corrigir para ver os últimos.")
            return True

        if field == "saved_tx_amount":
            match = re.search(r"(?:R\$\s*)?(\d+(?:[.,]\d{1,2})?)", text, flags=re.I)
            if not match:
                await user_repo.update(user, current_flow="finance_correction", flow_step=step)
                await update.message.reply_text("Manda só o valor correto, tipo `18,50`.", parse_mode="Markdown")
                return True
            amount = Decimal(match.group(1).replace(",", ".")).quantize(Decimal("0.01"))
            transaction = await repo.update(transaction, amount=amount)
        elif field == "saved_tx_description":
            transaction = await repo.update(transaction, description=text[:100] or None)
        else:
            await update.message.reply_text("Não reconheci o campo. Usa /corrigir de novo.")
            return True

        await update.message.reply_text(
            "✅ Corrigi esse lançamento:\n" + _transaction_line(transaction),
            reply_markup=_saved_transaction_edit_keyboard(transaction),
        )
        return True

    payload = await session_svc.get_pending_transaction(user.telegram_id)

    if not payload:
        await update.message.reply_text("Esse lançamento expirou. Manda de novo que eu registro.")
        return True

    draft = TransactionDraft.from_payload(payload)

    if step == "tx_amount":
        match = re.search(r"(?:R\$\s*)?(\d+(?:[.,]\d{1,2})?)", text, flags=re.I)
        if not match:
            await user_repo.update(user, current_flow="finance_correction", flow_step="tx_amount")
            await update.message.reply_text("Manda só o valor, tipo `18,50`.", parse_mode="Markdown")
            return True
        amount = Decimal(match.group(1).replace(",", ".")).quantize(Decimal("0.01"))
        draft = TransactionDraft(draft.transaction_type, amount, draft.category, draft.description, draft.happened_on)
    elif step == "tx_description":
        draft = TransactionDraft(draft.transaction_type, draft.amount, draft.category, text[:100] or None, draft.happened_on)
    elif step == "tx_category":
        draft = TransactionDraft(
            draft.transaction_type,
            draft.amount,
            _canonical_category(text, draft.transaction_type),
            draft.description,
            draft.happened_on,
        )
    elif step == "tx_date":
        draft = TransactionDraft(draft.transaction_type, draft.amount, draft.category, draft.description, _extract_date(text))

    await session_svc.set_pending_transaction(user.telegram_id, draft.to_payload())
    await update.message.reply_text(
        _draft_confirmation_text(draft, "Atualizei o rascunho:"),
        parse_mode="Markdown",
        reply_markup=_confirmation_keyboard(),
    )
    return True


async def handle_transaction_callback(update: Update, db: AsyncSession, user: User) -> bool:
    import logging
    logger = logging.getLogger(__name__)
    
    query = update.callback_query
    if not query or not (
        query.data in {TRANSACTION_CALLBACK_CONFIRM, TRANSACTION_CALLBACK_CANCEL, TRANSACTION_CALLBACK_EDIT}
        or query.data.startswith(TRANSACTION_CALLBACK_EDIT_PREFIX)
        or query.data.startswith(SAVED_TRANSACTION_CALLBACK_PREFIX)
        or query.data in {RESTART_CALLBACK_CONFIRM, RESTART_CALLBACK_CANCEL}
    ):
        logger.warning(f"❌ Callback inválido: {query.data if query else 'query=None'}")
        return False

    logger.info(f"📌 Callback recebido: {query.data} | User: {user.telegram_id}")

    session_svc = await _get_session_service()

    if query.data in {RESTART_CALLBACK_CONFIRM, RESTART_CALLBACK_CANCEL}:
        if query.data == RESTART_CALLBACK_CANCEL:
            await query.answer("Cancelado")
            await query.edit_message_text("Fechado, nada foi apagado.")
            return True

        transaction_count = await TransactionRepository(db).delete_all_for_user(user.id)
        goal_count = await GoalRepository(db).delete_all_for_user(user.id)
        await UserRepository(db).update(
            user,
            points=0,
            level=1,
            constancia_total=0,
            constancia_mes_atual=0,
            constancia_mes_referencia=None,
            constancia_marcos_atingidos=[],
            last_entry_date=None,
            current_flow=None,
            flow_step=None,
        )
        await session_svc.clear_pending_transaction(user.telegram_id)
        await query.answer("Zerado")
        await query.edit_message_text(
            "✅ Restart feito. Apaguei seus lançamentos, metas e progresso de pontos.\n\n"
            f"Removidos: {transaction_count} lançamentos e {goal_count} metas.\n"
            "Pode começar de novo mandando algo como `gastei 18,50 no lanche hoje`."
        )
        return True

    if query.data.startswith(SAVED_TRANSACTION_CALLBACK_PREFIX):
        action = query.data.replace(SAVED_TRANSACTION_CALLBACK_PREFIX, "", 1)
        repo = TransactionRepository(db)

        if action == "cancel":
            await query.answer("Cancelado")
            await query.edit_message_text("Beleza, não alterei nada.")
            return True

        if action.startswith("pick:"):
            try:
                transaction_id = uuid.UUID(action.split(":", 1)[1])
            except ValueError:
                await query.answer("Inválido")
                return True
            transaction = await repo.get_by_id(user.id, transaction_id)
            if not transaction:
                await query.answer("Não encontrado")
                await query.edit_message_text("Esse lançamento não foi encontrado. Usa /corrigir de novo.")
                return True
            await query.answer("Escolhe o campo")
            await query.edit_message_text(
                "Lançamento selecionado:\n"
                f"{_transaction_line(transaction)}\n\n"
                "O que você quer corrigir?",
                reply_markup=_saved_transaction_edit_keyboard(transaction),
            )
            return True

        parts = action.split(":")
        field = parts[0]
        try:
            transaction_id = uuid.UUID(parts[1])
        except (IndexError, ValueError):
            await query.answer("Inválido")
            return True
        transaction = await repo.get_by_id(user.id, transaction_id)
        if not transaction:
            await query.answer("Não encontrado")
            await query.edit_message_text("Esse lançamento não foi encontrado. Usa /corrigir de novo.")
            return True

        if field in {"amount", "description"}:
            await UserRepository(db).update(
                user,
                current_flow="finance_correction",
                flow_step=f"saved_tx_{field}|{transaction.id}",
            )
            prompt = "Manda o valor correto, tipo `18,50`." if field == "amount" else "Manda a descrição correta."
            await query.answer("Pode mandar")
            await query.edit_message_text(prompt, parse_mode="Markdown")
            return True

        if field == "type":
            new_type = "income" if transaction.transaction_type == "expense" else "expense"
            transaction = await repo.update(
                transaction,
                transaction_type=new_type,
                category=_canonical_category(transaction.category, new_type),
            )
        elif field == "category":
            try:
                category_index = int(parts[2])
                categories = INCOME_CATEGORIES if transaction.transaction_type == "income" else EXPENSE_CATEGORIES
                category = categories[category_index]
            except (IndexError, ValueError):
                await query.answer("Categoria inválida")
                return True
            transaction = await repo.update(transaction, category=category)
        elif field == "date_today":
            transaction = await repo.update(transaction, happened_on=date.today())
        elif field == "date_yesterday":
            transaction = await repo.update(transaction, happened_on=date.today() - timedelta(days=1))
        else:
            await query.answer("Campo inválido")
            return True

        await query.answer("Corrigido")
        await query.edit_message_text(
            "✅ Corrigi esse lançamento:\n"
            f"{_transaction_line(transaction)}",
            reply_markup=_saved_transaction_edit_keyboard(transaction),
        )
        return True

    if query.data == TRANSACTION_CALLBACK_CANCEL:
        await session_svc.clear_pending_transaction(user.telegram_id)
        await query.answer("Cancelado")
        await query.edit_message_text("Tudo bem, descartei esse lançamento.")
        logger.info(f"✅ Transação cancelada para {user.telegram_id}")
        return True

    payload = await session_svc.get_pending_transaction(user.telegram_id)
    if not payload:
        logger.warning(f"⚠️  Payload expirado para {user.telegram_id}")
        await query.answer("Esse lançamento expirou.")
        await query.edit_message_text("Esse lançamento expirou. Manda de novo que eu registro.")
        return True

    draft = TransactionDraft.from_payload(payload)

    if query.data == TRANSACTION_CALLBACK_EDIT:
        await query.answer("O que você quer corrigir?")
        await query.edit_message_text(
            "Qual campo você quer corrigir?\n\n"
            "Para valor ou descrição, toque no campo e mande a próxima mensagem.",
            reply_markup=_edit_transaction_keyboard(draft),
        )
        return True

    if query.data.startswith(TRANSACTION_CALLBACK_EDIT_PREFIX):
        action = query.data.replace(TRANSACTION_CALLBACK_EDIT_PREFIX, "", 1)
        if action == "back":
            await query.answer("Voltando")
            await query.edit_message_text("Manda o lançamento corrigido de novo que eu reviso.")
            return True
        if action in {"amount", "description"}:
            await UserRepository(db).update(
                user,
                current_flow="finance_correction",
                flow_step=f"tx_{action}",
            )
            prompt = "Manda o valor correto, tipo `18,50`." if action == "amount" else "Manda a descrição correta."
            await query.answer("Pode mandar")
            await query.edit_message_text(prompt, parse_mode="Markdown")
            return True
        if action == "type":
            new_type = "income" if draft.transaction_type == "expense" else "expense"
            draft = TransactionDraft(
                transaction_type=new_type,
                amount=draft.amount,
                category=_canonical_category(draft.category, new_type),
                description=draft.description,
                happened_on=draft.happened_on,
            )
        elif action.startswith("category:"):
            draft = TransactionDraft(
                transaction_type=draft.transaction_type,
                amount=draft.amount,
                category=_canonical_category(action.split(":", 1)[1], draft.transaction_type),
                description=draft.description,
                happened_on=draft.happened_on,
            )
        elif action == "date:today":
            draft = TransactionDraft(
                transaction_type=draft.transaction_type,
                amount=draft.amount,
                category=draft.category,
                description=draft.description,
                happened_on=date.today(),
            )
        elif action == "date:yesterday":
            draft = TransactionDraft(
                transaction_type=draft.transaction_type,
                amount=draft.amount,
                category=draft.category,
                description=draft.description,
                happened_on=date.today() - timedelta(days=1),
            )
        else:
            await query.answer("Me manda o lançamento corrigido de novo.")
            return True

        await session_svc.set_pending_transaction(user.telegram_id, draft.to_payload())
        await query.answer("Atualizado")
        await query.edit_message_text(
            _draft_confirmation_text(draft, "Atualizei o rascunho:"),
            parse_mode="Markdown",
            reply_markup=_confirmation_keyboard(),
        )
        return True

    try:
        logger.info(f"✅ Draft recuperado: {draft.transaction_type} R${draft.amount} - {draft.category}")
        
        user_repo = UserRepository(db)
        gamification = GamificationEngine(user_repo)
        first_entry_today = user.last_entry_date != date.today()
        transaction = await _save_transaction_draft(db, user, draft)
        logger.info(f"✅ Transação salva no BD: ID={transaction.id}, Valor={transaction.amount}")
        constancia = await gamification.update_constancia(user)

        points_messages = []
        if first_entry_today:
            result = await gamification.award(user, "first_entry_of_day")
            points_messages.append(f"+{result.points_gained} primeiro lançamento do dia")
        if transaction.transaction_type == "income":
            result = await gamification.award(user, "income_registered")
            points_messages.append(f"+{result.points_gained} receita registrada")
        for marco in constancia.marcos_novos:
            result = await gamification.award(user, MARCO_ACTIONS[marco])
            points_messages.append(f"+{result.points_gained} {marco} dias de constância")

        await session_svc.clear_pending_transaction(user.telegram_id)
        await query.answer("Salvo")
        message = await _after_transaction_message(db, user, transaction, points_messages)
        await query.edit_message_text(message, parse_mode="Markdown")
        logger.info(f"✅ Confirmação enviada ao usuário {user.telegram_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro em handle_transaction_callback: {e}", exc_info=True)
        raise


async def handle_gastos_command(update: Update, db: AsyncSession, user: User):
    text = update.message.text or ""
    if len(text.split()) > 1:
        handled = await maybe_handle_natural_transaction(update, db, user, text.replace("/gastos", "", 1))
        if handled:
            return

    await update.message.reply_text(GASTOS_HELP, parse_mode="Markdown")


async def handle_correct_command(update: Update, db: AsyncSession, user: User):
    repo = TransactionRepository(db)
    transactions = await repo.list_recent(user.id, limit=8)

    if not transactions:
        await update.message.reply_text(
            "Ainda não tem lançamento salvo para corrigir.\n"
            "Quando tiver algo errado na planilha, usa /corrigir que eu mostro os últimos registros."
        )
        return

    lines = ["Qual lançamento você quer corrigir?"]
    for index, transaction in enumerate(transactions, start=1):
        lines.append(f"{index}. {_transaction_line(transaction)}")

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=_saved_transaction_list_keyboard(transactions),
    )


async def handle_restart_command(update: Update, db: AsyncSession, user: User):
    await update.message.reply_text(
        "Restart apaga seus lançamentos, metas e pontos, mas mantém seu cadastro para você continuar usando o bot.\n\n"
        "Tem certeza que quer começar do zero?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Sim, zerar", callback_data=RESTART_CALLBACK_CONFIRM),
                    InlineKeyboardButton("Cancelar", callback_data=RESTART_CALLBACK_CANCEL),
                ]
            ]
        ),
    )


async def handle_photo_receipt(update: Update, db: AsyncSession, user: User):
    """Processa foto com legenda para registrar transação."""
    import logging
    logger = logging.getLogger(__name__)
    
    caption = update.message.caption or ""
    logger.info(f"📸 [handle_photo_receipt] Caption: '{caption}' | User: {user.telegram_id}")
    
    draft = await parse_transaction_draft_v2(caption) if caption else None
    
    if draft:
        logger.info(f"✅ Draft parseado: {draft.transaction_type} R${draft.amount} - {draft.category}")
        try:
            await _ask_transaction_confirmation(update, user, draft)
        except Exception as e:
            logger.error(f"❌ Erro em _ask_transaction_confirmation: {e}", exc_info=True)
            raise
        return

    # Sem legenda ou legenda inválida
    if not caption:
        logger.info(f"⚠️  Foto sem legenda recebida")
    else:
        logger.info(f"⚠️  Caption não foi parseada: '{caption}'")
    
    await update.message.reply_text(
        "Recebi a foto e nao vou armazenar a imagem.\n\n"
        "Ainda preciso de uma legenda com valor para registrar, por exemplo:\n"
        "`gastei R$18,50 num lanche hoje`",
        parse_mode="Markdown",
    )


async def handle_summary_command(update: Update, db: AsyncSession, user: User):
    repo = TransactionRepository(db)
    start, end = _month_range()
    prev_start, prev_end = _previous_month_range()
    transactions = await repo.list_by_period(user.id, start, end)
    previous_transactions = await repo.list_by_period(user.id, prev_start, prev_end)

    if not transactions:
        await _reply_markdown_safe(
            update.message,
            "📭 Ainda nao tenho lancamentos deste mes.\n\n"
            "Use /receita ou /gasto para comecar.\n"
            f"{CATEGORY_HINT}",
        )
        return

    summary = _summarize(transactions)
    previous_summary = _summarize(previous_transactions)
    monthly_income = Decimal(str(user.monthly_income or 0))
    top_category = next(iter(summary["by_category"]), None)
    lines = [
        "📊 *Resumo do mes*",
        f"Entradas: *{_money(summary['income'])}*",
        f"Saidas: *{_money(summary['expenses'])}*",
        f"Saldo: *{_money(summary['balance'])}*",
    ]

    if previous_transactions:
        diff = summary["expenses"] - previous_summary["expenses"]
        direction = "a mais" if diff > 0 else "a menos"
        lines.append(
            f"Comparado ao mês anterior: {_money(abs(diff))} {direction} em gastos"
        )

    if summary["by_category"]:
        lines.append("\n*Gastos por categoria:*")
        for category, total in list(summary["by_category"].items())[:6]:
            marker = "→ " if category == top_category else "• "
            pct = ""
            if monthly_income > 0:
                pct = f" ({(total / monthly_income * 100):.0f}% da renda)"
            lines.append(f"{marker}{category}: {_money(total)}{pct}")

    goal_repo = GoalRepository(db)
    goals = await goal_repo.get_active_by_user(user.id)
    if goals:
        lines.append("\n*Metas ativas:*")
        for goal in goals[:3]:
            lines.append(
                f"• {goal.title}: {_money(goal.current_amount)} de {_money(goal.target_amount)} ({goal.progress_pct}%)"
            )

    insight_context = {
        "usuario": user.first_name or "amigo",
        "renda_mensal": float(monthly_income),
        "receitas_mes": float(summary["income"]),
        "gastos_mes": float(summary["expenses"]),
        "saldo_mes": float(summary["balance"]),
        "maior_categoria": top_category,
        "gastos_por_categoria": {key: float(value) for key, value in summary["by_category"].items()},
        "gastos_mes_anterior": float(previous_summary["expenses"]),
    }
    insight = await _generate_optional_insight(insight_context)
    if insight:
        lines.extend(["", f"💡 {insight}"])

    await _reply_markdown_safe(update.message, "\n".join(lines))


async def handle_spreadsheet_command(update: Update, db: AsyncSession, user: User):
    repo = TransactionRepository(db)
    goal_repo = GoalRepository(db)
    start, end = _month_range()
    transactions = await repo.list_by_period(user.id, start, end)
    goals = await goal_repo.get_active_by_user(user.id)

    from app.flows.xlsx_export import build_finance_xlsx

    output = BytesIO(build_finance_xlsx(user, transactions, goals, start))
    output.seek(0)

    filename = f"finibot_controle_{start.strftime('%Y_%m')}.xlsx"
    await update.message.reply_document(
        document=output,
        filename=filename,
        caption="📎 Sua planilha financeira do mes.",
    )
