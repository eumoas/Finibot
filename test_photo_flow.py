"""Teste do fluxo de fotos com legenda."""
from datetime import date
from decimal import Decimal
from app.flows.finance_flow import parse_transaction_draft

# Simulando diferentes legendas que um usuário poderia enviar em uma foto
test_cases = [
    ("gastei R$19.90 lanche", "expense", Decimal("19.90"), "alimentacao"),
    ("gastei 19,90 comida", "expense", Decimal("19.90"), "alimentacao"),
    ("paguei R$12 ônibus", "expense", Decimal("12.00"), "transporte"),
    ("recebi 200 mesada", "income", Decimal("200.00"), "mesada"),
    ("comprei 150 roupa", "expense", Decimal("150.00"), "compras"),
]

print("🧪 Testando parser de transações via legenda de foto:\n")

for caption, expected_type, expected_amount, expected_category in test_cases:
    draft = parse_transaction_draft(caption)
    
    if draft is None:
        print(f"❌ FALHA: '{caption}'")
        print(f"   Parser retornou None\n")
    else:
        type_ok = draft.transaction_type == expected_type
        amount_ok = draft.amount == expected_amount
        category_ok = draft.category == expected_category
        
        if type_ok and amount_ok and category_ok:
            print(f"✅ OK: '{caption}'")
            print(f"   Tipo: {draft.transaction_type}, Valor: {draft.amount}, Categoria: {draft.category}")
            print(f"   Descrição: {draft.description}\n")
        else:
            print(f"⚠️ PARCIAL: '{caption}'")
            if not type_ok:
                print(f"   ❌ Tipo: esperado {expected_type}, obteve {draft.transaction_type}")
            if not amount_ok:
                print(f"   ❌ Valor: esperado {expected_amount}, obteve {draft.amount}")
            if not category_ok:
                print(f"   ❌ Categoria: esperada {expected_category}, obteve {draft.category}")
            print()

print("\n📋 Resumo: Teste concluído")
