"""
Servicio para la gestión de la lógica del torneo de eliminatorias.
"""
import random
from typing import Optional, Dict, Any
from app.models.match_model import MatchModel
from app.models.match_stats_model import MatchStatsModel
from app.services.event_bus import get_event_bus
from app.constants import (
    FASE_OCTAVOS, FASE_CUARTOS, FASE_SEMIFINAL, FASE_FINAL,
    FASES_CONFIG, FASES_ORDEN
)


class TournamentService:
    """Servicio para centralizar la lógica del torneo."""
    
    # Mapeo de rondas (usar minúsculas consistente con constants.py)
    RONDAS = [FASE_OCTAVOS, FASE_CUARTOS, FASE_SEMIFINAL, FASE_FINAL]
    
    # Número de partidos por ronda
    PARTIDOS_POR_RONDA = {
        FASE_OCTAVOS: 8,
        FASE_CUARTOS: 4,
        FASE_SEMIFINAL: 2,
        FASE_FINAL: 1
    }

    @staticmethod
    def generar_octavos_desde_emparejamientos(emparejamientos: list[dict]) -> None:
        """
        Genera los partidos de octavos desde una lista de emparejamientos.
        
        Args:
            emparejamientos: Lista de 8 diccionarios con 'local_id' y 'visitante_id'
        """
        if len(emparejamientos) != 8:
            raise ValueError("Se requieren exactamente 8 emparejamientos para octavos")
        
        # Crear los 8 partidos de octavos
        for i, emparejamiento in enumerate(emparejamientos, start=1):
            local_id = emparejamiento.get('local_id')
            visitante_id = emparejamiento.get('visitante_id')
            
            if not local_id or not visitante_id:
                raise ValueError(f"Emparejamiento {i} inválido: falta local_id o visitante_id")
            
            MatchModel.crear_partido(
                eliminatoria=FASE_OCTAVOS,
                slot=i,
                local_id=local_id,
                visitante_id=visitante_id
            )

    @staticmethod
    def randomizar_octavos(equipos: list[int]) -> list[dict]:
        """
        Genera emparejamientos aleatorios para octavos de final.
        
        Args:
            equipos: Lista de 16 IDs de equipos
            
        Returns:
            Lista de 8 emparejamientos [{local_id, visitante_id}, ...]
        """
        if len(equipos) != 16:
            raise ValueError("Se requieren exactamente 16 equipos para octavos")
        
        # Mezclar aleatoriamente los equipos
        equipos_mezclados = equipos.copy()
        random.shuffle(equipos_mezclados)
        
        # Crear emparejamientos
        emparejamientos = []
        for i in range(0, 16, 2):
            emparejamientos.append({
                'local_id': equipos_mezclados[i],
                'visitante_id': equipos_mezclados[i + 1]
            })
        
        return emparejamientos

    @staticmethod
    def resetear_cuadro() -> None:
        """Elimina todos los partidos del torneo."""
        MatchModel.borrar_todos_los_partidos()

    @staticmethod
    def avanzar_ronda(partido: dict) -> None:
        """
        Avanza el ganador de un partido a la siguiente ronda.
        
        Args:
            partido: Diccionario con los datos del partido jugado (debe tener ganador_equipo_id)
        """
        ganador_id = partido.get('ganador_equipo_id')
        
        if not ganador_id:
            raise ValueError("El partido debe tener un ganador para avanzar de ronda")
        
        eliminatoria_actual = partido.get('eliminatoria')
        slot_actual = partido.get('slot')
        
        if not eliminatoria_actual or slot_actual is None:
            raise ValueError("El partido debe tener eliminatoria y slot")
        
        # Normalizar la ronda a minúsculas para consistencia
        eliminatoria_actual = eliminatoria_actual.lower()
        
        print(f"[DEBUG avanzar_ronda] Partido {slot_actual} de {eliminatoria_actual}, ganador: {ganador_id}")
        
        # Determinar siguiente ronda
        siguiente_ronda = TournamentService._obtener_siguiente_ronda(eliminatoria_actual)
        
        if not siguiente_ronda:
            # Ya estamos en la final, no hay siguiente ronda
            print(f"[DEBUG avanzar_ronda] Ya es la final, no hay siguiente ronda")
            return
        
        print(f"[DEBUG avanzar_ronda] Siguiente ronda: {siguiente_ronda}")
        
        # Calcular slot del partido siguiente y posición (local/visitante)
        siguiente_slot, es_local = TournamentService._calcular_siguiente_partido(
            eliminatoria_actual, 
            slot_actual
        )
        
        print(f"[DEBUG avanzar_ronda] Siguiente slot: {siguiente_slot}, es_local: {es_local}")
        
        # Verificar si el partido de la siguiente ronda ya existe
        partidos_siguiente = MatchModel.listar_partidos(eliminatoria=siguiente_ronda)
        partido_siguiente = next(
            (p for p in partidos_siguiente if p['slot'] == siguiente_slot),
            None
        )
        
        if partido_siguiente:
            # El partido ya existe, actualizar el equipo correspondiente
            print(f"[DEBUG avanzar_ronda] Partido siguiente YA existe (ID: {partido_siguiente['id']}), actualizando equipo")
            TournamentService._actualizar_equipo_en_partido(
                partido_siguiente['id'],
                ganador_id,
                es_local
            )
            print(f"[DEBUG avanzar_ronda] Equipo {ganador_id} actualizado en partido {partido_siguiente['id']}")
        else:
            # Verificar si el partido hermano ya está jugado
            print(f"[DEBUG avanzar_ronda] Partido siguiente NO existe, buscando hermano...")
            partido_hermano = TournamentService._obtener_partido_hermano(
                eliminatoria_actual,
                slot_actual
            )
            
            if partido_hermano:
                print(f"[DEBUG avanzar_ronda] Hermano encontrado: slot {partido_hermano.get('slot')}, ganador: {partido_hermano.get('ganador_equipo_id')}")
            else:
                print(f"[DEBUG avanzar_ronda] No se encontró partido hermano")
            
            if partido_hermano and partido_hermano.get('ganador_equipo_id'):
                # El partido hermano ya tiene ganador, crear el partido siguiente
                ganador_hermano_id = partido_hermano['ganador_equipo_id']
                
                if es_local:
                    local_id = ganador_id
                    visitante_id = ganador_hermano_id
                else:
                    local_id = ganador_hermano_id
                    visitante_id = ganador_id
                
                print(f"[DEBUG avanzar_ronda] Creando partido en {siguiente_ronda}, slot {siguiente_slot}: {local_id} vs {visitante_id}")
                nuevo_partido_id = MatchModel.crear_partido(
                    eliminatoria=siguiente_ronda,
                    slot=siguiente_slot,
                    local_id=local_id,
                    visitante_id=visitante_id
                )
                print(f"[DEBUG avanzar_ronda] Partido creado con ID: {nuevo_partido_id}")
            else:
                print(f"[DEBUG avanzar_ronda] Hermano aún no jugado, esperando...")

    @staticmethod
    def _obtener_siguiente_ronda(ronda_actual: str) -> Optional[str]:
        """
        Obtiene la siguiente ronda en el torneo.
        
        Args:
            ronda_actual: Nombre de la ronda actual
            
        Returns:
            Nombre de la siguiente ronda o None si es la final
        """
        print(f"[DEBUG _obtener_siguiente_ronda] Ronda actual recibida: '{ronda_actual}'")
        print(f"[DEBUG _obtener_siguiente_ronda] RONDAS disponibles: {TournamentService.RONDAS}")
        
        # Normalizar a minúsculas para consistencia
        ronda_normalizada = ronda_actual.lower()
        print(f"[DEBUG _obtener_siguiente_ronda] Ronda normalizada: '{ronda_normalizada}'")
        
        try:
            index_actual = TournamentService.RONDAS.index(ronda_normalizada)
            print(f"[DEBUG _obtener_siguiente_ronda] Index encontrado: {index_actual}")
            if index_actual < len(TournamentService.RONDAS) - 1:
                siguiente = TournamentService.RONDAS[index_actual + 1]
                print(f"[DEBUG _obtener_siguiente_ronda] Siguiente ronda: '{siguiente}'")
                return siguiente
            else:
                print(f"[DEBUG _obtener_siguiente_ronda] Es la última ronda")
                return None
        except ValueError as e:
            print(f"[DEBUG _obtener_siguiente_ronda] ERROR: '{ronda_normalizada}' NO está en RONDAS")
            print(f"[DEBUG _obtener_siguiente_ronda] Exception: {e}")
            return None

    @staticmethod
    def _calcular_siguiente_partido(eliminatoria: str, slot: int) -> tuple[int, bool]:
        """
        Calcula el slot del partido siguiente y si el ganador va como local.
        
        Args:
            eliminatoria: Ronda actual
            slot: Slot actual (1-based)
            
        Returns:
            Tupla (siguiente_slot, es_local)
        """
        # Octavos: slots 1-8 -> Cuartos: slots 1-4
        # (1,2)->1; (3,4)->2; (5,6)->3; (7,8)->4
        # Cuartos: slots 1-4 -> Semifinal: slots 1-2
        # (1,2)->1; (3,4)->2
        # Semifinal: slots 1-2 -> Final: slot 1
        # (1,2)->1
        
        siguiente_slot = ((slot - 1) // 2) + 1
        es_local = (slot % 2 == 1)  # Slots impares van como local
        
        return siguiente_slot, es_local

    @staticmethod
    def _obtener_partido_hermano(eliminatoria: str, slot: int) -> Optional[dict]:
        """
        Obtiene el partido hermano (el otro partido que clasifica al mismo partido siguiente).
        
        Args:
            eliminatoria: Ronda actual
            slot: Slot actual
            
        Returns:
            Diccionario con los datos del partido hermano o None
        """
        # Determinar el slot hermano
        if slot % 2 == 1:
            # Slot impar, el hermano es el siguiente
            slot_hermano = slot + 1
        else:
            # Slot par, el hermano es el anterior
            slot_hermano = slot - 1
        
        # Obtener todos los partidos de la ronda
        partidos = MatchModel.listar_partidos(eliminatoria=eliminatoria)
        
        # Buscar el partido hermano
        for partido in partidos:
            if partido['slot'] == slot_hermano:
                return partido
        
        return None

    @staticmethod
    def _actualizar_equipo_en_partido(partido_id: int, equipo_id: int, es_local: bool) -> None:
        """
        Actualiza un equipo en un partido existente.
        
        Args:
            partido_id: ID del partido a actualizar
            equipo_id: ID del equipo ganador
            es_local: True si el equipo va como local, False si va como visitante
        """
        from app.models.db import get_connection
        
        print(f"[DEBUG _actualizar_equipo_en_partido] Partido ID: {partido_id}")
        print(f"[DEBUG _actualizar_equipo_en_partido] Equipo ID: {equipo_id}")
        print(f"[DEBUG _actualizar_equipo_en_partido] Es local: {es_local}")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        if es_local:
            print(f"[DEBUG _actualizar_equipo_en_partido] Actualizando equipo_local_id = {equipo_id}")
            cursor.execute(
                "UPDATE partidos SET equipo_local_id = ? WHERE id = ?",
                (equipo_id, partido_id)
            )
        else:
            print(f"[DEBUG _actualizar_equipo_en_partido] Actualizando equipo_visitante_id = {equipo_id}")
            cursor.execute(
                "UPDATE partidos SET equipo_visitante_id = ? WHERE id = ?",
                (equipo_id, partido_id)
            )
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"[DEBUG _actualizar_equipo_en_partido] ✓ Filas afectadas: {rows_affected}")

    @staticmethod
    def obtener_partidos_por_ronda(eliminatoria: str) -> list[dict]:
        """
        Obtiene todos los partidos de una ronda específica ordenados por slot.
        
        Args:
            eliminatoria: Nombre de la ronda
            
        Returns:
            Lista de partidos de la ronda
        """
        return MatchModel.listar_partidos(eliminatoria=eliminatoria)

    @staticmethod
    def verificar_ronda_completa(eliminatoria: str) -> bool:
        """
        Verifica si todos los partidos de una ronda están jugados.
        
        Args:
            eliminatoria: Nombre de la ronda
            
        Returns:
            True si todos los partidos están jugados, False en caso contrario
        """
        partidos = MatchModel.listar_partidos(eliminatoria=eliminatoria)
        
        # Verificar que existan todos los partidos esperados
        partidos_esperados = TournamentService.PARTIDOS_POR_RONDA.get(eliminatoria, 0)
        if len(partidos) < partidos_esperados:
            return False
        
        # Verificar que todos estén jugados
        return all(p['estado'] == 'Jugado' for p in partidos)

    @staticmethod
    def puede_avanzar_ronda(eliminatoria: str) -> bool:
        """
        Verifica si se puede avanzar a la siguiente ronda.
        
        Args:
            eliminatoria: Nombre de la ronda actual
            
        Returns:
            True si todos los partidos de la ronda están jugados
        """
        return TournamentService.verificar_ronda_completa(eliminatoria)

    @staticmethod
    def create_or_update_match(match_data: Dict[str, Any]) -> int:
        """
        Crea o actualiza un partido y emite eventos correspondientes.
        
        Args:
            match_data: Diccionario con datos del partido
                Required: equipo_local_id, equipo_visitante_id, eliminatoria
                Optional: id (para update), fecha_hora, arbitro_id, etc.
        
        Returns:
            ID del partido creado/actualizado
        """
        event_bus = get_event_bus()
        match_id = match_data.get('id')
        
        if match_id:
            # Actualizar partido existente
            MatchModel.actualizar_partido(match_id, match_data)
            event_bus.emit_match_updated(match_id)
            return match_id
        else:
            # Crear nuevo partido
            eliminatoria = match_data['eliminatoria']
            slot = match_data.get('slot', 1)
            local_id = match_data['equipo_local_id']
            visitante_id = match_data['equipo_visitante_id']
            
            match_id = MatchModel.crear_partido(eliminatoria, slot, local_id, visitante_id)
            
            # Actualizar campos adicionales si existen
            if 'fecha_hora' in match_data or 'arbitro_id' in match_data:
                MatchModel.actualizar_partido(match_id, match_data)
            
            event_bus.emit_match_created(match_id)
            return match_id

    @staticmethod
    def save_match_result(match_id: int, result_data: Dict[str, Any]) -> bool:
        """
        Guarda el resultado de un partido y propaga el ganador automáticamente.
        
        Args:
            match_id: ID del partido
            result_data: Diccionario con:
                - goles_local: int
                - goles_visitante: int
                - penaltis_local: int (opcional)
                - penaltis_visitante: int (opcional)
                - stats: list[dict] con estadísticas de jugadores (opcional)
        
        Returns:
            True si se guardó correctamente
        """
        event_bus = get_event_bus()
        
        # Obtener datos del partido
        partidos = MatchModel.listar_partidos()
        partido = next((p for p in partidos if p['id'] == match_id), None)
        
        if not partido:
            raise ValueError(f"Partido {match_id} no encontrado")
        
        goles_local = result_data.get('goles_local', 0)
        goles_visitante = result_data.get('goles_visitante', 0)
        penaltis_local = result_data.get('penaltis_local')
        penaltis_visitante = result_data.get('penaltis_visitante')
        
        # Determinar ganador
        ganador_id = None
        if goles_local > goles_visitante:
            ganador_id = partido.get('equipo_local_id') or partido.get('local_id')
        elif goles_visitante > goles_local:
            ganador_id = partido.get('equipo_visitante_id') or partido.get('visitante_id')
        elif penaltis_local is not None and penaltis_visitante is not None:
            # Empate, decidir por penaltis
            if penaltis_local > penaltis_visitante:
                ganador_id = partido.get('equipo_local_id') or partido.get('local_id')
            elif penaltis_visitante > penaltis_local:
                ganador_id = partido.get('equipo_visitante_id') or partido.get('visitante_id')
        
        # Guardar resultado usando el método correcto del modelo
        MatchModel.guardar_resultado(
            match_id,
            goles_local,
            goles_visitante,
            penaltis_local,
            penaltis_visitante
        )
        
        # Guardar estadísticas de jugadores si se proporcionan
        stats = result_data.get('stats', [])
        if stats:
            TournamentService._save_player_stats(match_id, stats)
        
        # Emitir evento de resultado guardado
        event_bus.emit_result_saved(match_id)
        
        # Propagar ganador automáticamente
        if ganador_id:
            TournamentService.propagate_winner(match_id)
        
        return True

    @staticmethod
    def propagate_winner(match_id: int) -> Optional[int]:
        """
        Propaga el ganador de un partido a la siguiente ronda.
        
        Args:
            match_id: ID del partido cuyo ganador se avanzará
        
        Returns:
            ID del partido siguiente creado/actualizado, o None si no hay siguiente
        """
        event_bus = get_event_bus()
        
        # Obtener datos del partido
        partidos = MatchModel.listar_partidos()
        partido = next((p for p in partidos if p['id'] == match_id), None)
        
        if not partido:
            return None
        
        ganador_id = partido.get('ganador_equipo_id')
        if not ganador_id:
            return None
        
        eliminatoria_actual = partido.get('eliminatoria')
        slot_actual = partido.get('slot')
        
        # Avanzar ronda usando lógica existente
        try:
            TournamentService.avanzar_ronda(partido)
            event_bus.emit_phase_advanced(eliminatoria_actual, match_id)
            
            # Obtener el partido de la siguiente ronda
            siguiente_ronda = TournamentService._obtener_siguiente_ronda(eliminatoria_actual)
            if siguiente_ronda:
                siguiente_slot, _ = TournamentService._calcular_siguiente_partido(
                    eliminatoria_actual, slot_actual
                )
                partidos_siguiente = MatchModel.listar_partidos(eliminatoria=siguiente_ronda)
                partido_siguiente = next(
                    (p for p in partidos_siguiente if p['slot'] == siguiente_slot),
                    None
                )
                return partido_siguiente['id'] if partido_siguiente else None
        except Exception as e:
            print(f"[ERROR] Error al propagar ganador: {e}")
            return None

    @staticmethod
    def _save_player_stats(match_id: int, stats: list[dict]) -> None:
        """
        Guarda las estadísticas individuales de jugadores en un partido.
        
        Args:
            match_id: ID del partido
            stats: Lista de diccionarios con estadísticas por jugador
        """
        # Limpiar estadísticas previas del partido
        MatchStatsModel.limpiar_stats_partido(match_id)
        
        # Guardar nuevas estadísticas
        for stat in stats:
            participant_name = stat.get('jugador', '')
            if not participant_name:
                continue
            
            # Buscar ID del participante por nombre
            from app.models.participant_model import ParticipantModel
            participantes = ParticipantModel.listar_participantes()
            participante = next(
                (p for p in participantes if p['nombre'] == participant_name),
                None
            )
            
            if not participante:
                continue
            
            participant_id = participante['id']
            goles = stat.get('goles', 0)
            amarillas = stat.get('amarillas', 0)
            rojas = stat.get('rojas', 0)
            
            # Guardar goles
            for _ in range(goles):
                MatchStatsModel.registrar_gol(match_id, participant_id)
            
            # Guardar tarjetas amarillas
            for _ in range(amarillas):
                MatchStatsModel.registrar_tarjeta_amarilla(match_id, participant_id)
            
            # Guardar tarjetas rojas
            for _ in range(rojas):
                MatchStatsModel.registrar_tarjeta_roja(match_id, participant_id)

    @staticmethod
    def get_bracket_state() -> Dict[str, Any]:
        """
        Obtiene el estado completo del cuadro de eliminatorias.
        
        Returns:
            Diccionario con el estado de todas las rondas:
            {
                'Octavos': [partido1, partido2, ...],
                'Cuartos': [...],
                'Semifinal': [...],
                'Final': [...]
            }
        """
        bracket = {}
        for ronda in TournamentService.RONDAS:
            partidos = MatchModel.listar_partidos(eliminatoria=ronda)
            # Ordenar por slot
            partidos_ordenados = sorted(partidos, key=lambda x: x.get('slot', 0))
            bracket[ronda] = partidos_ordenados
        
        return bracket

    @staticmethod
    def octavos_already_exist() -> bool:
        """
        Verifica si ya existen partidos de octavos en la base de datos.
        
        Returns:
            True si existen partidos de octavos, False en caso contrario
        """
        partidos_octavos = MatchModel.listar_partidos(eliminatoria=FASE_OCTAVOS)
        return len(partidos_octavos) > 0

    @staticmethod
    def randomize_and_create_octavos(equipos_ids: list[int]) -> None:
        """
        Genera emparejamientos aleatorios de octavos Y los persiste en BD con fechas automáticas.
        
        Args:
            equipos_ids: Lista de 16 IDs de equipos
            
        Raises:
            ValueError: Si no hay exactamente 16 equipos o si ya existen octavos
        """
        from datetime import datetime, timedelta
        
        print("\n" + "="*60)
        print("[TOURNAMENT SERVICE] randomize_and_create_octavos INICIADO")
        print("="*60)
        
        # Validación
        print(f"[DEBUG] Equipos recibidos: {len(equipos_ids)}")
        if len(equipos_ids) != 16:
            raise ValueError("Se requieren exactamente 16 equipos para octavos")
        
        # Eliminar octavos existentes si los hay (para evitar constraint UNIQUE)
        print("[DEBUG] Verificando si ya existen octavos...")
        if TournamentService.octavos_already_exist():
            print("[DEBUG] ⚠️ Ya existen octavos en BD, eliminándolos...")
            partidos_octavos = MatchModel.listar_partidos(eliminatoria=FASE_OCTAVOS)
            for partido in partidos_octavos:
                MatchModel.eliminar_partido(partido['id'])
                print(f"[DEBUG]   ✅ Eliminado partido ID {partido['id']}")
            print("[DEBUG] ✅ Octavos previos eliminados")
        else:
            print("[DEBUG] ✅ No existen octavos previos")
        
        # Generar emparejamientos aleatorios
        print("[DEBUG] Generando emparejamientos aleatorios...")
        emparejamientos = TournamentService.randomizar_octavos(equipos_ids)
        print(f"[DEBUG] ✅ {len(emparejamientos)} emparejamientos generados")
        
        # Fecha base: hoy + 1 día a las 16:00
        fecha_base = datetime.now() + timedelta(days=1)
        fecha_base = fecha_base.replace(hour=16, minute=0, second=0, microsecond=0)
        print(f"[DEBUG] Fecha base: {fecha_base}")
        
        # Horarios disponibles por día (2 partidos por día)
        horarios = ["16:00", "18:00"]
        
        # Crear los 8 partidos de octavos con fechas automáticas
        partidos_creados = []
        print("\n[DEBUG] Creando partidos en BD...")
        for i, emparejamiento in enumerate(emparejamientos):
            # Calcular día y horario
            dia_offset = i // 2  # 2 partidos por día
            horario_index = i % 2  # Alternar entre 16:00 y 18:00
            
            fecha_partido = fecha_base + timedelta(days=dia_offset)
            hora_partido = horarios[horario_index]
            
            # Formato: "YYYY-MM-DD HH:MM:SS"
            fecha_hora_str = fecha_partido.strftime(f"%Y-%m-%d {hora_partido}:00")
            
            print(f"\n  Partido {i+1}/8:")
            print(f"    Local ID: {emparejamiento['local_id']}")
            print(f"    Visitante ID: {emparejamiento['visitante_id']}")
            print(f"    Fecha/Hora: {fecha_hora_str}")
            print(f"    Slot: {i+1}")
            
            # Crear partido en BD
            match_id = MatchModel.crear_partido(
                eliminatoria=FASE_OCTAVOS,
                slot=i + 1,
                local_id=emparejamiento['local_id'],
                visitante_id=emparejamiento['visitante_id'],
                fecha_hora=fecha_hora_str,
                estado="Programado"
            )
            partidos_creados.append(match_id)
            print(f"    ✅ Partido creado con ID: {match_id}")
        
        print(f"\n[DEBUG] ✅ Total de partidos creados: {len(partidos_creados)}")
        print(f"[DEBUG] IDs creados: {partidos_creados}")
        
        # Verificar que se crearon en BD
        print("\n[DEBUG] Verificando en BD...")
        partidos_en_bd = MatchModel.listar_partidos(eliminatoria=FASE_OCTAVOS)
        print(f"[DEBUG] Partidos 'Octavos' encontrados en BD: {len(partidos_en_bd)}")
        
        if len(partidos_en_bd) != 8:
            print(f"[ERROR] ❌ Se esperaban 8 partidos pero hay {len(partidos_en_bd)}")
        else:
            print("[DEBUG] ✅ Verificación exitosa: 8 partidos en BD")
        
        # Emitir eventos para refrescar UI
        print("\n[DEBUG] Emitiendo eventos...")
        event_bus = get_event_bus()
        event_bus.bracket_updated.emit()
        print("[DEBUG] ✅ Evento bracket_updated emitido")
        event_bus.match_changed.emit(0)  # 0 = cambio general, no específico
        print("[DEBUG] ✅ Evento match_changed emitido")
        
        print("\n" + "="*60)
        print("[TOURNAMENT SERVICE] randomize_and_create_octavos COMPLETADO")
        print("="*60 + "\n")


