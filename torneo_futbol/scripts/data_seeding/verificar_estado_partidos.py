#!/usr/bin/env python3
"""
Script para verificar el estado de los partidos y sus ganadores.
"""

import sys
import os

# Agregar la ruta del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.match_model import MatchModel
from app.constants import FASE_OCTAVOS, FASE_CUARTOS, FASE_SEMIFINAL

def verificar_estado():
    """Verifica el estado de los partidos en todas las fases."""
    
    print("="*80)
    print("ESTADO DE LOS PARTIDOS Y GANADORES")
    print("="*80)
    
    fases = [FASE_OCTAVOS, FASE_CUARTOS, FASE_SEMIFINAL]
    
    for fase in fases:
        partidos = MatchModel.listar_partidos(eliminatoria=fase)
        
        print(f"\n{'='*80}")
        print(f"  {fase.upper()}: {len(partidos)} partidos")
        print(f"{'='*80}")
        
        if not partidos:
            print("  (ningún partido)")
            continue
        
        for p in sorted(partidos, key=lambda x: x.get('slot', 0)):
            slot = p.get('slot')
            partido_id = p.get('id')
            local = p.get('local_nombre', 'N/A')
            visitante = p.get('visitante_nombre', 'N/A')
            goles_local = p.get('goles_local')
            goles_visitante = p.get('goles_visitante')
            ganador_id = p.get('ganador_equipo_id')
            estado = p.get('estado', 'N/A')
            
            print(f"\n  📍 Slot {slot} (ID: {partido_id}):")
            print(f"     {local} vs {visitante}")
            
            if goles_local is not None and goles_visitante is not None:
                print(f"     Resultado: {goles_local} - {goles_visitante}")
            else:
                print(f"     Resultado: Sin jugar")
            
            if ganador_id:
                ganador_nombre = local if ganador_id == p.get('equipo_local_id') else visitante
                print(f"     ✅ Ganador: {ganador_nombre} (ID: {ganador_id})")
            else:
                print(f"     ⏳ Sin ganador")
            
            print(f"     Estado: {estado}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    verificar_estado()
