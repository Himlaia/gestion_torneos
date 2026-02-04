"""Servicio para gestionar la lógica de partidos con validaciones robustas."""
from dataclasses import dataclass
from typing import Optional
from app.models.match_model import MatchModel
from app.models.callup_model import CallupModel
from app.models.match_stats_model import MatchStatsModel
from app.models.goal_model import GoalModel
from app.services.event_bus import get_event_bus


@dataclass
class MatchData:
    """Estructura de datos validada para un partido."""
    id: Optional[int] = None
    eliminatoria: Optional[str] = None
    slot: Optional[int] = None
    fecha_hora: Optional[str] = None
    equipo_local_id: Optional[int] = None
    equipo_visitante_id: Optional[int] = None
    arbitro_id: Optional[int] = None
    goles_local: int = 0
    goles_visitante: int = 0
    penaltis_local: Optional[int] = None
    penaltis_visitante: Optional[int] = None
    ganador_equipo_id: Optional[int] = None
    estado: str = "Pendiente"
    
    def esta_programado(self) -> bool:
        """Verifica si el partido tiene los datos mínimos para ser programado."""
        return (
            self.equipo_local_id is not None and
            self.equipo_visitante_id is not None and
            self.fecha_hora is not None
        )
    
    def puede_editar_resultado(self) -> bool:
        """Verifica si se puede editar el resultado."""
        return self.equipo_local_id is not None and self.equipo_visitante_id is not None
    
    def puede_guardar_resultado(self) -> bool:
        """Verifica si se puede guardar el resultado (requiere árbitro)."""
        return self.puede_editar_resultado() and self.arbitro_id is not None
    
    @staticmethod
    def from_dict(data: dict) -> 'MatchData':
        """Crea MatchData desde un diccionario con validación."""
        return MatchData(
            id=data.get('id'),
            eliminatoria=data.get('eliminatoria'),
            slot=data.get('slot'),
            fecha_hora=data.get('fecha_hora'),
            equipo_local_id=data.get('local_id') or data.get('equipo_local_id'),
            equipo_visitante_id=data.get('visitante_id') or data.get('equipo_visitante_id'),
            arbitro_id=data.get('arbitro_id'),
            goles_local=data.get('goles_local', 0),
            goles_visitante=data.get('goles_visitante', 0),
            penaltis_local=data.get('penaltis_local'),
            penaltis_visitante=data.get('penaltis_visitante'),
            ganador_equipo_id=data.get('ganador_equipo_id'),
            estado=data.get('estado', 'Pendiente')
        )


