"""
Event Bus central para sincronización de eventos entre módulos.

Implementa un patrón Observer usando señales de Qt para
mantener sincronizadas todas las vistas de la aplicación.
"""
from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    """
    Bus de eventos centralizado para la aplicación.
    
    Permite que diferentes componentes se suscriban a eventos
    sin acoplamiento directo entre emisor y receptor.
    """
    
    _instance = None
    
    # Señales de equipos
    team_created = Signal(int)  # team_id
    team_updated = Signal(int)  # team_id
    team_deleted = Signal(int)  # team_id
    team_changed = Signal(int)  # team_id (create/update/delete genérico)
    
    # Señales de participantes
    participant_created = Signal(int)  # participant_id
    participant_updated = Signal(int)  # participant_id
    participant_deleted = Signal(int)  # participant_id
    participant_changed = Signal(int)  # participant_id (genérico)
    
    # Señales de partidos
    match_created = Signal(int)  # match_id
    match_updated = Signal(int)  # match_id
    match_deleted = Signal(int)  # match_id
    match_changed = Signal(int)  # match_id (genérico)
    
    # Señales de resultados
    result_saved = Signal(int)  # match_id
    result_changed = Signal(int)  # match_id
    
    # Señales de bracket/eliminatorias
    bracket_updated = Signal()  # Cuadro completo actualizado
    phase_advanced = Signal(str, int)  # (phase, match_id) - ganador avanzó
    
    # Señales de convocatorias
    callup_changed = Signal(int)  # match_id
    
    # Señales de clasificaciones/estadísticas
    stats_updated = Signal()  # Estadísticas globales actualizadas
    
    def __init__(self):
        """Inicializa el event bus."""
        super().__init__()
    
    @classmethod
    def get_instance(cls) -> 'EventBus':
        """
        Obtiene la instancia singleton del EventBus.
        
        Returns:
            Instancia única del EventBus
        """
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance
    
    # Métodos de conveniencia para emitir eventos
    
    def emit_team_created(self, team_id: int):
        """Emite evento de equipo creado."""
        self.team_created.emit(team_id)
        self.team_changed.emit(team_id)
    
    def emit_team_updated(self, team_id: int):
        """Emite evento de equipo actualizado."""
        self.team_updated.emit(team_id)
        self.team_changed.emit(team_id)
    
    def emit_team_deleted(self, team_id: int):
        """Emite evento de equipo eliminado."""
        self.team_deleted.emit(team_id)
        self.team_changed.emit(team_id)
    
    def emit_participant_created(self, participant_id: int):
        """Emite evento de participante creado."""
        self.participant_created.emit(participant_id)
        self.participant_changed.emit(participant_id)
    
    def emit_participant_updated(self, participant_id: int):
        """Emite evento de participante actualizado."""
        self.participant_updated.emit(participant_id)
        self.participant_changed.emit(participant_id)
    
    def emit_participant_deleted(self, participant_id: int):
        """Emite evento de participante eliminado."""
        self.participant_deleted.emit(participant_id)
        self.participant_changed.emit(participant_id)
    
    def emit_match_created(self, match_id: int):
        """Emite evento de partido creado."""
        self.match_created.emit(match_id)
        self.match_changed.emit(match_id)
        self.bracket_updated.emit()
    
    def emit_match_updated(self, match_id: int):
        """Emite evento de partido actualizado."""
        self.match_updated.emit(match_id)
        self.match_changed.emit(match_id)
        self.bracket_updated.emit()
    
    def emit_match_deleted(self, match_id: int):
        """Emite evento de partido eliminado."""
        self.match_deleted.emit(match_id)
        self.match_changed.emit(match_id)
        self.bracket_updated.emit()
    
    def emit_result_saved(self, match_id: int):
        """Emite evento de resultado guardado."""
        self.result_saved.emit(match_id)
        self.result_changed.emit(match_id)
        self.match_changed.emit(match_id)
        self.bracket_updated.emit()
        self.stats_updated.emit()
    
    def emit_phase_advanced(self, phase: str, match_id: int):
        """Emite evento de avance de fase."""
        self.phase_advanced.emit(phase, match_id)
        self.bracket_updated.emit()
    
    def emit_bracket_updated(self):
        """Emite evento de actualización del cuadro de eliminatorias."""
        self.bracket_updated.emit()


# Instancia singleton del event bus
def get_event_bus() -> EventBus:
    """
    Obtiene la instancia singleton del event bus.
    
    Returns:
        Instancia única del EventBus (usa get_instance() para garantizar singleton)
    """
    return EventBus.get_instance()
