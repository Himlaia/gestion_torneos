"""Modelo de datos para equipos."""
import sqlite3
from typing import Optional
from app.models.db import get_connection, DbError


class TeamModel:
    """Modelo para gestionar equipos en la base de datos."""
    
    @staticmethod
    def crear_equipo(nombre: str, curso: str, color: str, escudo_path: Optional[str] = None) -> int:
        """
        Crea un nuevo equipo en la base de datos.
        
        Args:
            nombre: Nombre del equipo (debe ser único)
            curso: Curso del equipo
            color: Colores del equipo
            escudo_path: Ruta al archivo del escudo (opcional)
            
        Returns:
            ID del equipo creado
            
        Raises:
            ValueError: Si el nombre ya existe
            DbError: Si hay error en la base de datos
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO equipos (nombre, curso, color, escudo_path)
                VALUES (?, ?, ?, ?)
            """, (nombre, curso, color, escudo_path))
            
            equipo_id = cursor.lastrowid
            conn.commit()
            return equipo_id
            
        except sqlite3.IntegrityError as e:
            if conn:
                conn.rollback()
            if "UNIQUE constraint failed: equipos.nombre" in str(e):
                raise ValueError(f"Ya existe un equipo con el nombre '{nombre}'")
            raise DbError(f"Error de integridad al crear equipo: {e}")
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DbError(f"Error al crear equipo: {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def actualizar_equipo(
        equipo_id: int,
        nombre: str,
        curso: str,
        color: str,
        escudo_path: Optional[str] = None
    ) -> None:
        """
        Actualiza un equipo existente.
        
        Args:
            equipo_id: ID del equipo a actualizar
            nombre: Nuevo nombre del equipo
            curso: Nuevo curso del equipo
            color: Nuevos colores del equipo
            escudo_path: Nueva ruta al escudo (opcional)
            
        Raises:
            ValueError: Si el nombre ya existe en otro equipo
            DbError: Si hay error en la base de datos
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE equipos
                SET nombre = ?, curso = ?, color = ?, escudo_path = ?
                WHERE id = ?
            """, (nombre, curso, color, escudo_path, equipo_id))
            
            conn.commit()
            
        except sqlite3.IntegrityError as e:
            if conn:
                conn.rollback()
            if "UNIQUE constraint failed: equipos.nombre" in str(e):
                raise ValueError(f"Ya existe un equipo con el nombre '{nombre}'")
            raise DbError(f"Error de integridad al actualizar equipo: {e}")
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DbError(f"Error al actualizar equipo: {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def eliminar_equipo(equipo_id: int) -> None:
        """
        Elimina un equipo de la base de datos.
        
        Args:
            equipo_id: ID del equipo a eliminar
            
        Raises:
            DbError: Si hay error en la base de datos
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM equipos WHERE id = ?", (equipo_id,))
            conn.commit()
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DbError(f"Error al eliminar equipo: {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def obtener_equipo_por_id(equipo_id: int) -> Optional[dict]:
        """
        Obtiene un equipo por su ID.
        
        Args:
            equipo_id: ID del equipo a buscar
            
        Returns:
            Diccionario con los datos del equipo o None si no existe
            
        Raises:
            DbError: Si hay error en la base de datos
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nombre, curso, color, escudo_path
                FROM equipos
                WHERE id = ?
            """, (equipo_id,))
            
            row = cursor.fetchone()
            
            if row:
                # Obtener número de jugadores
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM participantes
                    WHERE equipo_id = ?
                """, (equipo_id,))
                num_jugadores = cursor.fetchone()['count']
                
                return {
                    'id': row['id'],
                    'nombre': row['nombre'],
                    'curso': row['curso'],
                    'color': row['color'],
                    'escudo_path': row['escudo_path'] or '',
                    'num_jugadores': num_jugadores
                }
            return None
            
        except sqlite3.Error as e:
            raise DbError(f"Error al obtener equipo: {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def listar_equipos(busqueda: Optional[str] = None) -> list[dict]:
        """
        Lista todos los equipos, opcionalmente filtrados por búsqueda.
        
        Args:
            busqueda: Texto a buscar en el nombre del equipo (opcional)
            
        Returns:
            Lista de diccionarios con los datos de los equipos
            
        Raises:
            DbError: Si hay error en la base de datos
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if busqueda:
                cursor.execute("""
                    SELECT id, nombre, curso, color, escudo_path
                    FROM equipos
                    WHERE nombre LIKE ?
                    ORDER BY nombre
                """, (f"%{busqueda}%",))
            else:
                cursor.execute("""
                    SELECT id, nombre, curso, color, escudo_path
                    FROM equipos
                    ORDER BY nombre
                """)
            
            rows = cursor.fetchall()
            
            # Obtener conteo de jugadores para todos los equipos
            conteos = TeamModel.contar_jugadores_por_equipo()
            
            equipos = []
            for row in rows:
                equipo_id = row['id']
                equipos.append({
                    'id': equipo_id,
                    'nombre': row['nombre'],
                    'curso': row['curso'],
                    'color': row['color'],
                    'escudo_path': row['escudo_path'] or '',
                    'num_jugadores': conteos.get(equipo_id, 0)
                })
            
            return equipos
            
        except sqlite3.Error as e:
            raise DbError(f"Error al listar equipos: {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def contar_jugadores_por_equipo() -> dict[int, int]:
        """
        Cuenta el número de jugadores por equipo.
        
        Returns:
            Diccionario con {equipo_id: num_jugadores}
            
        Raises:
            DbError: Si hay error en la base de datos
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT equipo_id, COUNT(*) as count
                FROM participantes
                WHERE equipo_id IS NOT NULL
                GROUP BY equipo_id
            """)
            
            rows = cursor.fetchall()
            return {row['equipo_id']: row['count'] for row in rows}
            
        except sqlite3.Error as e:
            raise DbError(f"Error al contar jugadores: {e}")
        finally:
            if conn:
                conn.close()
