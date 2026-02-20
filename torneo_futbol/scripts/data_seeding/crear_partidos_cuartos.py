#!/usr/bin/env python3
"""
Script para crear manualmente partidos de cuartos basándose en ganadores de octavos.
Útil cuando los partidos se jugaron antes de corregir el emparejamiento del bracket.
"""

import sys
import os

# Agregar la ruta del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.db import get_connection
from app.models.match_model import MatchModel
from app.models.team_model import TeamModel
from app.constants import FASE_OCTAVOS, FASE_CUARTOS
from datetime import datetime, timedelta

def obtener_ganadores_octavos():
    """Obtiene los ganadores de octavos por slot."""
    partidos_octavos = MatchModel.listar_partidos(eliminatoria=FASE_OCTAVOS)
    ganadores = {}
    
    for partido in partidos_octavos:
        slot = partido.get('slot')
        ganador_id = partido.get('ganador_equipo_id')
        if ganador_id:
            ganadores[slot] = {
                'equipo_id': ganador_id,
                'equipo_nombre': partido.get('local_nombre') if ganador_id == partido.get('equipo_local_id') else partido.get('visitante_nombre')
            }
    
    return ganadores

def crear_partidos_cuartos():
    """Crea partidos de cuartos basándose en el emparejamiento correcto."""
    
    print("="*60)
    print("CREACIÓN MANUAL DE PARTIDOS DE CUARTOS")
    print("="*60)
    
    # Obtener ganadores de octavos
    ganadores = obtener_ganadores_octavos()
    
    print("\n📊 Ganadores de Octavos:")
    for slot, data in sorted(ganadores.items()):
        print(f"  Slot {slot}: {data['equipo_nombre']} (ID: {data['equipo_id']})")
    
    # Verificar partidos de cuartos existentes
    partidos_cuartos = MatchModel.listar_partidos(eliminatoria=FASE_CUARTOS)
    print(f"\n📋 Partidos de cuartos existentes: {len(partidos_cuartos)}")
    for p in partidos_cuartos:
        print(f"  Slot {p['slot']}: {p.get('local_nombre')} vs {p.get('visitante_nombre')} (ID: {p['id']})")
    
    # Emparejamiento correcto según el bracket
    # Cuartos 1: Octavos 1 vs Octavos 3
    # Cuartos 2: Octavos 5 vs Octavos 7
    # Cuartos 3: Octavos 2 vs Octavos 4
    # Cuartos 4: Octavos 6 vs Octavos 8
    
    emparejamientos = [
        (1, 1, 3),  # (slot_cuartos, slot_octavos_1, slot_octavos_2)
        (2, 5, 7),
        (3, 2, 4),
        (4, 6, 8)
    ]
    
    fecha_base = datetime.now() + timedelta(days=7)
    
    print("\n🔧 Creando partidos de cuartos...")
    
    for slot_cuartos, slot_oct_1, slot_oct_2 in emparejamientos:
        # Verificar si ya existe el partido
        partido_existente = next((p for p in partidos_cuartos if p['slot'] == slot_cuartos), None)
        
        if partido_existente:
            print(f"\n⚠️  Cuartos slot {slot_cuartos}: Ya existe (ID: {partido_existente['id']})")
            continue
        
        # Verificar ganadores
        ganador_1 = ganadores.get(slot_oct_1)
        ganador_2 = ganadores.get(slot_oct_2)
        
        if not ganador_1 and not ganador_2:
            print(f"\n⏭️  Cuartos slot {slot_cuartos}: Ningún ganador aún (octavos {slot_oct_1} y {slot_oct_2})")
            continue
        
        if not ganador_1:
            print(f"\n⚠️  Cuartos slot {slot_cuartos}: Falta ganador de octavos slot {slot_oct_1}")
            continue
        
        if not ganador_2:
            print(f"\n⚠️  Cuartos slot {slot_cuartos}: Falta ganador de octavos slot {slot_oct_2}")
            continue
        
        # Ambos ganadores disponibles, crear partido
        local_id = ganador_1['equipo_id']
        visitante_id = ganador_2['equipo_id']
        
        fecha_partido = fecha_base + timedelta(days=(slot_cuartos - 1))
        fecha_hora_str = fecha_partido.strftime('%Y-%m-%d 18:00:00')
        
        print(f"\n✅ Creando Cuartos slot {slot_cuartos}:")
        print(f"   Local: {ganador_1['equipo_nombre']} (ID: {local_id})")
        print(f"   Visitante: {ganador_2['equipo_nombre']} (ID: {visitante_id})")
        print(f"   Fecha: {fecha_hora_str}")
        
        try:
            nuevo_id = MatchModel.crear_partido(
                eliminatoria=FASE_CUARTOS,
                slot=slot_cuartos,
                local_id=local_id,
                visitante_id=visitante_id,
                fecha_hora=fecha_hora_str
            )
            print(f"   ✓ Partido creado con ID: {nuevo_id}")
        except Exception as e:
            print(f"   ✗ Error al crear partido: {e}")
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    
    # Mostrar estado final
    partidos_cuartos_final = MatchModel.listar_partidos(eliminatoria=FASE_CUARTOS)
    print(f"\n📊 Total de partidos de cuartos: {len(partidos_cuartos_final)}")
    for p in partidos_cuartos_final:
        print(f"  Slot {p['slot']}: {p.get('local_nombre')} vs {p.get('visitante_nombre')}")

if __name__ == '__main__':
    crear_partidos_cuartos()
