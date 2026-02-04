"""Modelo para operaciones CRUD sobre la tabla goles."""
from typing import Optional
from app.models.db import get_connection


class GoalModel:
    """Modelo para gestionar los goles con autor en partidos."""
    
    @staticmethod
    def registrar_gol(
        partido_id: int,
        participante_id: int,
        equipo_id: int,
        minuto: Optional[int] = None
    ) -> int:
        """
        Registra un gol con autor específico.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del jugador que marcó
            equipo_id: ID del equipo del jugador
            minuto: Minuto en que se marcó (opcional)
            
        Returns:
            ID del gol registrado
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO goles (partido_id, participante_id, equipo_id, minuto)
            VALUES (?, ?, ?, ?)
        """, (partido_id, participante_id, equipo_id, minuto))
        
        gol_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return gol_id
    
    @staticmethod
    def obtener_goles_partido(partido_id: int) -> list[dict]:
        """
        Obtiene todos los goles de un partido.
        
        Args:
            partido_id: ID del partido
            
        Returns:
            Lista de diccionarios con información de los goles
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                g.id,
                g.partido_id,
                g.participante_id,
                p.nombre || ' ' || COALESCE(p.apellidos, '') as jugador_nombre,
                g.equipo_id,
                e.nombre as equipo_nombre,
                g.minuto
            FROM goles g
            INNER JOIN participantes p ON g.participante_id = p.id
            INNER JOIN equipos e ON g.equipo_id = e.id
            WHERE g.partido_id = ?
            ORDER BY COALESCE(g.minuto, 999), g.id
        """, (partido_id,))
        
        filas = cursor.fetchall()
        conn.close()
        
        goles = []
        for fila in filas:
            goles.append({
                "id": fila[0],
                "partido_id": fila[1],
                "participante_id": fila[2],
                "jugador_nombre": fila[3].strip(),
                "equipo_id": fila[4],
                "equipo_nombre": fila[5],
                "minuto": fila[6]
            })
        
        return goles
    
    @staticmethod
    def obtener_goles_equipo_partido(partido_id: int, equipo_id: int) -> list[dict]:
        """
        Obtiene los goles de un equipo específico en un partido.
        
        Args:
            partido_id: ID del partido
            equipo_id: ID del equipo
            
        Returns:
            Lista de diccionarios con información de los goles
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                g.id,
                g.participante_id,
                p.nombre || ' ' || COALESCE(p.apellidos, '') as jugador_nombre,
                g.minuto
            FROM goles g
            INNER JOIN participantes p ON g.participante_id = p.id
            WHERE g.partido_id = ? AND g.equipo_id = ?
            ORDER BY COALESCE(g.minuto, 999), g.id
        """, (partido_id, equipo_id))
        
        filas = cursor.fetchall()
        conn.close()
        
        goles = []
        for fila in filas:
            goles.append({
                "id": fila[0],
                "participante_id": fila[1],
                "jugador_nombre": fila[2].strip(),
                "minuto": fila[3]
            })
        
        return goles
    
    @staticmethod
    def eliminar_gol(gol_id: int) -> None:
        """
        Elimina un gol específico.
        
        Args:
            gol_id: ID del gol a eliminar
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM goles WHERE id = ?", (gol_id,))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def limpiar_goles_partido(partido_id: int) -> None:
        """
        Elimina todos los goles de un partido.
        
        Args:
            partido_id: ID del partido
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM goles WHERE partido_id = ?", (partido_id,))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def contar_goles_equipo_partido(partido_id: int, equipo_id: int) -> int:
        """
        Cuenta los goles de un equipo en un partido.
        
        Args:
            partido_id: ID del partido
            equipo_id: ID del equipo
            
        Returns:
            Número de goles
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM goles 
            WHERE partido_id = ? AND equipo_id = ?
        """, (partido_id, equipo_id))
        
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0] if resultado else 0
    
    @staticmethod
    def actualizar_minuto(gol_id: int, minuto: Optional[int]) -> None:
        """
        Actualiza el minuto de un gol.
        
        Args:
            gol_id: ID del gol
            minuto: Nuevo minuto (puede ser None)
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE goles 
            SET minuto = ?
            WHERE id = ?
        """, (minuto, gol_id))
        
        conn.commit()
        conn.close()