class MatchService:
    """Servicio centralizado para gestión de partidos con validaciones."""
    
    @staticmethod
    def load_match(partido_id: int) -> Optional[MatchData]:
        """
        Carga un partido con validación.
        
        Args:
            partido_id: ID del partido
            
        Returns:
            MatchData validado o None si no existe
        """
        data = MatchModel.obtener_partido_por_id(partido_id)
        if not data:
            return None
        return MatchData.from_dict(data)
    
    @staticmethod
    def validate_for_result_save(match: MatchData) -> tuple[bool, str]:
        """
        Valida si un partido está listo para guardar resultado.
        
        Args:
            match: Datos del partido
            
        Returns:
            (es_valido, mensaje_error)
        """
        if not match.equipo_local_id or not match.equipo_visitante_id:
            return False, "El partido no tiene equipos asignados.\n\nVaya a 'Datos' y asigne ambos equipos."
        
        if not match.arbitro_id:
            return False, "Debe asignar un árbitro antes de guardar el resultado."
        
        # Validar convocatorias
        if match.id:
            local_count = CallupModel.contar_convocados_equipo(match.id, match.equipo_local_id)
            visitante_count = CallupModel.contar_convocados_equipo(match.id, match.equipo_visitante_id)
            
            if local_count < 1:
                return False, "El equipo local debe tener al menos 1 jugador convocado."
            
            if visitante_count < 1:
                return False, "El equipo visitante debe tener al menos 1 jugador convocado."
        
        return True, ""
    
    @staticmethod
    def save_match_data(
        partido_id: int,
        fase: str,
        fecha_hora: str,
        equipo_local_id: Optional[int],
        equipo_visitante_id: Optional[int],
        arbitro_id: Optional[int]
    ) -> None:
        """
        Guarda los datos básicos del partido SIN eliminar emparejamientos.
        
        Args:
            partido_id: ID del partido
            fase: Fase del torneo
            fecha_hora: Fecha y hora del partido
            equipo_local_id: ID del equipo local
            equipo_visitante_id: ID del equipo visitante
            arbitro_id: ID del árbitro
        """
        # Actualizar partido manteniendo estado y emparejamientos
        MatchModel.actualizar_partido(
            partido_id, fase, fecha_hora,
            equipo_local_id, equipo_visitante_id,
            "Programado" if fecha_hora else "Pendiente",
            arbitro_id
        )
        
        # Emitir evento
        event_bus = get_event_bus()
        event_bus.emit_match_updated(partido_id)
    
    @staticmethod
    def save_convocatoria(partido_id: int, local_ids: list[int], visitante_ids: list[int]) -> None:
        """
        Guarda la convocatoria completa de un partido.
        
        Args:
            partido_id: ID del partido
            local_ids: Lista de IDs de jugadores convocados del equipo local
            visitante_ids: Lista de IDs de jugadores convocados del equipo visitante
        """
        # Cargar partido para obtener equipo_ids
        match = MatchService.load_match(partido_id)
        if not match or not match.equipo_local_id or not match.equipo_visitante_id:
            raise ValueError("No se pueden guardar convocados sin equipos asignados")
        
        # Limpiar convocatoria actual
        CallupModel.limpiar_convocados_partido(partido_id)
        
        # Añadir convocados locales
        for participante_id in local_ids:
            CallupModel.convocar_jugador(partido_id, participante_id, match.equipo_local_id)
            MatchStatsModel.inicializar_stats(partido_id, [participante_id])
        
        # Añadir convocados visitantes
        for participante_id in visitante_ids:
            CallupModel.convocar_jugador(partido_id, participante_id, match.equipo_visitante_id)
            MatchStatsModel.inicializar_stats(partido_id, [participante_id])
    
    @staticmethod
    def save_result_with_goals(
        partido_id: int,
        goles_local: int,
        goles_visitante: int,
        penaltis_local: Optional[int],
        penaltis_visitante: Optional[int],
        goles_detalle: list[dict],
        stats: list[dict]
    ) -> dict:
        """
        Guarda el resultado con goles detallados y estadísticas.
        
        Args:
            partido_id: ID del partido
            goles_local: Goles del equipo local
            goles_visitante: Goles del equipo visitante
            penaltis_local: Penaltis del equipo local (si aplica)
            penaltis_visitante: Penaltis del equipo visitante (si aplica)
            goles_detalle: Lista de dicts con {participante_id, equipo_id, minuto}
            stats: Lista de dicts con estadísticas de jugadores
            
        Returns:
            Diccionario con resultado guardado
        """
        # Validar partido
        match = MatchService.load_match(partido_id)
        if not match:
            raise ValueError(f"Partido {partido_id} no encontrado")
        
        es_valido, mensaje = MatchService.validate_for_result_save(match)
        if not es_valido:
            raise ValueError(mensaje)
        
        print(f"\n{'='*60}")
        print(f"[MATCH_SERVICE] Guardando resultado del partido {partido_id}")
        print(f"[MATCH_SERVICE] Goles: {goles_local}-{goles_visitante}")
        print(f"[MATCH_SERVICE] Goles detallados: {len(goles_detalle)}")
        print(f"[MATCH_SERVICE] Stats recibidas: {len(stats)}")
        print(f"{'='*60}\n")
        
        # Guardar resultado en tabla partidos
        resultado = MatchModel.guardar_resultado(
            partido_id, goles_local, goles_visitante,
            penaltis_local, penaltis_visitante
        )
        
        print(f"[MATCH_SERVICE] Resultado guardado. Ganador: {resultado.get('ganador_equipo_id')}")
        
        # Limpiar goles anteriores
        GoalModel.limpiar_goles_partido(partido_id)
        print(f"[MATCH_SERVICE] Goles anteriores limpiados")
        
        # Registrar goles con autor
        goles_por_jugador = {}
        for gol in goles_detalle:
            GoalModel.registrar_gol(
                partido_id,
                gol['participante_id'],
                gol['equipo_id'],
                gol.get('minuto')
            )
            # Contar goles por jugador
            participante_id = gol.get('participante_id')
            if participante_id:
                goles_por_jugador[participante_id] = goles_por_jugador.get(participante_id, 0) + 1
        
        print(f"[MATCH_SERVICE] {len(goles_detalle)} goles registrados en BD")
        print(f"[MATCH_SERVICE] Distribución de goles: {goles_por_jugador}")
        
        # IMPORTANTE: Sobrescribir TODOS los goles en stats con los calculados desde goles_detalle
        # Esto garantiza que las estadísticas reflejen EXACTAMENTE los goles detallados
        for stat in stats:
            participante_id = stat.get('participante_id')
            if participante_id:
                # Sobrescribir con goles calculados (0 si no tiene goles)
                stat['goles'] = goles_por_jugador.get(participante_id, 0)
        
        print(f"[MATCH_SERVICE] Estadísticas actualizadas con goles calculados")
        
        # Guardar estadísticas de jugadores
        MatchStatsModel.guardar_stats(partido_id, stats)
        print(f"[MATCH_SERVICE] Estadísticas guardadas en BD")
        
        # Emitir eventos
        event_bus = get_event_bus()
        event_bus.emit_result_saved(partido_id)
        print(f"[MATCH_SERVICE] Evento result_saved emitido")
        
        # Propagar ganador si existe
        ganador_id = resultado.get('ganador_equipo_id')
        if ganador_id:
            print(f"[MATCH_SERVICE] Propagando ganador {ganador_id} a siguiente ronda...")
            from app.services.tournament_service import TournamentService
            try:
                partido_siguiente_id = TournamentService.propagate_winner(partido_id)
                if partido_siguiente_id:
                    print(f"[MATCH_SERVICE] Ganador propagado a partido {partido_siguiente_id}")
                else:
                    print(f"[MATCH_SERVICE] Propagación completada (final o esperando hermano)")
            except Exception as e:
                print(f"[MATCH_SERVICE ERROR] Error al propagar ganador: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[MATCH_SERVICE] No hay ganador definido, no se propaga")
        
        print(f"\n[MATCH_SERVICE] ✓ Resultado guardado exitosamente\n")
        return resultado
    
    @staticmethod
    def randomize_goalscorers(
        partido_id: int,
        goles_local: int,
        goles_visitante: int
    ) -> list[dict]:
        """
        Distribuye goles aleatoriamente entre los convocados.
        
        Args:
            partido_id: ID del partido
            goles_local: Número de goles del equipo local
            goles_visitante: Número de goles del equipo visitante
            
        Returns:
            Lista de dicts con {participante_id, equipo_id, minuto}
            Lista vacía si no hay convocados suficientes
        """
        import random
        
        match = MatchService.load_match(partido_id)
        if not match or not match.equipo_local_id or not match.equipo_visitante_id:
            return []
        
        # Obtener convocados de cada equipo
        convocados_local = CallupModel.obtener_convocados_equipo(partido_id, match.equipo_local_id)
        convocados_visitante = CallupModel.obtener_convocados_equipo(partido_id, match.equipo_visitante_id)
        
        # Si no hay convocados, retornar vacío
        if (goles_local > 0 and not convocados_local) or (goles_visitante > 0 and not convocados_visitante):
            return []
        
        goles_detalle = []
        
        # Distribuir goles locales
        if goles_local > 0 and convocados_local:
            for i in range(goles_local):
                jugador = random.choice(convocados_local)
                minuto = random.randint(1, 90)
                goles_detalle.append({
                    'participante_id': jugador['participante_id'],
                    'equipo_id': match.equipo_local_id,
                    'minuto': minuto
                })
        
        # Distribuir goles visitantes
        if goles_visitante > 0 and convocados_visitante:
            for i in range(goles_visitante):
                jugador = random.choice(convocados_visitante)
                minuto = random.randint(1, 90)
                goles_detalle.append({
                    'participante_id': jugador['participante_id'],
                    'equipo_id': match.equipo_visitante_id,
                    'minuto': minuto
                })
        
        # Ordenar por minuto
        goles_detalle.sort(key=lambda x: x.get('minuto') or 999)
        
        return goles_detalle
