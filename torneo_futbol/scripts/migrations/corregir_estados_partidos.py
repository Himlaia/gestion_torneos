"""
Script para corregir el estado de partidos marcados como 'Jugado' pero sin resultado.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.models.db import get_connection

def corregir_estados():
    """Corrige partidos marcados como 'Jugado' pero sin resultado."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar partidos con estado 'Jugado' pero sin ganador
    cursor.execute("""
        SELECT id, eliminatoria, slot, equipo_local_id, equipo_visitante_id, 
               goles_local, goles_visitante, ganador_equipo_id, estado
        FROM partidos
        WHERE estado = 'Jugado' AND ganador_equipo_id IS NULL
    """)
    
    partidos_sin_resultado = cursor.fetchall()
    
    if not partidos_sin_resultado:
        print("✅ No hay partidos que corregir.")
        return
    
    print(f"📋 Encontrados {len(partidos_sin_resultado)} partidos marcados como 'Jugado' pero sin resultado:")
    print()
    
    for p in partidos_sin_resultado:
        id_partido, eliminatoria, slot, local_id, visitante_id, goles_l, goles_v, ganador, estado = p
        
        # Obtener nombres de equipos
        cursor.execute("SELECT nombre FROM equipos WHERE id = ?", (local_id,))
        result = cursor.fetchone()
        local_nombre = result[0] if result else "Desconocido"
        
        cursor.execute("SELECT nombre FROM equipos WHERE id = ?", (visitante_id,))
        result = cursor.fetchone()
        visitante_nombre = result[0] if result else "Desconocido"
        
        print(f"  ID:{id_partido} | {eliminatoria} slot {slot}")
        print(f"    {local_nombre} vs {visitante_nombre}")
        print(f"    Goles: {goles_l} - {goles_v} | Ganador: {ganador} | Estado: {estado}")
        
        # Corregir a 'Programado' si tiene ambos equipos, o 'Pendiente' si falta alguno
        if local_id and visitante_id:
            nuevo_estado = 'Programado'
        else:
            nuevo_estado = 'Pendiente'
        
        cursor.execute("""
            UPDATE partidos 
            SET estado = ?
            WHERE id = ?
        """, (nuevo_estado, id_partido))
        
        print(f"    ✅ Estado actualizado a: {nuevo_estado}")
        print()
    
    conn.commit()
    print(f"✅ {len(partidos_sin_resultado)} partidos corregidos exitosamente.")

if __name__ == "__main__":
    print("="*60)
    print("CORRECCIÓN DE ESTADOS DE PARTIDOS")
    print("="*60)
    print()
    
    corregir_estados()
