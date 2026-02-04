"""
Modelo para la gestión de participantes (jugadores y árbitros).
"""
import sqlite3
from typing import Optional
from app.models.db import get_connection


class ParticipantModel:
    """Modelo para operaciones CRUD sobre la tabla participantes."""

    @staticmethod
    def crear_participante(datos: dict) -> int:
        """
        Crea un nuevo participante en la base de datos.
        
        Args:
            datos: Diccionario con los datos del participante
            
        Returns:
            ID del participante creado
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Valores por defecto
        nombre = datos.get("nombre", "")
        apellidos = datos.get("apellidos")
        fecha_nacimiento = datos.get("fecha_nacimiento", "")
        curso = datos.get("curso", "")
        tipo_jugador = datos.get("tipo_jugador", "Jugador")
        posicion = datos.get("posicion", "")
        t_amarillas = datos.get("t_amarillas", 0)
        t_rojas = datos.get("t_rojas", 0)
        goles = datos.get("goles", 0)
        equipo_id = datos.get("equipo_id")
        
        cursor.execute("""
            INSERT INTO participantes (
                nombre, apellidos, fecha_nacimiento, curso,
                tipo_jugador, posicion, t_amarillas, t_rojas, goles, equipo_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre, apellidos, fecha_nacimiento, curso, tipo_jugador, 
              posicion, t_amarillas, t_rojas, goles, equipo_id))
        
        conn.commit()
        participante_id = cursor.lastrowid
        conn.close()
        
        return participante_id

    @staticmethod
    def actualizar_participante(participante_id: int, datos: dict) -> None:
        """
        Actualiza los datos de un participante existente.
        
        Args:
            participante_id: ID del participante a actualizar
            datos: Diccionario con los nuevos datos
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Construir la consulta dinámicamente según los campos presentes
        campos = []
        valores = []
        
        if "nombre" in datos:
            campos.append("nombre = ?")
            valores.append(datos["nombre"])
        if "apellidos" in datos:
            campos.append("apellidos = ?")
            valores.append(datos["apellidos"])
        if "fecha_nacimiento" in datos:
            campos.append("fecha_nacimiento = ?")
            valores.append(datos["fecha_nacimiento"])
        if "curso" in datos:
            campos.append("curso = ?")
            valores.append(datos["curso"])
        if "tipo_jugador" in datos:
            campos.append("tipo_jugador = ?")
            valores.append(datos["tipo_jugador"])
        if "posicion" in datos:
            campos.append("posicion = ?")
            valores.append(datos["posicion"])
        if "t_amarillas" in datos:
            campos.append("t_amarillas = ?")
            valores.append(datos["t_amarillas"])
        if "t_rojas" in datos:
            campos.append("t_rojas = ?")
            valores.append(datos["t_rojas"])
        if "goles" in datos:
            campos.append("goles = ?")
            valores.append(datos["goles"])
        if "equipo_id" in datos:
            campos.append("equipo_id = ?")
            valores.append(datos["equipo_id"])
        
        if campos:
            valores.append(participante_id)
            consulta = f"UPDATE participantes SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(consulta, valores)
            conn.commit()
        
        conn.close()

    @staticmethod
    def eliminar_participante(participante_id: int) -> None:
        """
        Elimina un participante de la base de datos.
        
        Args:
            participante_id: ID del participante a eliminar
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM participantes WHERE id = ?", (participante_id,))
        
        conn.commit()
        conn.close()

    @staticmethod
    def obtener_participante_por_id(participante_id: int) -> Optional[dict]:
        """
        Obtiene un participante por su ID.
        
        Args:
            participante_id: ID del participante
            
        Returns:
            Diccionario con los datos del participante o None si no existe
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id, p.nombre, p.apellidos, p.fecha_nacimiento, p.curso,
                p.tipo_jugador, p.posicion, p.t_amarillas, p.t_rojas, p.goles,
                p.equipo_id, e.nombre as equipo_nombre
            FROM participantes p
            LEFT JOIN equipos e ON p.equipo_id = e.id
            WHERE p.id = ?
        """, (participante_id,))
        
        fila = cursor.fetchone()
        conn.close()
        
        if fila:
            return {
                "id": fila[0],
                "nombre": fila[1],
                "apellidos": fila[2],
                "fecha_nacimiento": fila[3],
                "curso": fila[4],
                "tipo_jugador": fila[5],
                "posicion": fila[6],
                "t_amarillas": fila[7],
                "t_rojas": fila[8],
                "goles": fila[9],
                "equipo_id": fila[10],
                "equipo_nombre": fila[11]
            }
        return None

    @staticmethod
    def listar_participantes(
        busqueda: Optional[str] = None,
        filtro_rol: Optional[str] = None,
        filtro_equipo_id: Optional[int] = None,
        filtro_curso: Optional[str] = None
    ) -> list[dict]:
        """
        Lista participantes con filtros opcionales.
        
        Args:
            busqueda: Texto para buscar en nombre o apellidos
            filtro_rol: "Todos"|"Jugadores"|"Árbitros"|"Ambos"
            filtro_equipo_id: ID del equipo para filtrar
            filtro_curso: "Todos"|"1º ESO"|"2º ESO"|etc.
            
        Returns:
            Lista de diccionarios con los datos de los participantes
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Construcción de la consulta base
        consulta = """
            SELECT 
                p.id, p.nombre, p.apellidos, p.fecha_nacimiento, p.curso,
                p.tipo_jugador, p.posicion, p.t_amarillas, p.t_rojas, p.goles,
                p.equipo_id, e.nombre as equipo_nombre
            FROM participantes p
            LEFT JOIN equipos e ON p.equipo_id = e.id
            WHERE 1=1
        """
        parametros = []
        
        # Aplicar filtros
        if busqueda and busqueda.strip():
            consulta += " AND (p.nombre LIKE ? OR p.apellidos LIKE ?)"
            patron = f"%{busqueda}%"
            parametros.extend([patron, patron])
        
        if filtro_rol and filtro_rol != "Todos":
            if filtro_rol == "Jugadores":
                consulta += " AND p.tipo_jugador = 'Jugador'"
            elif filtro_rol == "Árbitros":
                consulta += " AND p.tipo_jugador = 'Árbitro'"
            elif filtro_rol == "Ambos":
                consulta += " AND p.tipo_jugador = 'Ambos'"
        
        if filtro_equipo_id is not None:
            consulta += " AND p.equipo_id = ?"
            parametros.append(filtro_equipo_id)
        
        if filtro_curso and filtro_curso != "Todos":
            consulta += " AND p.curso = ?"
            parametros.append(filtro_curso)
        
        consulta += " ORDER BY p.apellidos, p.nombre"
        
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        
        if len(filas) == 0:
            print(f"⚠️ 0 participantes encontrados")
            print(f"Query: {consulta}")
            print(f"Parámetros: {parametros}")
        
        conn.close()
        
        participantes = []
        for fila in filas:
            participantes.append({
                "id": fila[0],
                "nombre": fila[1],
                "apellidos": fila[2],
                "fecha_nacimiento": fila[3],
                "curso": fila[4],
                "tipo_jugador": fila[5],
                "posicion": fila[6],
                "t_amarillas": fila[7],
                "t_rojas": fila[8],
                "goles": fila[9],
                "equipo_id": fila[10],
                "equipo_nombre": fila[11]
            })
        
        return participantes

    @staticmethod
    def asignar_a_equipo(participante_id: int, equipo_id: Optional[int]) -> None:
        """
        Asigna un participante a un equipo o lo desasigna.
        
        Args:
            participante_id: ID del participante
            equipo_id: ID del equipo o None para desasignar
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE participantes SET equipo_id = ? WHERE id = ?",
            (equipo_id, participante_id)
        )
        
        conn.commit()
        conn.close()

    @staticmethod
    def listar_arbitros() -> list[dict]:
        """
        Lista todos los participantes que pueden arbitrar.
        
        Returns:
            Lista de diccionarios con los datos de los árbitros
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id, p.nombre, p.apellidos, p.fecha_nacimiento, p.curso,
                p.tipo_jugador, p.posicion, p.t_amarillas, p.t_rojas, p.goles,
                p.equipo_id, e.nombre as equipo_nombre
            FROM participantes p
            LEFT JOIN equipos e ON p.equipo_id = e.id
            WHERE p.tipo_jugador IN ('Árbitro', 'Ambos')
            ORDER BY p.apellidos, p.nombre
        """)
        
        filas = cursor.fetchall()
        conn.close()
        
        arbitros = []
        for fila in filas:
            arbitros.append({
                "id": fila[0],
                "nombre": fila[1],
                "apellidos": fila[2],
                "fecha_nacimiento": fila[3],
                "curso": fila[4],
                "tipo_jugador": fila[5],
                "posicion": fila[6],
                "t_amarillas": fila[7],
                "t_rojas": fila[8],
                "goles": fila[9],
                "equipo_id": fila[10],
                "equipo_nombre": fila[11]
            })
        
        return arbitros

    @staticmethod
    def listar_jugadores_por_equipo(equipo_id: int) -> list[dict]:
        """
        Lista todos los jugadores de un equipo específico.
        
        Args:
            equipo_id: ID del equipo
            
        Returns:
            Lista de diccionarios con los datos de los jugadores
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id, p.nombre, p.apellidos, p.fecha_nacimiento, p.curso,
                p.tipo_jugador, p.posicion, p.t_amarillas, p.t_rojas, p.goles,
                p.equipo_id, e.nombre as equipo_nombre
            FROM participantes p
            LEFT JOIN equipos e ON p.equipo_id = e.id
            WHERE p.equipo_id = ?
            ORDER BY p.apellidos, p.nombre
        """, (equipo_id,))
        
        filas = cursor.fetchall()
        conn.close()
        
        jugadores = []
        for fila in filas:
            jugadores.append({
                "id": fila[0],
                "nombre": fila[1],
                "apellidos": fila[2],
                "fecha_nacimiento": fila[3],
                "curso": fila[4],
                "tipo_jugador": fila[5],
                "posicion": fila[6],
                "t_amarillas": fila[7],
                "t_rojas": fila[8],
                "goles": fila[9],
                "equipo_id": fila[10],
                "equipo_nombre": fila[11]
            })
        
        return jugadores

    @staticmethod
    def actualizar_acumulados(partido_id: int) -> None:
        """
        Actualiza las estadísticas acumuladas de los participantes basándose en un partido.
        Solo actualiza si el partido estaba en estado "Pendiente" antes de ser marcado como "Jugado",
        para evitar duplicados si se guarda dos veces el mismo partido.
        
        Args:
            partido_id: ID del partido cuyas estadísticas se sumarán a los acumulados
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Iniciar transacción
            cursor.execute("BEGIN TRANSACTION")
            
            # Verificar el estado actual del partido
            cursor.execute("""
                SELECT estado FROM partidos WHERE id = ?
            """, (partido_id,))
            
            resultado = cursor.fetchone()
            if not resultado:
                conn.rollback()
                conn.close()
                return
            
            estado_partido = resultado[0]
            
            # Solo actualizar acumulados si el partido está en estado "Jugado"
            # y no ha sido procesado antes (esto se controla llamando este método
            # solo cuando cambia de "Pendiente" a "Jugado")
            if estado_partido != "Jugado":
                # El partido no está jugado, no actualizar acumulados
                conn.rollback()
                conn.close()
                return
            
            # Obtener las estadísticas del partido
            cursor.execute("""
                SELECT participante_id, goles, amarillas, rojas
                FROM stats_partido
                WHERE partido_id = ?
            """, (partido_id,))
            
            stats = cursor.fetchall()
            
            # Actualizar cada participante sumando las estadísticas
            for stat in stats:
                participante_id, goles, amarillas, rojas = stat
                
                cursor.execute("""
                    UPDATE participantes
                    SET goles = goles + ?,
                        t_amarillas = t_amarillas + ?,
                        t_rojas = t_rojas + ?
                    WHERE id = ?
                """, (goles, amarillas, rojas, participante_id))
            
            # Confirmar transacción
            conn.commit()
            
        except Exception as e:
            # Revertir en caso de error
            conn.rollback()
            raise e
        finally:
            conn.close()
