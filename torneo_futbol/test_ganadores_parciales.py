"""Script para verificar por qué no se muestran los ganadores parciales."""
import sys
sys.path.insert(0, '.')

from app.models.match_model import MatchModel
from app.models.team_model import TeamModel
from app.services.tournament_service import TournamentService

print("="*80)
print("TEST: Verificar ganadores parciales en cuartos")
print("="*80)

# Obtener partidos de octavos
octavos = MatchModel.listar_partidos(eliminatoria="octavos")
print(f"\n📋 PARTIDOS DE OCTAVOS: {len(octavos)} partidos")
print("-"*80)

# Obtener equipos para nombres
equipos = TeamModel.listar_equipos()
equipos_dict = {e['id']: e['nombre'] for e in equipos}

# Mostrar cada partido de octavos con su estado
for partido in sorted(octavos, key=lambda p: p.get('slot', 0)):
    slot = partido.get('slot')
    local_id = partido.get('equipo_local_id')
    visitante_id = partido.get('equipo_visitante_id')
    ganador_id = partido.get('ganador_equipo_id')
    estado = partido.get('estado')
    
    local_nombre = equipos_dict.get(local_id, f'ID:{local_id}')
    visitante_nombre = equipos_dict.get(visitante_id, f'ID:{visitante_id}')
    ganador_nombre = equipos_dict.get(ganador_id, 'Sin ganador') if ganador_id else 'Sin ganador'
    
    print(f"Slot {slot:2d}: {local_nombre:30s} vs {visitante_nombre:30s}")
    print(f"          Estado: {estado:15s} Ganador: {ganador_nombre}")

# Simular la lógica de ganadores parciales
print("\n" + "="*80)
print("🔍 SIMULACIÓN: ¿Qué partidos de cuartos deberían crearse?")
print("="*80)

for slot_cuartos in range(1, 5):
    slot_octavos_1 = (slot_cuartos - 1) * 2 + 1
    slot_octavos_2 = (slot_cuartos - 1) * 2 + 2
    
    print(f"\n📌 Cuartos Slot {slot_cuartos} (viene de Octavos slots {slot_octavos_1} y {slot_octavos_2})")
    
    partido_1 = next((p for p in octavos if p.get('slot') == slot_octavos_1), None)
    partido_2 = next((p for p in octavos if p.get('slot') == slot_octavos_2), None)
    
    if partido_1:
        ganador_1 = partido_1.get('ganador_equipo_id')
        ganador_1_nombre = equipos_dict.get(ganador_1, 'Sin ganador') if ganador_1 else 'Sin ganador'
        print(f"   Octavos slot {slot_octavos_1}: {ganador_1_nombre} (ID: {ganador_1})")
    else:
        print(f"   Octavos slot {slot_octavos_1}: NO EXISTE")
    
    if partido_2:
        ganador_2 = partido_2.get('ganador_equipo_id')
        ganador_2_nombre = equipos_dict.get(ganador_2, 'Sin ganador') if ganador_2 else 'Sin ganador'
        print(f"   Octavos slot {slot_octavos_2}: {ganador_2_nombre} (ID: {ganador_2})")
    else:
        print(f"   Octavos slot {slot_octavos_2}: NO EXISTE")
    
    ganador_1_id = partido_1.get('ganador_equipo_id') if partido_1 else None
    ganador_2_id = partido_2.get('ganador_equipo_id') if partido_2 else None
    
    if ganador_1_id or ganador_2_id:
        print(f"   ✅ DEBERÍA CREARSE partido virtual:")
        local_nombre = equipos_dict.get(ganador_1_id, 'Pendiente') if ganador_1_id else 'Pendiente'
        visitante_nombre = equipos_dict.get(ganador_2_id, 'Pendiente') if ganador_2_id else 'Pendiente'
        print(f"      {local_nombre} vs {visitante_nombre}")
    else:
        print(f"   ❌ NO se crea (ambos sin ganador)")

# Verificar cuartos reales
print("\n" + "="*80)
print("📋 PARTIDOS REALES EN CUARTOS (BD)")
print("="*80)

cuartos = MatchModel.listar_partidos(eliminatoria="cuartos")
print(f"Total: {len(cuartos)} partidos")
for partido in sorted(cuartos, key=lambda p: p.get('slot', 0)):
    slot = partido.get('slot')
    local_id = partido.get('equipo_local_id')
    visitante_id = partido.get('equipo_visitante_id')
    local_nombre = equipos_dict.get(local_id, 'Pendiente')
    visitante_nombre = equipos_dict.get(visitante_id, 'Pendiente')
    print(f"Slot {slot}: {local_nombre} vs {visitante_nombre}")

print("\n" + "="*80)
