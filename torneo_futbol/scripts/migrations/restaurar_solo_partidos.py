"""
Script para restaurar SOLO los partidos desde un backup.
Mantiene equipos y participantes actuales.
"""
import sqlite3
from pathlib import Path

def restaurar_solo_partidos(backup_db_path: str, destino_db_path: str):
    """
    Restaura solo partidos y goles desde una BD de backup.
    No toca equipos ni participantes.
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
    print("RESTAURACIÓN DE PARTIDOS DESDE BACKUP")
    print("=" * 70)
    
    # Conectar a ambas bases de datos
    conn_backup = sqlite3.connect(str(backup_path))
    conn_destino = sqlite3.connect(str(destino_path))
    
    conn_backup.row_factory = sqlite3.Row
    conn_destino.row_factory = sqlite3.Row
    
    cursor_backup = conn_backup.cursor()
    cursor_destino = conn_destino.cursor()
    
    try:
        # Verificar partidos en backup
        cursor_backup.execute("SELECT COUNT(*) FROM partidos")
        partidos_backup = cursor_backup.fetchone()[0]
        
        cursor_backup.execute("SELECT COUNT(*) FROM goles")
        goles_backup = cursor_backup.fetchone()[0]
        
        print(f"\n📦 Datos en el BACKUP:")
        print(f"   - Partidos: {partidos_backup}")
        print(f"   - Goles: {goles_backup}")
        
        # Verificar estado actual
        cursor_destino.execute("SELECT COUNT(*) FROM partidos")
        partidos_actual = cursor_destino.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM goles")
        goles_actual = cursor_destino.fetchone()[0]
        
        print(f"\n📊 Estado actual de la BD:")
        print(f"   - Partidos: {partidos_actual}")
        print(f"   - Goles: {goles_actual}")
        
        if partidos_actual > 0:
            print(f"\n⚠️  ADVERTENCIA: Ya hay {partidos_actual} partidos en la BD.")
            respuesta = input("¿Desea REEMPLAZAR los partidos actuales? (si/no): ")
            if respuesta.lower() not in ['si', 's', 'sí']:
                print("\n❌ Operación cancelada por el usuario.")
                return False
        
        # Limpiar partidos y goles existentes
        print("\n🗑️  Limpiando partidos y goles actuales...")
        cursor_destino.execute("DELETE FROM goles")
        cursor_destino.execute("DELETE FROM partidos")
        print("   - Limpiados")
        
        # Restaurar partidos
        print("\n📥 Restaurando partidos...")
        cursor_backup.execute("SELECT * FROM partidos")
        partidos = cursor_backup.fetchall()
        
        columnas_partidos = [desc[0] for desc in cursor_backup.description]
        
        for partido in partidos:
            columnas_str = ", ".join(columnas_partidos)
            placeholders = ", ".join(["?" for _ in columnas_partidos])
            valores = tuple(partido[col] for col in columnas_partidos)
            
            cursor_destino.execute(f"""
                INSERT INTO partidos ({columnas_str})
                VALUES ({placeholders})
            """, valores)
        
        print(f"   ✅ {len(partidos)} partidos restaurados")
        
        # Restaurar goles
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
        else:
            print("   - No hay goles en el backup")
        
        # Confirmar cambios
        conn_destino.commit()
        
        # Verificar resultado final
        cursor_destino.execute("SELECT COUNT(*) FROM partidos")
        partidos_final = cursor_destino.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM goles")
        goles_final = cursor_destino.fetchone()[0]
        
        print("\n" + "=" * 70)
        print("✅ RESTAURACIÓN DE PARTIDOS COMPLETADA")
        print("=" * 70)
        print(f"\n📊 Estado final de la BD:")
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
    exito = restaurar_solo_partidos(str(backup_db), str(destino_db))
    
    if exito:
        print("\n" + "=" * 70)
        print("🎉 Puedes abrir la aplicación ahora y tus partidos estarán restaurados.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ La restauración no se completó.")
        print("=" * 70)
    
    input("\nPresiona Enter para cerrar...")
