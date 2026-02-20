"""Script para restaurar los partidos perdidos después de reiniciar el torneo."""
import sqlite3
import sys
from pathlib import Path

# Agregar el path del proyecto
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from app.models.db import get_connection

def restaurar_partidos():
    """Restaura los 9 partidos de octavos que se habían jugado."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Los partidos que tenías
    # (id, eliminatoria, slot, fecha_hora, local_id, visitante_id, arbitro_id, 
    #  goles_local, goles_visitante, penaltis_local, penaltis_visitante, ganador_id, estado)
    partidos = [
        (185, 'octavos', 1, '2025-01-27 20:00:00', 1, 16, None, 3, 1, None, None, 1, 'Jugado'),
        (186, 'octavos', 2, '2025-01-27 20:00:00', 9, 8, None, 1, 1, 4, 2, 9, 'Jugado'),
        (187, 'octavos', 3, '2025-01-28 20:00:00', 5, 12, None, 1, 0, None, None, 5, 'Jugado'),
        (188, 'octavos', 4, '2025-01-28 20:00:00', 13, 4, None, 1, 2, None, None, 4, 'Jugado'),
        (189, 'octavos', 5, '2025-01-29 20:00:00', 3, 14, None, 0, 0, 3, 1, 3, 'Jugado'),
        (190, 'octavos', 6, '2025-01-29 20:00:00', 11, 6, None, 0, 1, None, None, 6, 'Jugado'),
        (191, 'octavos', 7, '2025-01-30 20:00:00', 7, 10, None, 1, 0, None, None, 7, 'Jugado'),
        (192, 'octavos', 8, '2025-01-30 20:00:00', 15, 2, None, 0, 1, None, None, 2, 'Jugado'),
        # Partido de cuartos generado automáticamente
        (193, 'cuartos', 1, '2025-02-03 20:00:00', 1, 9, None, 0, 0, None, None, None, 'Pendiente'),
    ]
    
    print("Restaurando partidos...")
    for partido in partidos:
        cursor.execute("""
            INSERT INTO partidos 
            (id, eliminatoria, slot, fecha_hora, equipo_local_id, equipo_visitante_id, arbitro_id,
             goles_local, goles_visitante, penaltis_local, penaltis_visitante, ganador_equipo_id, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, partido)
        print(f"  Partido {partido[0]}: Equipo {partido[4]} vs Equipo {partido[5]} - {partido[1]} - {partido[12]}")
    
    # Los goles que tenías - usando IDs actuales de participantes
    # Buscar un participante de cada equipo para asignar los goles
    goles_por_equipo = {
        1: 3,   # 3 goles
        16: 1,  # 1 gol
        9: 1,   # 1 gol
        8: 1,   # 1 gol
        5: 1,   # 1 gol
        13: 1,  # 1 gol
        4: 2,   # 2 goles
    }
    
    print("\nRestaurando goles...")
    for equipo_id, num_goles in goles_por_equipo.items():
        # Encontrar participante del equipo
        cursor.execute("""
            SELECT id FROM participantes 
            WHERE equipo_id = ? AND tipo_jugador IN ('Jugador', 'Ambos')
            LIMIT 1
        """, (equipo_id,))
        participante = cursor.fetchone()
        
        if not participante:
            print(f"  ⚠ No se encontró participante para equipo {equipo_id}")
            continue
        
        participante_id = participante[0]
        
        # Encontrar el partido donde jugó este equipo
        cursor.execute("""
            SELECT id FROM partidos 
            WHERE (equipo_local_id = ? OR equipo_visitante_id = ?)
            AND estado = 'Jugado'
            ORDER BY id
            LIMIT 1
        """, (equipo_id, equipo_id))
        partido = cursor.fetchone()
        
        if not partido:
            print(f"  ⚠ No se encontró partido jugado para equipo {equipo_id}")
            continue
        
        partido_id = partido[0]
        
        # Insertar los goles
        for i in range(num_goles):
            minuto = 15 + (i * 15)
            cursor.execute("""
                INSERT INTO goles (partido_id, participante_id, equipo_id, minuto)
                VALUES (?, ?, ?, ?)
            """, (partido_id, participante_id, equipo_id, minuto))
            print(f"  Gol en partido {partido_id}, equipo {equipo_id}, participante {participante_id}, minuto {minuto}")
    
    conn.commit()
    conn.close()
    
    print(f"\n¡Partidos restaurados correctamente!")
    print(f"- {len(partidos)} partidos")
    print(f"- Goles restaurados para {len(goles_por_equipo)} equipos")

if __name__ == "__main__":
    try:
        restaurar_partidos()
    except Exception as e:
        print(f"Error al restaurar: {e}")
        import traceback
        traceback.print_exc()
