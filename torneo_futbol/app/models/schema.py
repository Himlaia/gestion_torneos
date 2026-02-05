"""Esquema de la base de datos y creación de tablas."""
import sqlite3


def create_schema(conn: sqlite3.Connection) -> None:
    """
    Crea el esquema completo de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
    """
    cursor = conn.cursor()
    
    # Habilitar claves foráneas
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Tabla de equipos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            curso TEXT NOT NULL,
            color TEXT NOT NULL,
            escudo_path TEXT
        )
    """)
    
    # Tabla de participantes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT,
            fecha_nacimiento TEXT NOT NULL,
            curso TEXT NOT NULL,
            tipo_jugador TEXT NOT NULL,
            posicion TEXT NOT NULL,
            t_amarillas INTEGER NOT NULL DEFAULT 0,
            t_rojas INTEGER NOT NULL DEFAULT 0,
            goles INTEGER NOT NULL DEFAULT 0,
            equipo_id INTEGER,
            FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE SET NULL
        )
    """)
    
    # Tabla de partidos
    # NOTA: equipo_local_id y equipo_visitante_id permiten NULL para soportar 
    # partidos con equipos por definir (cuando solo un ganador ha avanzado)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eliminatoria TEXT NOT NULL,
            slot INTEGER NOT NULL,
            fecha_hora TEXT,
            equipo_local_id INTEGER,
            equipo_visitante_id INTEGER,
            arbitro_id INTEGER,
            goles_local INTEGER,
            goles_visitante INTEGER,
            penaltis_local INTEGER,
            penaltis_visitante INTEGER,
            ganador_equipo_id INTEGER,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            FOREIGN KEY (equipo_local_id) REFERENCES equipos(id) ON DELETE RESTRICT,
            FOREIGN KEY (equipo_visitante_id) REFERENCES equipos(id) ON DELETE RESTRICT,
            FOREIGN KEY (arbitro_id) REFERENCES participantes(id) ON DELETE SET NULL,
            FOREIGN KEY (ganador_equipo_id) REFERENCES equipos(id) ON DELETE SET NULL,
            UNIQUE (eliminatoria, slot)
        )
    """)
    
    # Tabla de convocados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS convocados (
            partido_id INTEGER NOT NULL,
            participante_id INTEGER NOT NULL,
            equipo_id INTEGER NOT NULL,
            PRIMARY KEY (partido_id, participante_id),
            FOREIGN KEY (partido_id) REFERENCES partidos(id) ON DELETE CASCADE,
            FOREIGN KEY (participante_id) REFERENCES participantes(id) ON DELETE CASCADE,
            FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE RESTRICT
        )
    """)
    
    # Tabla de estadísticas del partido
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats_partido (
            partido_id INTEGER NOT NULL,
            participante_id INTEGER NOT NULL,
            goles INTEGER NOT NULL DEFAULT 0,
            amarillas INTEGER NOT NULL DEFAULT 0,
            rojas INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (partido_id, participante_id),
            FOREIGN KEY (partido_id, participante_id)
                REFERENCES convocados(partido_id, participante_id)
                ON DELETE CASCADE
        )
    """)
    
    # Tabla de goles con autor
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partido_id INTEGER NOT NULL,
            participante_id INTEGER NOT NULL,
            equipo_id INTEGER NOT NULL,
            minuto INTEGER,
            FOREIGN KEY (partido_id) REFERENCES partidos(id) ON DELETE CASCADE,
            FOREIGN KEY (participante_id) REFERENCES participantes(id) ON DELETE CASCADE,
            FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE RESTRICT
        )
    """)
    
    # Crear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_participantes_equipo ON participantes(equipo_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_partidos_eliminatoria ON partidos(eliminatoria)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_convocados_partido ON convocados(partido_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_goles_partido ON goles(partido_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_goles_participante ON goles(participante_id)")
    
    print("✓ Esquema de base de datos creado correctamente")
