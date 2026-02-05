import sqlite3

conn = sqlite3.connect('data/torneo.db')
cursor = conn.cursor()

print('=== PARTIDOS OCTAVOS ===')
cursor.execute('SELECT id, slot, equipo_local_id, equipo_visitante_id, ganador_equipo_id, estado FROM partidos WHERE eliminatoria="octavos" ORDER BY slot')
octavos = cursor.fetchall()
print(f'Total: {len(octavos)} partidos')
for row in octavos:
    print(f'  ID:{row[0]} Slot:{row[1]} Local:{row[2]} Visitante:{row[3]} Ganador:{row[4]} Estado:{row[5]}')

print('\n=== PARTIDOS CUARTOS ===')
cursor.execute('SELECT id, slot, equipo_local_id, equipo_visitante_id, ganador_equipo_id, estado FROM partidos WHERE eliminatoria="cuartos" ORDER BY slot')
cuartos = cursor.fetchall()
print(f'Total: {len(cuartos)} partidos')
for row in cuartos:
    print(f'  ID:{row[0]} Slot:{row[1]} Local:{row[2]} Visitante:{row[3]} Ganador:{row[4]} Estado:{row[5]}')

# Obtener nombres de equipos
print('\n=== EQUIPOS (para referencia) ===')
cursor.execute('SELECT id, nombre FROM equipos ORDER BY id')
equipos = {row[0]: row[1] for row in cursor.fetchall()}
for eq_id, nombre in list(equipos.items())[:5]:
    print(f'  ID:{eq_id} -> {nombre}')

conn.close()
