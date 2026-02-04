"""
Modelo para la gestión de convocatorias de partidos.
"""
import sqlite3
from app.models.db import get_connection


class CallupModel:
    """Modelo para operaciones CRUD sobre la tabla convocados."""

    @staticmethod
    def listar_convocados(partido_id: int) -> list[dict]:
        """
        Lista todos los jugadores convocados para un partido.
        
        Args:
            partido_id: ID del partido
            
        Returns:
            Lista de diccionarios con los datos de los convocados
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.participante_id,
                p.nombre,
                p.apellidos,
                c.equipo_id,
                e.nombre as equipo_nombre
            FROM convocados c
            INNER JOIN participantes p ON c.participante_id = p.id
            INNER JOIN equipos e ON c.equipo_id = e.id
            WHERE c.partido_id = ?
            ORDER BY e.nombre, p.apellidos, p.nombre
        """, (partido_id,))
        
        filas = cursor.fetchall()
        conn.close()
        
        convocados = []
        for fila in filas:
            convocados.append({
                "participante_id": fila[0],
                "nombre": fila[1],
                "apellidos": fila[2],
                "equipo_id": fila[3],
                "equipo_nombre": fila[4]
            })
        
        return convocados

    @staticmethod
    def listar_convocados_por_equipo(partido_id: int, equipo_id: int) -> list[dict]:
        """
        Lista los jugadores convocados de un equipo específico para un partido.
        
        Args:
            partido_id: ID del partido
            equipo_id: ID del equipo
            
        Returns:
            Lista de diccionarios con los datos de los convocados del equipo
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.participante_id,
                p.nombre,
                p.apellidos,
                c.equipo_id,
                e.nombre as equipo_nombre
            FROM convocados c
            INNER JOIN participantes p ON c.participante_id = p.id
            INNER JOIN equipos e ON c.equipo_id = e.id
            WHERE c.partido_id = ? AND c.equipo_id = ?
            ORDER BY p.apellidos, p.nombre
        """, (partido_id, equipo_id))
        
        filas = cursor.fetchall()
        conn.close()
        
        convocados = []
        for fila in filas:
            convocados.append({
                "participante_id": fila[0],
                "nombre": fila[1],
                "apellidos": fila[2],
                "equipo_id": fila[3],
                "equipo_nombre": fila[4]
            })
        
        return convocados

    @staticmethod
    def convocar_jugador(partido_id: int, participante_id: int, equipo_id: int) -> None:
        """
        Convoca un jugador para un partido.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del participante (jugador)
            equipo_id: ID del equipo al que pertenece
            
        Raises:
            sqlite3.IntegrityError: Si el jugador ya está convocado para este partido
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO convocados (partido_id, participante_id, equipo_id)
                VALUES (?, ?, ?)
            """, (partido_id, participante_id, equipo_id))
            
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.close()
            raise sqlite3.IntegrityError(
                f"El jugador ya está convocado para este partido"
            ) from e
        finally:
            if conn:
                conn.close()

    @staticmethod
    def quitar_convocado(partido_id: int, participante_id: int) -> None:
        """
        Quita un jugador de la convocatoria de un partido.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del participante a quitar
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM convocados 
            WHERE partido_id = ? AND participante_id = ?
        """, (partido_id, participante_id))
        
        conn.commit()
        conn.close()

    @staticmethod
    def limpiar_convocados(partido_id: int) -> None:
        """
        Elimina todos los convocados de un partido.
        
        Args:
            partido_id: ID del partido
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM convocados WHERE partido_id = ?
        """, (partido_id,))
        
        conn.commit()
        conn.close()

    @staticmethod
    def esta_convocado(partido_id: int, participante_id: int) -> bool:
        """
        Verifica si un jugador ya está convocado para un partido.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del participante
            
        Returns:
            True si el jugador está convocado, False en caso contrario
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM convocados 
            WHERE partido_id = ? AND participante_id = ?
        """, (partido_id, participante_id))
        
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0] > 0

    @staticmethod
    def contar_convocados_equipo(partido_id: int, equipo_id: int) -> int:
        """
        Cuenta cuántos jugadores tiene convocados un equipo para un partido.
        
        Args:
            partido_id: ID del partido
            equipo_id: ID del equipo
            
        Returns:
            Número de jugadores convocados
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM convocados 
            WHERE partido_id = ? AND equipo_id = ?
        """, (partido_id, equipo_id))
        
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0]
    
    @staticmethod
    def obtener_convocados_equipo(partido_id: int, equipo_id: int) -> list[dict]:
        """
        Alias de listar_convocados_por_equipo para compatibilidad.
        
        Args:
            partido_id: ID del partido
            equipo_id: ID del equipo
            
        Returns:
            Lista de diccionarios con los datos de los convocados del equipo
        """
        return CallupModel.listar_convocados_por_equipo(partido_id, equipo_id)
