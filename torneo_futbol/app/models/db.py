"""Gestión de la conexión a la base de datos."""
import sqlite3
import sys
from pathlib import Path
from typing import Optional


class DbError(Exception):
    """Excepción personalizada para errores de base de datos."""
    pass


def get_db_path() -> Path:
    """
    Obtiene la ruta absoluta al archivo de base de datos.
    Crea el directorio data si no existe.
    
    Si la aplicación está empaquetada (PyInstaller), guarda la BD
    en el directorio del ejecutable. Si está en desarrollo, usa
    la carpeta data/ del proyecto.
    
    Returns:
        Path: Ruta al archivo torneo.db
    """
    # Detectar si estamos en un ejecutable empaquetado
    if getattr(sys, 'frozen', False):
        # Estamos en un ejecutable empaquetado
        # sys.executable es la ruta al .exe
        root_dir = Path(sys.executable).parent
    else:
        # Estamos en desarrollo
        root_dir = Path(__file__).resolve().parent.parent.parent
    
    data_dir = root_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    return data_dir / "torneo.db"


_db_path_printed = False
_schema_printed = False

def get_connection() -> sqlite3.Connection:
    """
    Obtiene una conexión a la base de datos SQLite.
    Configura row_factory y activa claves foráneas.
    
    Returns:
        sqlite3.Connection: Conexión configurada a la base de datos
        
    Raises:
        DbError: Si hay error al conectar
    """
    global _db_path_printed, _schema_printed
    try:
        db_path = get_db_path()
        if not _db_path_printed:
            print(f"[APP-DB] Ruta absoluta BD: {db_path.resolve()}")
            _db_path_printed = True
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Solo imprimir info de debug si la tabla partidos ya existe
        if not _schema_printed:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='partidos'")
            tabla_existe = cursor.fetchone()
            
            if tabla_existe:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%part%'")
                tablas = cursor.fetchall()
                print(f"[APP-ESQUEMA] Tablas con 'part': {[t[0] for t in tablas]}")
                
                cursor.execute("PRAGMA table_info(partidos)")
                columnas_info = cursor.fetchall()
                print(f"[APP-ESQUEMA] Columnas de 'partidos': {[col[1] for col in columnas_info]}")
                
                cursor.execute("SELECT COUNT(*) FROM partidos")
                count = cursor.fetchone()[0]
                print(f"[APP-ESQUEMA] Total partidos en BD: {count}")
            else:
                print("[APP-ESQUEMA] Base de datos nueva - esperando inicialización del esquema")
            
            _schema_printed = True
        
        return conn
    except sqlite3.Error as e:
        raise DbError(f"Error al conectar a la base de datos: {e}")


def init_db() -> None:
    """
    Inicializa la base de datos creando el esquema.
    
    Raises:
        DbError: Si hay error durante la inicialización
    """
    conn = None
    try:
        db_path = get_db_path()
        print(f"Ruta de base de datos: {db_path.absolute()}")
        
        conn = get_connection()
        
        # Importar y ejecutar creación de esquema
        from app.models.schema import create_schema
        create_schema(conn)
        
        conn.commit()
        
        # Verificar datos existentes
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM equipos")
        equipos_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM participantes")
        participantes_count = cursor.fetchone()[0]
        print(f"✓ Base de datos inicializada correctamente")
        print(f"  - Equipos existentes: {equipos_count}")
        print(f"  - Participantes existentes: {participantes_count}")
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DbError(f"Error al inicializar la base de datos: {e}")
    except ImportError as e:
        if conn:
            conn.rollback()
        raise DbError(f"Error al importar el esquema: {e}")
    finally:
        if conn:
            conn.close()


def execute_query(query: str, params: tuple = (), fetch: str = None) -> Optional[list]:
    """
    Ejecuta una consulta SQL de forma segura.
    
    Args:
        query: Consulta SQL a ejecutar
        params: Parámetros para la consulta (tupla)
        fetch: Tipo de fetch ('one', 'all', None para INSERT/UPDATE/DELETE)
        
    Returns:
        list o dict o None según el tipo de fetch
        
    Raises:
        DbError: Si hay error en la ejecución
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        else:
            result = None
        
        conn.commit()
        return result
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DbError(f"Error al ejecutar consulta: {e}")
    finally:
        if conn:
            conn.close()
