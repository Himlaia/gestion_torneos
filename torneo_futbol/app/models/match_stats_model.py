"""
Modelo para la gestión de estadísticas de partidos.
"""
import sqlite3
from app.models.db import get_connection


class MatchStatsModel:
    """Modelo para operaciones CRUD sobre la tabla stats_partido."""

    @staticmethod
    def inicializar_stats(partido_id: int, participante_ids: list[int]) -> None:
        """
        Inicializa las estadísticas para los participantes de un partido.
        Inserta filas con valores 0 si no existen.
        
        Args:
            partido_id: ID del partido
            participante_ids: Lista de IDs de participantes a inicializar
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        for participante_id in participante_ids:
            # Verificar si ya existe
            cursor.execute("""
                SELECT COUNT(*) FROM stats_partido 
                WHERE partido_id = ? AND participante_id = ?
            """, (partido_id, participante_id))
            
            existe = cursor.fetchone()[0] > 0
            
            if not existe:
                # Insertar con valores iniciales en 0
                cursor.execute("""
                    INSERT INTO stats_partido (partido_id, participante_id, goles, amarillas, rojas)
                    VALUES (?, ?, 0, 0, 0)
                """, (partido_id, participante_id))
        
        conn.commit()
        conn.close()

    @staticmethod
    def obtener_stats(partido_id: int) -> list[dict]:
        """
        Obtiene todas las estadísticas de un partido.
        
        Args:
            partido_id: ID del partido
            
        Returns:
            Lista de diccionarios con las estadísticas de cada participante
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sp.participante_id,
                p.nombre,
                p.apellidos,
                e.nombre as equipo_nombre,
                sp.goles,
                sp.amarillas,
                sp.rojas
            FROM stats_partido sp
            INNER JOIN participantes p ON sp.participante_id = p.id
            LEFT JOIN equipos e ON p.equipo_id = e.id
            WHERE sp.partido_id = ?
            ORDER BY e.nombre, p.apellidos, p.nombre
        """, (partido_id,))
        
        filas = cursor.fetchall()
        conn.close()
        
        stats = []
        for fila in filas:
            stats.append({
                "participante_id": fila[0],
                "nombre": fila[1],
                "apellidos": fila[2],
                "equipo_nombre": fila[3],
                "goles": fila[4],
                "amarillas": fila[5],
                "rojas": fila[6]
            })
        
        return stats

    @staticmethod
    def guardar_stats(partido_id: int, stats: list[dict]) -> None:
        """
        Guarda las estadísticas de múltiples participantes en un partido.
        
        Args:
            partido_id: ID del partido
            stats: Lista de diccionarios con participante_id, goles, amarillas, rojas
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        for stat in stats:
            participante_id = stat.get("participante_id")
            goles = stat.get("goles", 0)
            amarillas = stat.get("amarillas", 0)
            rojas = stat.get("rojas", 0)
            
            if participante_id is None:
                continue
            
            # Verificar si ya existe
            cursor.execute("""
                SELECT COUNT(*) FROM stats_partido 
                WHERE partido_id = ? AND participante_id = ?
            """, (partido_id, participante_id))
            
            existe = cursor.fetchone()[0] > 0
            
            if existe:
                # Actualizar
                cursor.execute("""
                    UPDATE stats_partido 
                    SET goles = ?, amarillas = ?, rojas = ?
                    WHERE partido_id = ? AND participante_id = ?
                """, (goles, amarillas, rojas, partido_id, participante_id))
            else:
                # Insertar
                cursor.execute("""
                    INSERT INTO stats_partido (partido_id, participante_id, goles, amarillas, rojas)
                    VALUES (?, ?, ?, ?, ?)
                """, (partido_id, participante_id, goles, amarillas, rojas))
        
        conn.commit()
        conn.close()

    @staticmethod
    def obtener_stats_participante(partido_id: int, participante_id: int) -> dict:
        """
        Obtiene las estadísticas de un participante específico en un partido.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del participante
            
        Returns:
            Diccionario con las estadísticas o None si no existe
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sp.participante_id,
                p.nombre,
                p.apellidos,
                e.nombre as equipo_nombre,
                sp.goles,
                sp.amarillas,
                sp.rojas
            FROM stats_partido sp
            INNER JOIN participantes p ON sp.participante_id = p.id
            LEFT JOIN equipos e ON p.equipo_id = e.id
            WHERE sp.partido_id = ? AND sp.participante_id = ?
        """, (partido_id, participante_id))
        
        fila = cursor.fetchone()
        conn.close()
        
        if fila:
            return {
                "participante_id": fila[0],
                "nombre": fila[1],
                "apellidos": fila[2],
                "equipo_nombre": fila[3],
                "goles": fila[4],
                "amarillas": fila[5],
                "rojas": fila[6]
            }
        return None

    @staticmethod
    def limpiar_stats(partido_id: int) -> None:
        """
        Elimina todas las estadísticas de un partido.
        
        Args:
            partido_id: ID del partido
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM stats_partido WHERE partido_id = ?
        """, (partido_id,))
        
        conn.commit()
        conn.close()

    @staticmethod
    def actualizar_stat_participante(
        partido_id: int, 
        participante_id: int, 
        goles: int = 0, 
        amarillas: int = 0, 
        rojas: int = 0
    ) -> None:
        """
        Actualiza o crea las estadísticas de un participante en un partido.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del participante
            goles: Número de goles
            amarillas: Número de tarjetas amarillas
            rojas: Número de tarjetas rojas
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute("""
            SELECT COUNT(*) FROM stats_partido 
            WHERE partido_id = ? AND participante_id = ?
        """, (partido_id, participante_id))
        
        existe = cursor.fetchone()[0] > 0
        
        if existe:
            # Actualizar
            cursor.execute("""
                UPDATE stats_partido 
                SET goles = ?, amarillas = ?, rojas = ?
                WHERE partido_id = ? AND participante_id = ?
            """, (goles, amarillas, rojas, partido_id, participante_id))
        else:
            # Insertar
            cursor.execute("""
                INSERT INTO stats_partido (partido_id, participante_id, goles, amarillas, rojas)
                VALUES (?, ?, ?, ?, ?)
            """, (partido_id, participante_id, goles, amarillas, rojas))
        
        conn.commit()
        conn.close()

    @staticmethod
    def limpiar_stats_partido(partido_id: int) -> None:
        """
        Alias para limpiar_stats. Elimina todas las estadísticas de un partido.
        
        Args:
            partido_id: ID del partido
        """
        MatchStatsModel.limpiar_stats(partido_id)

    @staticmethod
    def registrar_gol(partido_id: int, participante_id: int) -> None:
        """
        Registra un gol de un participante en un partido.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del participante
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe registro
        cursor.execute("""
            SELECT goles FROM stats_partido 
            WHERE partido_id = ? AND participante_id = ?
        """, (partido_id, participante_id))
        
        resultado = cursor.fetchone()
        
        if resultado:
            # Incrementar goles
            nuevo_goles = resultado[0] + 1
            cursor.execute("""
                UPDATE stats_partido 
                SET goles = ?
                WHERE partido_id = ? AND participante_id = ?
            """, (nuevo_goles, partido_id, participante_id))
        else:
            # Crear registro con 1 gol
            cursor.execute("""
                INSERT INTO stats_partido (partido_id, participante_id, goles, amarillas, rojas)
                VALUES (?, ?, 1, 0, 0)
            """, (partido_id, participante_id))
        
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_tarjeta_amarilla(partido_id: int, participante_id: int) -> None:
        """
        Registra una tarjeta amarilla de un participante en un partido.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del participante
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe registro
        cursor.execute("""
            SELECT amarillas FROM stats_partido 
            WHERE partido_id = ? AND participante_id = ?
        """, (partido_id, participante_id))
        
        resultado = cursor.fetchone()
        
        if resultado:
            # Incrementar amarillas
            nuevo_amarillas = resultado[0] + 1
            cursor.execute("""
                UPDATE stats_partido 
                SET amarillas = ?
                WHERE partido_id = ? AND participante_id = ?
            """, (nuevo_amarillas, partido_id, participante_id))
        else:
            # Crear registro con 1 amarilla
            cursor.execute("""
                INSERT INTO stats_partido (partido_id, participante_id, goles, amarillas, rojas)
                VALUES (?, ?, 0, 1, 0)
            """, (partido_id, participante_id))
        
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_tarjeta_roja(partido_id: int, participante_id: int) -> None:
        """
        Registra una tarjeta roja de un participante en un partido.
        
        Args:
            partido_id: ID del partido
            participante_id: ID del participante
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe registro
        cursor.execute("""
            SELECT rojas FROM stats_partido 
            WHERE partido_id = ? AND participante_id = ?
        """, (partido_id, participante_id))
        
        resultado = cursor.fetchone()
        
        if resultado:
            # Incrementar rojas
            nuevo_rojas = resultado[0] + 1
            cursor.execute("""
                UPDATE stats_partido 
                SET rojas = ?
                WHERE partido_id = ? AND participante_id = ?
            """, (nuevo_rojas, partido_id, participante_id))
        else:
            # Crear registro con 1 roja
            cursor.execute("""
                INSERT INTO stats_partido (partido_id, participante_id, goles, amarillas, rojas)
                VALUES (?, ?, 0, 0, 1)
            """, (partido_id, participante_id))
        
        conn.commit()
        conn.close()
