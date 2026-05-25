"""Teste para validar parser de legendas de foto."""
import sys
sys.path.insert(0, '/home/moas/Documentos/FiniBot')

from datetime import date
from decimal import Decimal
from app.flows.finance_flow import parse_transaction_draft

print("🧪 TESTE: Parser de Legendas de Foto\n")
print("=" * 60)

# Casos de teste típicos que um usuário enviaria em uma foto
test_cases = [
    # (legenda, esperado_reconhecer)
    ("gastei R$19.90 lanche", True),
    ("gastei 19,90 comida", True),
    ("paguei R$12 ônibus", True),
    ("recebi 200 mesada", True),
    ("comprei 150 roupa", True),
    ("gasto 45 cinema", True),
    ("19.90", True),  # Só valor
    ("R$ 50", True),   # Com símbolo
    ("", False),       # Vazio
    ("foto do cupom", False),  # Sem valor
    ("comprovante de pagamento", False),  # Sem valor
]

for caption, deveria_funcionar in test_cases:
    draft = parse_transaction_draft(caption)
    
    if draft is None:
        status = "❌ FALHOU" if deveria_funcionar else "✅ OK (rejeitado)"
        print(f"\n{status}: '{caption}'")
        if deveria_funcionar:
            print("   ⚠️  Deveria ter parseado mas retornou None!")
    else:
        status = "✅ OK" if deveria_funcionar else "❌ FALHOU (deveria rejeitar)"
        print(f"\n{status}: '{caption}'")
        print(f"   Tipo: {draft.transaction_type}")
        print(f"   Valor: R${draft.amount:.2f}")
        print(f"   Categoria: {draft.category}")
        if draft.description:
            print(f"   Descrição: {draft.description}")

print("\n" + "=" * 60)
print("✅ Teste concluído!")
