"""
Modelo para la gestión de partidos.
"""
import sqlite3
from typing import Optional
from app.models.db import get_connection


class MatchModel:
    """Modelo para operaciones CRUD sobre la tabla partidos."""

    @staticmethod
    def crear_partido(
        eliminatoria: str, 
        slot: int, 
        local_id: int, 
        visitante_id: int,
        fecha_hora: Optional[str] = None,
        estado: str = "Pendiente"
    ) -> int:
        """
        Crea un nuevo partido en la base de datos.
        
        Args:
            eliminatoria: Nombre de la eliminatoria (ej: "Octavos", "Cuartos", "Semifinal", "Final")
            slot: Número de slot dentro de la eliminatoria
            local_id: ID del equipo local
            visitante_id: ID del equipo visitante
            fecha_hora: Fecha y hora del partido en formato "YYYY-MM-DD HH:MM:SS" (opcional)
            estado: Estado inicial del partido (por defecto "Pendiente", puede ser "Programado")
            
        Returns:
            ID del partido creado
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO partidos (
                eliminatoria, slot, fecha_hora,
                equipo_local_id, equipo_visitante_id,
                arbitro_id, goles_local, goles_visitante,
                penaltis_local, penaltis_visitante,
                ganador_equipo_id, estado
            ) VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL, ?)
        """, (eliminatoria, slot, fecha_hora, local_id, visitante_id, estado))
        
        conn.commit()
        partido_id = cursor.lastrowid
        conn.close()
        
        return partido_id

    @staticmethod
    def borrar_todos_los_partidos() -> None:
        """Elimina todos los partidos de la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM partidos")
        
        conn.commit()
        conn.close()

    @staticmethod
    def listar_partidos(
        eliminatoria: Optional[str] = None,
        estado: Optional[str] = None
    ) -> list[dict]:
        """
        Lista partidos con filtros opcionales.
        
        Args:
            eliminatoria: Filtrar por eliminatoria específica
            estado: Filtrar por estado ("Pendiente", "Jugado", etc.)
            
        Returns:
            Lista de diccionarios con los datos de los partidos
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Construcción de la consulta base con JOINs
        consulta = """
            SELECT 
                p.id, p.eliminatoria, p.slot, p.fecha_hora,
                p.equipo_local_id, el.nombre as local_nombre,
                p.equipo_visitante_id, ev.nombre as visitante_nombre,
                p.arbitro_id, 
                CASE 
                    WHEN pa.nombre IS NOT NULL THEN pa.nombre || ' ' || COALESCE(pa.apellidos, '')
                    ELSE NULL
                END as arbitro_nombre,
                p.goles_local, p.goles_visitante,
                p.penaltis_local, p.penaltis_visitante,
                p.ganador_equipo_id, p.estado
            FROM partidos p
            LEFT JOIN equipos el ON p.equipo_local_id = el.id
            LEFT JOIN equipos ev ON p.equipo_visitante_id = ev.id
            LEFT JOIN participantes pa ON p.arbitro_id = pa.id
            WHERE 1=1
        """
        parametros = []
        
        # Aplicar filtros
        if eliminatoria:
            consulta += " AND p.eliminatoria = ?"
            parametros.append(eliminatoria)
        
        if estado:
            consulta += " AND p.estado = ?"
            parametros.append(estado)
        
        consulta += " ORDER BY p.fecha_hora DESC, p.eliminatoria, p.slot"
        
        print(f"[APP-QUERY] SQL: {consulta}")
        print(f"[APP-QUERY] Params: {parametros}")
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        print(f"[APP-QUERY] Resultado: {len(filas)} partidos")
        if len(filas) > 0:
            print(f"[APP-QUERY] Primeros 3 partidos:")
            for i, fila in enumerate(filas[:3]):
                print(f"  [{i+1}] ID:{fila[0]} Fecha:{fila[3]} Local:{fila[5]} vs Visitante:{fila[7]} Estado:{fila[15]}")
        conn.close()
        
        partidos = []
        for fila in filas:
            partidos.append({
                "id": fila[0],
                "eliminatoria": fila[1],
                "slot": fila[2],
                "fecha_hora": fila[3],
                "local_id": fila[4],
                "equipo_local_id": fila[4],  # Alias para compatibilidad
                "local_nombre": fila[5],
                "visitante_id": fila[6],
                "equipo_visitante_id": fila[6],  # Alias para compatibilidad
                "visitante_nombre": fila[7],
                "arbitro_id": fila[8],
                "arbitro_nombre": fila[9],
                "goles_local": fila[10],
                "goles_visitante": fila[11],
                "penaltis_local": fila[12],
                "penaltis_visitante": fila[13],
                "ganador_equipo_id": fila[14],
                "estado": fila[15]
            })
        
        return partidos

    @staticmethod
    def obtener_partido_por_id(partido_id: int) -> Optional[dict]:
        """
        Obtiene un partido por su ID.
        
        Args:
            partido_id: ID del partido
            
        Returns:
            Diccionario con los datos del partido o None si no existe
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id, p.eliminatoria, p.slot, p.fecha_hora,
                p.equipo_local_id, el.nombre as local_nombre,
                p.equipo_visitante_id, ev.nombre as visitante_nombre,
                p.arbitro_id,
                CASE 
                    WHEN pa.nombre IS NOT NULL THEN pa.nombre || ' ' || COALESCE(pa.apellidos, '')
                    ELSE NULL
                END as arbitro_nombre,
                p.goles_local, p.goles_visitante,
                p.penaltis_local, p.penaltis_visitante,
                p.ganador_equipo_id, p.estado
            FROM partidos p
            LEFT JOIN equipos el ON p.equipo_local_id = el.id
            LEFT JOIN equipos ev ON p.equipo_visitante_id = ev.id
            LEFT JOIN participantes pa ON p.arbitro_id = pa.id
            WHERE p.id = ?
        """, (partido_id,))
        
        fila = cursor.fetchone()
        conn.close()
        
        if fila:
            return {
                "id": fila[0],
                "eliminatoria": fila[1],
                "slot": fila[2],
                "fecha_hora": fila[3],
                "local_id": fila[4],
                "equipo_local_id": fila[4],  # Alias para compatibilidad
                "local_nombre": fila[5],
                "visitante_id": fila[6],
                "equipo_visitante_id": fila[6],  # Alias para compatibilidad
                "visitante_nombre": fila[7],
                "arbitro_id": fila[8],
                "arbitro_nombre": fila[9],
                "goles_local": fila[10],
                "goles_visitante": fila[11],
                "penaltis_local": fila[12],
                "penaltis_visitante": fila[13],
                "ganador_equipo_id": fila[14],
                "estado": fila[15]
            }
        return None

    @staticmethod
    def asignar_arbitro(partido_id: int, arbitro_id: int) -> None:
        """
        Asigna un árbitro a un partido.
        
        Args:
            partido_id: ID del partido
            arbitro_id: ID del participante que actuará como árbitro
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE partidos SET arbitro_id = ? WHERE id = ?",
            (arbitro_id, partido_id)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def actualizar_fecha_hora(partido_id: int, fecha_hora: str) -> None:
        """
        Actualiza la fecha y hora de un partido.
        
        Args:
            partido_id: ID del partido
            fecha_hora: Nueva fecha y hora en formato "yyyy-MM-dd HH:mm"
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE partidos SET fecha_hora = ? WHERE id = ?",
            (fecha_hora, partido_id)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def obtener_partidos_por_fecha(fecha: str) -> list[dict]:
        """
        Obtiene los partidos programados para una fecha específica.
        
        Args:
            fecha: Fecha en formato "yyyy-MM-dd"
            
        Returns:
            Lista de diccionarios con los datos de los partidos
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        consulta = """
            SELECT 
                p.id, p.eliminatoria, p.slot, p.fecha_hora,
                p.equipo_local_id, el.nombre as local_nombre,
                p.equipo_visitante_id, ev.nombre as visitante_nombre,
                p.arbitro_id, 
                CASE 
                    WHEN pa.nombre IS NOT NULL THEN pa.nombre || ' ' || COALESCE(pa.apellidos, '')
                    ELSE NULL
                END as arbitro_nombre,
                p.goles_local, p.goles_visitante,
                p.penaltis_local, p.penaltis_visitante,
                p.ganador_equipo_id, p.estado
            FROM partidos p
            LEFT JOIN equipos el ON p.equipo_local_id = el.id
            LEFT JOIN equipos ev ON p.equipo_visitante_id = ev.id
            LEFT JOIN participantes pa ON p.arbitro_id = pa.id
            WHERE DATE(p.fecha_hora) = ?
            ORDER BY p.fecha_hora, p.slot
        """
        
        cursor.execute(consulta, (fecha,))
        filas = cursor.fetchall()
        conn.close()
        
        partidos = []
        for fila in filas:
            partidos.append({
                "id": fila[0],
                "eliminatoria": fila[1],
                "slot": fila[2],
                "fecha_hora": fila[3],
                "local_id": fila[4],
                "local_nombre": fila[5],
                "visitante_id": fila[6],
                "visitante_nombre": fila[7],
                "arbitro_id": fila[8],
                "arbitro_nombre": fila[9],
                "goles_local": fila[10],
                "goles_visitante": fila[11],
                "penaltis_local": fila[12],
                "penaltis_visitante": fila[13],
                "ganador_equipo_id": fila[14],
                "estado": fila[15]
            })
        return partidos
    
    @staticmethod
    def obtener_partidos_pendientes() -> list[dict]:
        """
        Obtiene los partidos sin fecha/hora asignada (pendientes de programar).
        
        Returns:
            Lista de diccionarios con los datos de los partidos pendientes
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        consulta = """
            SELECT 
                p.id, p.eliminatoria, p.slot, p.fecha_hora,
                p.equipo_local_id, el.nombre as local_nombre,
                p.equipo_visitante_id, ev.nombre as visitante_nombre,
                p.arbitro_id, 
                CASE 
                    WHEN pa.nombre IS NOT NULL THEN pa.nombre || ' ' || COALESCE(pa.apellidos, '')
                    ELSE NULL
                END as arbitro_nombre,
                p.goles_local, p.goles_visitante,
                p.penaltis_local, p.penaltis_visitante,
                p.ganador_equipo_id, p.estado
            FROM partidos p
            LEFT JOIN equipos el ON p.equipo_local_id = el.id
            LEFT JOIN equipos ev ON p.equipo_visitante_id = ev.id
            LEFT JOIN participantes pa ON p.arbitro_id = pa.id
            WHERE p.fecha_hora IS NULL
            ORDER BY p.eliminatoria, p.slot
        """
        
        cursor.execute(consulta)
        filas = cursor.fetchall()
        conn.close()
        
        partidos = []
        for fila in filas:
            partidos.append({
                "id": fila[0],
                "eliminatoria": fila[1],
                "slot": fila[2],
                "fecha_hora": fila[3],
                "local_id": fila[4],
                "local_nombre": fila[5],
                "visitante_id": fila[6],
                "visitante_nombre": fila[7],
                "arbitro_id": fila[8],
                "arbitro_nombre": fila[9],
                "goles_local": fila[10],
                "goles_visitante": fila[11],
                "penaltis_local": fila[12],
                "penaltis_visitante": fila[13],
                "ganador_equipo_id": fila[14],
                "estado": fila[15]
            })
        return partidos

    @staticmethod
    def obtener_partidos_por_fase(fase: str) -> list[dict]:
        """
        Obtiene los partidos de una fase específica.
        
        Args:
            fase: Nombre de la fase (octavos, cuartos, semifinal, final)
            
        Returns:
            Lista de diccionarios con los datos de los partidos
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        consulta = """
            SELECT 
                p.id, p.eliminatoria, p.slot, p.fecha_hora,
                p.equipo_local_id, el.nombre as local_nombre,
                p.equipo_visitante_id, ev.nombre as visitante_nombre,
                p.arbitro_id, 
                CASE 
                    WHEN pa.nombre IS NOT NULL THEN pa.nombre || ' ' || COALESCE(pa.apellidos, '')
                    ELSE NULL
                END as arbitro_nombre,
                p.goles_local, p.goles_visitante,
                p.penaltis_local, p.penaltis_visitante,
                p.ganador_equipo_id, p.estado
            FROM partidos p
            LEFT JOIN equipos el ON p.equipo_local_id = el.id
            LEFT JOIN equipos ev ON p.equipo_visitante_id = ev.id
            LEFT JOIN participantes pa ON p.arbitro_id = pa.id
            WHERE p.eliminatoria = ?
            ORDER BY p.slot
        """
        
        cursor.execute(consulta, (fase,))
        filas = cursor.fetchall()
        conn.close()
        
        partidos = []
        for fila in filas:
            partidos.append({
                "id": fila[0],
                "eliminatoria": fila[1],
                "slot": fila[2],
                "fecha_hora": fila[3],
                "local_id": fila[4],
                "local_nombre": fila[5],
                "visitante_id": fila[6],
                "visitante_nombre": fila[7],
                "arbitro_id": fila[8],
                "arbitro_nombre": fila[9],
                "goles_local": fila[10],
                "goles_visitante": fila[11],
                "penaltis_local": fila[12],
                "penaltis_visitante": fila[13],
                "ganador_equipo_id": fila[14],
                "estado": fila[15]
            })
        return partidos

    @staticmethod
    def quitar_arbitro(partido_id: int) -> None:
        """
        Quita el árbitro asignado a un partido.
        
        Args:
            partido_id: ID del partido
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE partidos SET arbitro_id = NULL WHERE id = ?",
            (partido_id,)
        )
        
        conn.commit()
        conn.close()

    @staticmethod
    def guardar_resultado(
        partido_id: int,
        goles_local: int,
        goles_visitante: int,
        penaltis_local: Optional[int] = None,
        penaltis_visitante: Optional[int] = None
    ) -> dict:
        """
        Guarda el resultado de un partido y determina el ganador.
        
        Args:
            partido_id: ID del partido
            goles_local: Goles del equipo local
            goles_visitante: Goles del equipo visitante
            penaltis_local: Goles en penaltis del equipo local (opcional)
            penaltis_visitante: Goles en penaltis del equipo visitante (opcional)
            
        Returns:
            Diccionario con ganador_equipo_id, estado actualizado y estado_previo
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener datos del partido incluyendo estado previo
        cursor.execute(
            "SELECT equipo_local_id, equipo_visitante_id, estado FROM partidos WHERE id = ?",
            (partido_id,)
        )
        fila = cursor.fetchone()
        
        if not fila:
            conn.close()
            raise ValueError(f"Partido con ID {partido_id} no encontrado")
        
        local_id, visitante_id, estado_previo = fila
        
        # Determinar ganador
        ganador_equipo_id = None
        
        if goles_local > goles_visitante:
            ganador_equipo_id = local_id
        elif goles_visitante > goles_local:
            ganador_equipo_id = visitante_id
        else:
            # Empate en tiempo regular, verificar penaltis
            if penaltis_local is not None and penaltis_visitante is not None:
                if penaltis_local > penaltis_visitante:
                    ganador_equipo_id = local_id
                elif penaltis_visitante > penaltis_local:
                    ganador_equipo_id = visitante_id
                # Si también empatan en penaltis, ganador_equipo_id queda None
        
        # Actualizar partido
        cursor.execute("""
            UPDATE partidos 
            SET goles_local = ?,
                goles_visitante = ?,
                penaltis_local = ?,
                penaltis_visitante = ?,
                ganador_equipo_id = ?,
                estado = 'Jugado'
            WHERE id = ?
        """, (goles_local, goles_visitante, penaltis_local, penaltis_visitante, 
              ganador_equipo_id, partido_id))
        
        conn.commit()
        conn.close()
        
        return {
            "ganador_equipo_id": ganador_equipo_id,
            "estado": "Jugado",
            "estado_previo": estado_previo
        }

    @staticmethod
    def insertar_partido(
        eliminatoria: str,
        fecha_hora: str,
        local_id: int,
        visitante_id: int,
        estado: str = 'Programado',
        arbitro_id: Optional[int] = None
    ) -> int:
        """
        Inserta un nuevo partido en la base de datos.
        
        Args:
            eliminatoria: Nombre de la ronda (ej: "Jornada 1", "Octavos", etc.)
            fecha_hora: Fecha y hora en formato "yyyy-MM-dd HH:mm:ss"
            local_id: ID del equipo local
            visitante_id: ID del equipo visitante
            estado: Estado del partido (default: 'Programado')
            arbitro_id: ID del árbitro (opcional)
            
        Returns:
            ID del partido creado
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener el siguiente slot para esta eliminatoria
        cursor.execute(
            "SELECT COALESCE(MAX(slot), 0) + 1 FROM partidos WHERE eliminatoria = ?",
            (eliminatoria,)
        )
        slot = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO partidos (
                eliminatoria, slot, fecha_hora,
                equipo_local_id, equipo_visitante_id,
                arbitro_id, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (eliminatoria, slot, fecha_hora, local_id, visitante_id, arbitro_id, estado))
        
        conn.commit()
        partido_id = cursor.lastrowid
        conn.close()
        
        return partido_id

    @staticmethod
    def actualizar_partido(
        partido_id: int,
        eliminatoria: str,
        fecha_hora: str,
        local_id: int,
        visitante_id: int,
        estado: str,
        arbitro_id: Optional[int] = None
    ) -> None:
        """
        Actualiza un partido existente.
        
        Args:
            partido_id: ID del partido a actualizar
            eliminatoria: Nombre de la ronda
            fecha_hora: Fecha y hora en formato "yyyy-MM-dd HH:mm:ss"
            local_id: ID del equipo local
            visitante_id: ID del equipo visitante
            estado: Estado del partido
            arbitro_id: ID del árbitro (opcional)
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE partidos 
            SET eliminatoria = ?,
                fecha_hora = ?,
                equipo_local_id = ?,
                equipo_visitante_id = ?,
                estado = ?,
                arbitro_id = ?
            WHERE id = ?
        """, (eliminatoria, fecha_hora, local_id, visitante_id, estado, arbitro_id, partido_id))
        
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar_partido(partido_id: int) -> None:
        """
        Elimina un partido de la base de datos.
        
        Args:
            partido_id: ID del partido a eliminar
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Primero eliminar convocados asociados
        cursor.execute("DELETE FROM convocados WHERE partido_id = ?", (partido_id,))
        
        # Luego eliminar estadísticas asociadas
        cursor.execute("DELETE FROM stats_partido WHERE partido_id = ?", (partido_id,))
        
        # Finalmente eliminar el partido
        cursor.execute("DELETE FROM partidos WHERE id = ?", (partido_id,))
        
        conn.commit()
        conn.close()

    @staticmethod
    def obtener_fechas_con_partidos() -> list[str]:
        """
        Obtiene todas las fechas que tienen partidos programados.
        
        Returns:
            Lista de fechas en formato "yyyy-MM-dd"
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT DATE(fecha_hora) as fecha
            FROM partidos
            WHERE fecha_hora IS NOT NULL
            ORDER BY fecha
        """)
        
        filas = cursor.fetchall()
        conn.close()
        
        return [fila[0] for fila in filas if fila[0]]
