"""Script para probar la propagación de ganadores."""
import sys
sys.path.insert(0, '.')

from app.models.match_model import MatchModel
from app.services.tournament_service import TournamentService

print("="*60)
print("TEST DE PROPAGACIÓN DE GANADORES")
print("="*60)

# Simular lo que pasaría si completamos el slot 2 de octavos
print("\nEscenario: ¿Qué pasa si el slot 2 de octavos se juega?")
print("Slot 1 (Sevilla) ya tiene ganador")
print("Si slot 2 también tiene ganador, se debería crear el partido 1 de cuartos")

# Obtener partido del slot 1 (ya jugado)
partidos_octavos = MatchModel.listar_partidos(eliminatoria="octavos")
partido_slot1 = next((p for p in partidos_octavos if p['slot'] == 1), None)
partido_slot2 = next((p for p in partidos_octavos if p['slot'] == 2), None)

if partido_slot1:
    print(f"\nPartido Slot 1:")
    print(f"  ID: {partido_slot1['id']}")
    print(f"  Local: {partido_slot1.get('equipo_local_id')}")
    print(f"  Visitante: {partido_slot1.get('equipo_visitante_id')}")
    print(f"  Ganador: {partido_slot1.get('ganador_equipo_id')}")
    print(f"  Estado: {partido_slot1.get('estado')}")

if partido_slot2:
    print(f"\nPartido Slot 2:")
    print(f"  ID: {partido_slot2['id']}")
    print(f"  Local: {partido_slot2.get('equipo_local_id')}")
    print(f"  Visitante: {partido_slot2.get('equipo_visitante_id')}")
    print(f"  Ganador: {partido_slot2.get('ganador_equipo_id')}")
    print(f"  Estado: {partido_slot2.get('estado')}")

# Verificar lógica de hermanos
print("\n--- Probando lógica de hermanos ---")
slot_actual = 1
slot_hermano = slot_actual + 1 if slot_actual % 2 == 1 else slot_actual - 1
print(f"Slot actual: {slot_actual}")
print(f"Slot hermano calculado: {slot_hermano}")

# Obtener hermano
hermano = TournamentService._obtener_partido_hermano("octavos", 1)
if hermano:
    print(f"Hermano encontrado: Slot {hermano.get('slot')}")
    print(f"  Ganador del hermano: {hermano.get('ganador_equipo_id')}")
else:
    print("ERROR: No se encontró hermano")

# Calcular siguiente slot
siguiente_slot, es_local = TournamentService._calcular_siguiente_partido("octavos", 1)
print(f"\nSiguiente partido:")
print(f"  Slot en cuartos: {siguiente_slot}")
print(f"  Ganador de slot 1 va como: {'Local' if es_local else 'Visitante'}")

# Verificar si existen partidos en cuartos
partidos_cuartos = MatchModel.listar_partidos(eliminatoria="cuartos")
print(f"\nPartidos actuales en cuartos: {len(partidos_cuartos)}")

print("\n" + "="*60)
