"""
Script para restaurar datos de equipos y participantes desde un backup.
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

def restaurar_desde_backup(backup_db_path: str, destino_db_path: str):
    """
    Restaura equipos y participantes desde una BD de backup.
    
    Args:
        backup_db_path: Ruta a la BD de backup
        destino_db_path: Ruta a la BD de destino (actual)
    """
    backup_path = Path(backup_db_path)
    destino_path = Path(destino_db_path)
    
    if not backup_path.exists():
        print(f"❌ Error: No se encontró el archivo de backup: {backup_path}")
        return False
    
    if not destino_path.exists():
        print(f"❌ Error: No se encontró la BD de destino: {destino_path}")
        return False
    
    print("=" * 70)
    print("RESTAURACIÓN DE DATOS DESDE BACKUP")
    print("=" * 70)
    
    # Conectar a ambas bases de datos
    conn_backup = sqlite3.connect(str(backup_path))
    conn_destino = sqlite3.connect(str(destino_path))
    
    conn_backup.row_factory = sqlite3.Row
    conn_destino.row_factory = sqlite3.Row
    
    cursor_backup = conn_backup.cursor()
    cursor_destino = conn_destino.cursor()
    
    try:
        # Verificar datos existentes en destino
        cursor_destino.execute("SELECT COUNT(*) FROM equipos")
        equipos_existentes = cursor_destino.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM participantes")
        participantes_existentes = cursor_destino.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM partidos")
        partidos_existentes = cursor_destino.fetchone()[0]
        
        print(f"\n📊 Estado actual de la BD:")
        print(f"   - Equipos: {equipos_existentes}")
        print(f"   - Participantes: {participantes_existentes}")
        print(f"   - Partidos: {partidos_existentes}")
        
        # Verificar datos en backup
        cursor_backup.execute("SELECT COUNT(*) FROM equipos")
        equipos_backup = cursor_backup.fetchone()[0]
        
        cursor_backup.execute("SELECT COUNT(*) FROM participantes")
        participantes_backup = cursor_backup.fetchone()[0]
        
        cursor_backup.execute("SELECT COUNT(*) FROM partidos")
        partidos_backup = cursor_backup.fetchone()[0]
        
        print(f"\n📦 Datos en el BACKUP:")
        print(f"   - Equipos: {equipos_backup}")
        print(f"   - Participantes: {participantes_backup}")
        print(f"   - Partidos: {partidos_backup}")
        
        if equipos_existentes > 0 or participantes_existentes > 0:
            print(f"\n⚠️  ADVERTENCIA: La BD actual tiene datos.")
            respuesta = input("¿Desea REEMPLAZAR los datos actuales con los del backup? (si/no): ")
            if respuesta.lower() not in ['si', 's', 'sí']:
                print("\n❌ Operación cancelada por el usuario.")
                return False
        
        # Limpiar datos existentes
        print("\n🗑️  Limpiando datos actuales...")
        
        # Verificar qué tablas existen
        cursor_destino.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas_existentes = [row[0] for row in cursor_destino.fetchall()]
        
        # Eliminar datos en orden de dependencias (si existen)
        tablas_a_limpiar = ['convocatorias', 'goles', 'estadisticas_partidos', 'partidos', 'participantes', 'equipos']
        for tabla in tablas_a_limpiar:
            if tabla in tablas_existentes:
                cursor_destino.execute(f"DELETE FROM {tabla}")
                print(f"   - Limpiada tabla: {tabla}")
        
        # Restaurar equipos
        print("\n📥 Restaurando equipos...")
        cursor_backup.execute("SELECT * FROM equipos")
        equipos = cursor_backup.fetchall()
        
        for equipo in equipos:
            cursor_destino.execute("""
                INSERT INTO equipos (id, nombre, curso, color, escudo_path)
                VALUES (?, ?, ?, ?, ?)
            """, (
                equipo['id'],
                equipo['nombre'],
                equipo['curso'],
                equipo['color'],
                equipo['escudo_path'] if 'escudo_path' in equipo.keys() else None
            ))
        
        print(f"   ✅ {len(equipos)} equipos restaurados")
        
        # Restaurar participantes
        print("\n📥 Restaurando participantes...")
        cursor_backup.execute("SELECT * FROM participantes")
        participantes = cursor_backup.fetchall()
        
        # Verificar columnas disponibles en backup
        columnas_backup = [desc[0] for desc in cursor_backup.description]
        
        for participante in participantes:
            # Adaptar según las columnas disponibles
            if 'apellidos' in columnas_backup:
                cursor_destino.execute("""
                    INSERT INTO participantes 
                    (id, nombre, apellidos, fecha_nacimiento, curso, tipo_jugador, 
                     posicion, t_amarillas, t_rojas, goles, equipo_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    participante['id'],
                    participante['nombre'],
                    participante['apellidos'],
                    participante['fecha_nacimiento'] if 'fecha_nacimiento' in columnas_backup else None,
                    participante['curso'] if 'curso' in columnas_backup else None,
                    participante['tipo_jugador'] if 'tipo_jugador' in columnas_backup else None,
                    participante['posicion'] if 'posicion' in columnas_backup else None,
                    participante['t_amarillas'] if 't_amarillas' in columnas_backup else 0,
                    participante['t_rojas'] if 't_rojas' in columnas_backup else 0,
                    participante['goles'] if 'goles' in columnas_backup else 0,
                    participante['equipo_id']
                ))
            else:
                # Versión con apellido (singular)
                cursor_destino.execute("""
                    INSERT INTO participantes 
                    (id, nombre, apellidos, fecha_nacimiento, curso, tipo_jugador, 
                     posicion, t_amarillas, t_rojas, goles, equipo_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    participante['id'],
                    participante['nombre'],
                    participante.get('apellido', ''),
                    participante['fecha_nacimiento'] if 'fecha_nacimiento' in columnas_backup else None,
                    participante['curso'] if 'curso' in columnas_backup else None,
                    participante['tipo_jugador'] if 'tipo_jugador' in columnas_backup else None,
                    participante['posicion'] if 'posicion' in columnas_backup else None,
                    participante['t_amarillas'] if 't_amarillas' in columnas_backup else 0,
                    participante['t_rojas'] if 't_rojas' in columnas_backup else 0,
                    participante['goles'] if 'goles' in columnas_backup else 0,
                    participante['equipo_id']
                ))
        
        print(f"   ✅ {len(participantes)} participantes restaurados")
        
        # Restaurar partidos
        print("\n📥 Restaurando partidos...")
        cursor_backup.execute("SELECT * FROM partidos")
        partidos = cursor_backup.fetchall()
        
        # Obtener nombres de columnas de partidos en backup
        columnas_partidos = [desc[0] for desc in cursor_backup.description]
        
        for partido in partidos:
            # Construir la consulta dinámicamente según las columnas disponibles
            columnas_str = ", ".join(columnas_partidos)
            placeholders = ", ".join(["?" for _ in columnas_partidos])
            valores = tuple(partido[col] for col in columnas_partidos)
            
            cursor_destino.execute(f"""
                INSERT INTO partidos ({columnas_str})
                VALUES ({placeholders})
            """, valores)
        
        print(f"   ✅ {len(partidos)} partidos restaurados")
        
        # Restaurar goles si existen
        cursor_backup.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='goles'")
        if cursor_backup.fetchone():
            print("\n📥 Restaurando goles...")
            cursor_backup.execute("SELECT * FROM goles")
            goles = cursor_backup.fetchall()
            
            if goles:
                columnas_goles = [desc[0] for desc in cursor_backup.description]
                
                for gol in goles:
                    columnas_str = ", ".join(columnas_goles)
                    placeholders = ", ".join(["?" for _ in columnas_goles])
                    valores = tuple(gol[col] for col in columnas_goles)
                    
                    cursor_destino.execute(f"""
                        INSERT INTO goles ({columnas_str})
                        VALUES ({placeholders})
                    """, valores)
                
                print(f"   ✅ {len(goles)} goles restaurados")
        
        # Confirmar cambios
        conn_destino.commit()
        
        # Verificar resultado final
        cursor_destino.execute("SELECT COUNT(*) FROM equipos")
        equipos_final = cursor_destino.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM participantes")
        participantes_final = cursor_destino.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM partidos")
        partidos_final = cursor_destino.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM goles")
        goles_final = cursor_destino.fetchone()[0]
        
        print("\n" + "=" * 70)
        print("✅ RESTAURACIÓN COMPLETADA CON ÉXITO")
        print("=" * 70)
        print(f"\n📊 Estado final de la BD:")
        print(f"   - Equipos: {equipos_final}")
        print(f"   - Participantes: {participantes_final}")
        print(f"   - Partidos: {partidos_final}")
        print(f"   - Goles: {goles_final}")
        print(f"\n💾 Base de datos actualizada: {destino_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la restauración: {e}")
        conn_destino.rollback()
        return False
        
    finally:
        conn_backup.close()
        conn_destino.close()


if __name__ == "__main__":
    # Rutas por defecto
    proyecto_dir = Path(__file__).resolve().parent.parent
    data_dir = proyecto_dir / "data"
    
    backup_db = data_dir / "torneo_backup_20260204_233553.db"
    destino_db = data_dir / "torneo.db"
    
    print(f"\n📁 Directorio del proyecto: {proyecto_dir}")
    print(f"📁 Directorio de datos: {data_dir}")
    print(f"📦 Archivo de backup: {backup_db.name}")
    print(f"🎯 Base de datos destino: {destino_db.name}")
    
    # Ejecutar restauración
    exito = restaurar_desde_backup(str(backup_db), str(destino_db))
    
    if exito:
        print("\n" + "=" * 70)
        print("🎉 Puedes abrir la aplicación ahora y tus datos estarán restaurados.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ La restauración no se completó.")
        print("=" * 70)
    
    input("\nPresiona Enter para cerrar...")
