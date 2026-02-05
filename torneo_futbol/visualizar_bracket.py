"""
Script para visualizar cómo deberían verse los combos del bracket.
"""

print("="*80)
print("VISUALIZACIÓN DEL BRACKET - Cuartos de Final")
print("="*80)

# Según la lógica del código:
# - Slots impares (1, 3) van a la izquierda
# - Slots pares (2, 4) van a la derecha
# - Cada match tiene 2 combos (A y B)

print("\n📍 LADO IZQUIERDO (combos_cuartos_left)")
print("-"*80)
print("Match 0 (Slot 1):")
print("  Combo 0 (A): Local del slot 1 → Sevilla FC")
print("  Combo 1 (B): Visitante del slot 1 → (Pendiente)")
print()
print("Match 1 (Slot 3):")
print("  Combo 2 (A): Local del slot 3 → (Pendiente)")
print("  Combo 3 (B): Visitante del slot 3 → (Pendiente)")

print("\n📍 LADO DERECHO (combos_cuartos_right)")
print("-"*80)
print("Match 0 (Slot 2):")
print("  Combo 0 (A): Local del slot 2 → Real Madrid CF ← AQUÍ DEBERÍA ESTAR")
print("  Combo 1 (B): Visitante del slot 2 → (Pendiente)")
print()
print("Match 1 (Slot 4):")
print("  Combo 2 (A): Local del slot 4 → (Pendiente)")
print("  Combo 3 (B): Visitante del slot 4 → (Pendiente)")

print("\n" + "="*80)
print("CONCLUSIÓN")
print("="*80)
print("El Real Madrid DEBERÍA aparecer en:")
print("  - Lado: DERECHO")
print("  - Match: 0 (el primero de arriba)")
print("  - Posición: Local (combo A, arriba del 'vs')")
print()
print("Si no aparece ahí, el problema es de rendering/UI, no de lógica.")
print("="*80)
