#!/usr/bin/env python3
"""
Script para migrar la base de datos y permitir NULL en equipo_local_id y equipo_visitante_id.
Esto es necesario para soportar partidos con equipos por definir (cuando solo un ganador ha avanzado).
"""

import sys
import os
import sqlite3
from datetime import datetime

# Agregar la ruta del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.db import get_db_path

def migrar_base_datos():
    """Migra la tabla partidos para permitir NULL en campos de equipos."""
    
    db_path = get_db_path()
    print(f"🗄️  Base de datos: {db_path}")
    
    # Backup
    db_path_str = str(db_path)
    backup_path = db_path_str.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    print(f"📦 Creando backup en: {backup_path}")
    
    import shutil
    shutil.copy2(db_path_str, backup_path)
    print("✅ Backup creado")
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path_str)
    cursor = conn.cursor()
    
    try:
        print("\n🔧 Iniciando migración...")
        
        # SQLite no permite ALTER COLUMN directamente, hay que recrear la tabla
        print("  1. Creando tabla temporal...")
        cursor.execute("""
            CREATE TABLE partidos_new (
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
        
        print("  2. Copiando datos existentes...")
        cursor.execute("""
            INSERT INTO partidos_new 
            SELECT * FROM partidos
        """)
        
        print("  3. Eliminando tabla antigua...")
        cursor.execute("DROP TABLE partidos")
        
        print("  4. Renombrando tabla nueva...")
        cursor.execute("ALTER TABLE partidos_new RENAME TO partidos")
        
        conn.commit()
        print("\n✅ Migración completada exitosamente")
        
        # Verificar
        print("\n📊 Verificando estructura...")
        cursor.execute("PRAGMA table_info(partidos)")
        columnas = cursor.fetchall()
        
        for col in columnas:
            col_id, name, type_, notnull, default, pk = col
            if name in ['equipo_local_id', 'equipo_visitante_id']:
                nullable = "NULL permitido" if notnull == 0 else "NOT NULL"
                print(f"  ✓ {name}: {type_} ({nullable})")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        conn.rollback()
        print(f"💾 Puedes restaurar el backup desde: {backup_path}")
        raise
    
    finally:
        conn.close()
    
    print(f"\n✨ Listo! La base de datos ahora permite partidos con equipos por definir")
    print(f"📁 Backup guardado en: {backup_path}")

if __name__ == '__main__':
    migrar_base_datos()
