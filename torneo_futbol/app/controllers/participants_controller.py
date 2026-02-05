"""
Controlador para la gestión de participantes (jugadores y árbitros).
"""
from PySide6.QtWidgets import QMessageBox
from app.models.participant_model import ParticipantModel
from app.models.team_model import TeamModel
from app.services.event_bus import EventBus


class ControladorGestionParticipantes:
    """Controlador para conectar la vista de participantes con los modelos."""
    
    def __init__(self, vista):
        """
        Inicializa el controlador y conecta las señales de la vista.
        
        Args:
            vista: Instancia de PageGestionParticipantes
        """
        self.vista = vista
        self.participante_actual_id = None
        self.modo_actual = "ver"  # "ver" | "crear" | "editar"
        
        # Obtener instancia del Event Bus
        self.event_bus = EventBus.get_instance()
        
        # Conectar señales
        self._conectar_senales()
        self._conectar_event_bus()
        
        # Cargar datos iniciales
        self.cargar_filtros()
        self.cargar_tabla()
    
    def _conectar_senales(self):
        """Conecta todas las señales de la vista con los métodos del controlador."""
        self.vista.nuevo_participante_signal.connect(self._on_nuevo)
        self.vista.editar_participante_signal.connect(self._on_editar)
        self.vista.eliminar_participante_signal.connect(self._on_eliminar)
        self.vista.guardar_participante_signal.connect(self._on_guardar)
        self.vista.cancelar_edicion_signal.connect(self._on_cancelar)
        self.vista.buscar_participante_changed_signal.connect(self._on_buscar)
        self.vista.filtros_changed_signal.connect(self._on_filtros_changed)
        self.vista.participante_seleccionado_signal.connect(self._on_seleccionado)
        self.vista.guardar_equipo_signal.connect(self._on_guardar_equipo)
        self.vista.quitar_equipo_signal.connect(self._on_quitar_equipo)
    
    def _conectar_event_bus(self):
        """Conecta el Event Bus para escuchar cambios externos."""
        # Escuchar cambios en equipos para actualizar combos
        self.event_bus.team_created.connect(self._on_team_changed_external)
        self.event_bus.team_updated.connect(self._on_team_changed_external)
        self.event_bus.team_deleted.connect(self._on_team_changed_external)
    
    def cargar_filtros(self):
        """Carga los datos en los combos de filtros (equipos y cursos)."""
        # Cargar equipos
        equipos = TeamModel.listar_equipos()
        lista_equipos = ["Todos"] + [eq["nombre"] for eq in equipos]
        self.vista.cargar_combo_equipos_filtro(lista_equipos)
        
        # Cargar equipos para asignación en el formulario
        equipos_asignacion = ["Sin equipo"] + [eq["nombre"] for eq in equipos]
        self.vista.cargar_combo_equipos_asignacion(equipos_asignacion)
        self.equipos_dict = {eq["nombre"]: eq["id"] for eq in equipos}
        
        # Cargar equipos en el combo del tab Asignaciones
        self.vista.load_equipos_into_combo(self.equipos_dict)
        
        # Cargar cursos (lista predefinida)
        cursos = ["Todos", "1º ESO", "2º ESO", "3º ESO", "4º ESO", 
                  "1º Bachillerato", "2º Bachillerato"]
        self.vista.cargar_combo_cursos(cursos)
    
    def cargar_tabla(self):
        """Carga los participantes en la tabla según los filtros actuales."""
        # Obtener filtros actuales de la vista
        filtros = self.vista.obtener_filtros_actuales()
        
        # Preparar parámetros para el modelo
        busqueda = filtros.get("busqueda")
        if busqueda == "":
            busqueda = None
        
        filtro_rol = filtros.get("rol")
        if filtro_rol == "Todos":
            filtro_rol = None
        
        filtro_curso = filtros.get("curso")
        if filtro_curso == "Todos":
            filtro_curso = None
        
        # Obtener equipo_id si el filtro no es "Todos"
        filtro_equipo_id = None
        nombre_equipo = filtros.get("equipo")
        if nombre_equipo and nombre_equipo != "Todos":
            filtro_equipo_id = self.equipos_dict.get(nombre_equipo)
        
        print(f"🔍 Cargando participantes con filtros: busqueda={busqueda}, rol={filtro_rol}, equipo_id={filtro_equipo_id}, curso={filtro_curso}")
        
        # Obtener participantes del modelo
        participantes = ParticipantModel.listar_participantes(
            busqueda=busqueda,
            filtro_rol=filtro_rol,
            filtro_equipo_id=filtro_equipo_id,
            filtro_curso=filtro_curso
        )
        
        print(f"✅ {len(participantes)} participantes encontrados")
        
        # Actualizar la tabla en la vista
        self.vista.actualizar_tabla(participantes)
    
    def _on_buscar(self, texto: str):
        """
        Maneja el cambio en el campo de búsqueda.
        
        Args:
            texto: Texto de búsqueda
        """
        self.cargar_tabla()
    
    def _on_filtros_changed(self, filtros: dict):
        """
        Maneja el cambio en los filtros.
        
        Args:
            filtros: Diccionario con los valores de los filtros
        """
        self.cargar_tabla()
    
    def _on_seleccionado(self, datos: dict):
        """
        Maneja la selección de un participante en la tabla.
        
        Args:
            datos: Diccionario con los datos del participante seleccionado
        """
        self.participante_actual_id = datos.get("id")
        
        # Obtener datos completos del participante
        participante = ParticipantModel.obtener_participante_por_id(self.participante_actual_id)
        
        if participante:
            # Convertir tipo_jugador a checkboxes
            es_jugador = participante["tipo_jugador"] in ("Jugador", "Ambos")
            es_arbitro = participante["tipo_jugador"] in ("Árbitro", "Ambos")
            
            # Preparar datos para el formulario
            datos_formulario = {
                "nombre": participante["nombre"],
                "apellidos": participante["apellidos"] or "",
                "fecha_nacimiento": participante["fecha_nacimiento"],
                "curso": participante["curso"],
                "es_jugador": es_jugador,
                "es_arbitro": es_arbitro,
                "posicion": participante["posicion"],
                "t_amarillas": participante["t_amarillas"],
                "t_rojas": participante["t_rojas"],
                "goles": participante["goles"],
                "equipo_nombre": participante["equipo_nombre"] or "Sin equipo"
            }
            
            # Rellenar formulario en modo "ver"
            self.modo_actual = "ver"
            self.vista.rellenar_formulario(datos_formulario, modo="ver")
            
            # Si es árbitro, cargar partidos arbitrados
            if es_arbitro:
                from app.models.match_model import MatchModel
                partidos_arbitrados = MatchModel.obtener_partidos_arbitrados(self.participante_actual_id)
                self.vista.set_partidos_arbitrados(partidos_arbitrados)
    
    def _on_nuevo(self):
        """Maneja la acción de crear un nuevo participante."""
        self.participante_actual_id = None
        self.modo_actual = "crear"
        
        # Limpiar formulario y poner en modo crear
        datos_vacios = {
            "nombre": "",
            "apellidos": "",
            "fecha_nacimiento": "",
            "curso": "1º ESO",
            "es_jugador": True,
            "es_arbitro": False,
            "posicion": "Delantero",
            "t_amarillas": 0,
            "t_rojas": 0,
            "goles": 0,
            "equipo_nombre": "Sin equipo"
        }
        self.vista.rellenar_formulario(datos_vacios, modo="crear")
    
    def _on_editar(self):
        """Maneja la acción de editar el participante actual."""
        if not self.participante_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un participante para editar."
            )
            return
        
        participante = ParticipantModel.obtener_participante_por_id(self.participante_actual_id)
        
        if not participante:
            QMessageBox.warning(
                self.vista,
                "Error",
                "No se pudo cargar el participante seleccionado."
            )
            return
        
        es_jugador = participante["tipo_jugador"] in ("Jugador", "Ambos")
        es_arbitro = participante["tipo_jugador"] in ("Árbitro", "Ambos")
        
        datos_formulario = {
            "nombre": participante["nombre"],
            "apellidos": participante["apellidos"] or "",
            "fecha_nacimiento": participante["fecha_nacimiento"],
            "curso": participante["curso"],
            "es_jugador": es_jugador,
            "es_arbitro": es_arbitro,
            "posicion": participante["posicion"],
            "t_amarillas": participante["t_amarillas"],
            "t_rojas": participante["t_rojas"],
            "goles": participante["goles"],
            "equipo_nombre": participante["equipo_nombre"] or "Sin equipo"
        }
        
        self.modo_actual = "editar"
        self.vista.rellenar_formulario(datos_formulario, modo="editar")
    
    def _on_eliminar(self):
        """Maneja la acción de eliminar el participante actual."""
        if not self.participante_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un participante para eliminar."
            )
            return
        
        # Confirmación
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar este participante?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                ParticipantModel.eliminar_participante(self.participante_actual_id)
                
                # Emitir evento
                self.event_bus.participant_deleted.emit(self.participante_actual_id)
                
                self.participante_actual_id = None
                self.modo_actual = "ver"
                
                # Limpiar formulario y recargar tabla
                self.vista.limpiar_formulario()
                self.cargar_tabla()
                
                QMessageBox.information(
                    self.vista,
                    "Éxito",
                    "Participante eliminado correctamente."
                )
            except Exception as e:
                QMessageBox.critical(
                    self.vista,
                    "Error",
                    f"Error al eliminar participante: {str(e)}"
                )
    
    def _on_guardar(self):
        """Maneja la acción de guardar (crear o actualizar) un participante."""
        # Obtener datos del formulario
        datos_formulario = self.vista.obtener_datos_formulario()
        
        # Validar que al menos un rol esté marcado
        es_jugador = datos_formulario.get("es_jugador", False)
        es_arbitro = datos_formulario.get("es_arbitro", False)
        
        if not es_jugador and not es_arbitro:
            QMessageBox.warning(
                self.vista,
                "Validación",
                "Debe marcar al menos un rol (Jugador o Árbitro)."
            )
            return
        
        # Determinar tipo_jugador
        if es_jugador and es_arbitro:
            tipo_jugador = "Ambos"
        elif es_jugador:
            tipo_jugador = "Jugador"
        else:
            tipo_jugador = "Árbitro"
        
        # Normalizar posición y equipo según el rol
        posicion = datos_formulario.get("posicion", "Sin definir")
        equipo_nombre = datos_formulario.get("equipo_nombre", "Sin equipo")
        
        if not es_jugador:
            # Si no es jugador, forzar posición a "Sin definir" y quitar equipo
            posicion = "Sin definir"
            equipo_id = None
        else:
            # Si es jugador, permitir equipo NULL o asignado
            if equipo_nombre == "Sin equipo":
                equipo_id = None
            else:
                equipo_id = self.equipos_dict.get(equipo_nombre)
        
        # Preparar datos para el modelo
        datos_participante = {
            "nombre": datos_formulario.get("nombre", ""),
            "apellidos": datos_formulario.get("apellidos", ""),
            "fecha_nacimiento": datos_formulario.get("fecha_nacimiento", ""),
            "curso": datos_formulario.get("curso", ""),
            "tipo_jugador": tipo_jugador,
            "posicion": posicion,
            "t_amarillas": datos_formulario.get("t_amarillas", 0),
            "t_rojas": datos_formulario.get("t_rojas", 0),
            "goles": datos_formulario.get("goles", 0),
            "equipo_id": equipo_id
        }
        
        try:
            if self.modo_actual == "crear":
                # Crear nuevo participante
                participante_id = ParticipantModel.crear_participante(datos_participante)
                self.participante_actual_id = participante_id
                mensaje = "Participante creado correctamente."
                
                # Emitir evento
                self.event_bus.participant_created.emit(participante_id)
            else:
                # Actualizar participante existente
                ParticipantModel.actualizar_participante(
                    self.participante_actual_id,
                    datos_participante
                )
                mensaje = "Participante actualizado correctamente."
                
                # Emitir evento
                self.event_bus.participant_updated.emit(self.participante_actual_id)
            
            # Recargar tabla y volver a modo "ver"
            self.cargar_tabla()
            
            # Recargar datos del participante actual
            if self.participante_actual_id:
                participante = ParticipantModel.obtener_participante_por_id(
                    self.participante_actual_id
                )
                if participante:
                    self._on_seleccionado(participante)
            
            QMessageBox.information(self.vista, "Éxito", mensaje)
            
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al guardar participante: {str(e)}"
            )
    
    def _on_cancelar(self):
        """Maneja la acción de cancelar la edición/creación."""
        self.modo_actual = "ver"
        
        if self.participante_actual_id:
            participante = ParticipantModel.obtener_participante_por_id(
                self.participante_actual_id
            )
            if participante:
                self._on_seleccionado(participante)
            else:
                self.vista.limpiar_formulario()
                self.vista.set_modo("ver")
        else:
            self.vista.limpiar_formulario()
            self.vista.set_modo("ver")
    
    def _on_guardar_equipo(self):
        """Maneja la acción de guardar asignación de equipo desde el comboEquipo."""
        if not self.participante_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un participante para asignar equipo."
            )
            return
        
        # Verificar que el participante sea jugador
        participante = ParticipantModel.obtener_participante_por_id(
            self.participante_actual_id
        )
        
        if participante and participante["tipo_jugador"] not in ("Jugador", "Ambos"):
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Solo se puede asignar equipo a participantes con rol de Jugador."
            )
            return
        
        # Obtener equipo seleccionado del comboEquipo
        equipo_id = self.vista.comboEquipo.currentData()
        
        if equipo_id is None:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un equipo válido."
            )
            return
        
        try:
            ParticipantModel.asignar_a_equipo(self.participante_actual_id, equipo_id)
            self.cargar_tabla()
            
            # Recargar datos del participante
            participante = ParticipantModel.obtener_participante_por_id(
                self.participante_actual_id
            )
            if participante:
                self._on_seleccionado(participante)
            
            QMessageBox.information(
                self.vista,
                "Éxito",
                "Equipo asignado correctamente."
            )
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al asignar equipo: {str(e)}"
            )
    
    def _on_quitar_equipo(self):
        """Maneja la eliminación de la asignación de equipo del participante actual."""
        if not self.participante_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un participante para quitar equipo."
            )
            return
        
        # Confirmación
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar",
            "¿Está seguro de que desea quitar el equipo asignado?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                ParticipantModel.asignar_a_equipo(self.participante_actual_id, None)
                self.cargar_tabla()
                
                # Recargar datos del participante
                participante = ParticipantModel.obtener_participante_por_id(
                    self.participante_actual_id
                )
                if participante:
                    self._on_seleccionado(participante)
                
                QMessageBox.information(
                    self.vista,
                    "Éxito",
                    "Equipo eliminado correctamente."
                )
            except Exception as e:
                QMessageBox.critical(
                    self.vista,
                    "Error",
                    f"Error al quitar equipo: {str(e)}"
                )
    
    # ==================== LISTENERS DEL EVENT BUS ====================
    
    def _on_team_changed_external(self, team_id: int):
        """
        Escucha cambios en equipos desde otros módulos.
        Recarga los combos de equipos cuando hay cambios.
        """
        print(f"[ParticipantsController] Cambio en equipo {team_id}, recargando filtros...")
        self.cargar_filtros()


