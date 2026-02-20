#!/usr/bin/env python3
"""
Script para forzar la propagación de ganadores existentes a la siguiente ronda.
Útil cuando se corrigió la lógica después de que los partidos ya se jugaron.
"""

import sys
import os

# Agregar la ruta del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.match_model import MatchModel
from app.services.tournament_service import TournamentService
from app.constants import FASE_OCTAVOS, FASE_CUARTOS, FASE_SEMIFINAL

def forzar_propagacion():
    """Propaga todos los ganadores existentes a la siguiente ronda."""
    
    print("="*80)
    print("FORZAR PROPAGACIÓN DE GANADORES")
    print("="*80)
    
    fases = [FASE_OCTAVOS, FASE_CUARTOS, FASE_SEMIFINAL]
    
    for fase in fases:
        print(f"\n{'='*80}")
        print(f"  Procesando {fase.upper()}")
        print(f"{'='*80}")
        
        partidos = MatchModel.listar_partidos(eliminatoria=fase)
        
        if not partidos:
            print(f"  No hay partidos en {fase}")
            continue
        
        for partido in partidos:
            ganador_id = partido.get('ganador_equipo_id')
            
            if not ganador_id:
                print(f"  ⏭️  Slot {partido['slot']}: Sin ganador, omitiendo")
                continue
            
            partido_id = partido['id']
            local_nombre = partido.get('local_nombre', 'N/A')
            visitante_nombre = partido.get('visitante_nombre', 'N/A')
            ganador_nombre = local_nombre if ganador_id == partido.get('equipo_local_id') else visitante_nombre
            
            print(f"\n  📍 Slot {partido['slot']} (ID: {partido_id}):")
            print(f"     {local_nombre} vs {visitante_nombre}")
            print(f"     Ganador: {ganador_nombre} (ID: {ganador_id})")
            
            try:
                print(f"     🔄 Propagando ganador...")
                partido_siguiente_id = TournamentService.propagate_winner(partido_id)
                
                if partido_siguiente_id:
                    print(f"     ✅ Propagado a partido ID: {partido_siguiente_id}")
                else:
                    print(f"     ✓ Propagación completada (final o ya existía)")
                    
            except Exception as e:
                print(f"     ❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "="*80)
    print("PROPAGACIÓN COMPLETADA")
    print("="*80)
    
    # Verificar estado final
    print("\n📊 ESTADO FINAL:")
    for fase in fases:
        partidos = MatchModel.listar_partidos(eliminatoria=fase)
        print(f"\n  {fase.upper()}: {len(partidos)} partidos")
        for p in partidos:
            ganador_id = p.get('ganador_equipo_id')
            ganador_str = ""
            if ganador_id:
                ganador_nombre = p.get('local_nombre') if ganador_id == p.get('equipo_local_id') else p.get('visitante_nombre')
                ganador_str = f" → Ganador: {ganador_nombre}"
            print(f"    Slot {p['slot']}: {p.get('local_nombre')} vs {p.get('visitante_nombre')}{ganador_str}")

if __name__ == '__main__':
    forzar_propagacion()
