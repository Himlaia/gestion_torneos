"""
Controlador para la gestión de partidos y calendario.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from app.models.match_model import MatchModel
from app.models.participant_model import ParticipantModel
from app.models.callup_model import CallupModel
from app.models.match_stats_model import MatchStatsModel
from app.models.goal_model import GoalModel
from app.services.tournament_service import TournamentService
from app.services.match_service import MatchService, MatchData
from app.services.event_bus import get_event_bus


class ControladorCalendarioPartidos:
    """Controlador para conectar la vista de partidos con los modelos y servicios."""
    
    def __init__(self, vista):
        """
        Inicializa el controlador y conecta las señales de la vista.
        
        Args:
            vista: Instancia de PageCalendarioPartidos
        """
        self.vista = vista
        self.partido_actual_id = None
        self.partido_actual = None
        self.bracket_controller = None  # Referencia al controlador del cuadro
        self.equipos_dict = {}  # Diccionario para conversión nombre->id
        
        # Obtener event bus
        self.event_bus = get_event_bus()
        
        # Conectar al event bus para recibir actualizaciones
        self._conectar_event_bus()
        
        # Conectar señales
        self._conectar_senales()
        
        # Cargar datos iniciales
        self.cargar_equipos()
        self.cargar_arbitros()
        self.cargar_tabla()
    
    def set_bracket_controller(self, bracket_controller):
        """
        Establece la referencia al controlador del cuadro de eliminatorias.
        
        Args:
            bracket_controller: Instancia de ControladorCuadroEliminatorias
        """
        self.bracket_controller = bracket_controller
    
    def _conectar_event_bus(self):
        """Conecta el controlador al event bus para recibir actualizaciones."""
        # Escuchar cambios en equipos para actualizar combos
        self.event_bus.team_changed.connect(self._on_team_changed_external)
        
        # Escuchar cambios en participantes para actualizar listas
        self.event_bus.participant_changed.connect(self._on_participant_changed_external)
        
        # Escuchar cambios en otros partidos para refrescar tabla
        self.event_bus.match_changed.connect(self._on_match_changed_external)
    
    def _on_team_changed_external(self, team_id: int):
        """Maneja cambios en equipos desde otras partes de la app."""
        # Recargar lista de equipos en combos
        self.cargar_equipos()
        
        # Si el partido actual involucra este equipo, recargar detalle
        if self.partido_actual:
            if (self.partido_actual.get('equipo_local_id') == team_id or
                self.partido_actual.get('equipo_visitante_id') == team_id):
                # Recargar partido completo
                self.partido_actual = MatchModel.obtener_partido_por_id(self.partido_actual_id)
                if self.partido_actual:
                    self.vista.rellenar_detalle(self.partido_actual)
    
    def _on_participant_changed_external(self, participant_id: int):
        """Maneja cambios en participantes desde otras partes de la app."""
        # Recargar árbitros
        self.cargar_arbitros()
        
        # Si estamos viendo un partido, recargar jugadores disponibles
        if self.partido_actual_id:
            self.cargar_jugadores_disponibles()
            self.cargar_convocados()
    
    def _on_match_changed_external(self, match_id: int):
        """Maneja cambios en partidos desde otras partes de la app."""
        print(f"\n[MATCHES CONTROLLER] _on_match_changed_external recibido: match_id={match_id}")
        
        # Si match_id es 0, es un cambio general (múltiples partidos)
        if match_id == 0:
            print("[DEBUG] Cambio general detectado, recargando tabla completa...")
            self.cargar_tabla()
            print("[DEBUG] ✅ Tabla recargada")
            
            # También refrescar el calendario
            if hasattr(self.vista, 'calendario_partidos'):
                print("[DEBUG] Refrescando marcas del calendario...")
                self.vista.calendario_partidos.refresh_calendar_marks()
                print("[DEBUG] ✅ Calendario refrescado")
            return
        
        # Si no es el partido actual, solo refrescar tabla
        if match_id != self.partido_actual_id:
            print(f"[DEBUG] Cambio en partido {match_id} (no es el actual), recargando tabla...")
            self.cargar_tabla()
            print("[DEBUG] ✅ Tabla recargada")
        # Si es el actual, ya se habrá refrescado localmente
        else:
            print(f"[DEBUG] Cambio en partido actual {match_id}, ya manejado localmente")
    
    def _conectar_senales(self):
        """Conecta todas las señales de la vista con los métodos del controlador."""
        print("[CONTROLLER] _conectar_senales() - Iniciando conexión de señales...")
        
        # Acciones principales
        try:
            self.vista.nuevo_partido_signal.connect(self._on_nuevo_partido)
            print("  ✅ nuevo_partido_signal conectado a _on_nuevo_partido")
        except Exception as e:
            print(f"  ❌ ERROR conectando nuevo_partido_signal: {e}")
        
        # Selección y filtros
        self.vista.partido_seleccionado_signal.connect(self._on_seleccionado)
        self.vista.filtros_changed_signal.connect(self._on_filtros_changed)
        self.vista.abrir_partido_desde_dialogo_signal.connect(self._on_abrir_partido_desde_dialogo)
        
        # Edición de partido
        self.vista.guardar_partido_signal.connect(self._on_guardar_partido)
        self.vista.eliminar_partido_signal.connect(self._on_eliminar_partido)
        self.vista.cancelar_partido_signal.connect(self._on_cancelar_partido)
        
        # Convocatoria: conectar señal de cambios para persistir automáticamente
        self.vista.convocatoria_changed_signal.connect(self._on_convocatoria_cambiada)
        
        # Resultado
        self.vista.guardar_resultado_signal.connect(self._on_guardar_resultado)
        self.vista.cancelar_cambios_signal.connect(self._on_cancelar)
        
        # Validación de fase
        try:
            self.vista.fase_changed_signal.connect(self._on_fase_changed)
            print("  ✅ fase_changed_signal conectado a _on_fase_changed")
        except Exception as e:
            print(f"  ❌ ERROR conectando fase_changed_signal: {e}")
    
    def cargar_arbitros(self):
        """Carga la lista de árbitros disponibles."""
        arbitros = ParticipantModel.listar_arbitros()
        
        # Crear lista de nombres para el combo
        lista_arbitros = ["Sin asignar"] + [
            f"{arb['nombre']} {arb['apellidos'] or ''}".strip() 
            for arb in arbitros
        ]
        
        # Guardar diccionario para conversión
        self.arbitros_dict = {
            f"{arb['nombre']} {arb['apellidos'] or ''}".strip(): arb['id'] 
            for arb in arbitros
        }
        
        # Cargar en la vista
        self.vista.cargar_arbitros_en_combo(lista_arbitros)
    
    def cargar_tabla(self):
        """Carga los partidos en la tabla según los filtros actuales."""
        print("\n[MATCHES CONTROLLER] cargar_tabla INICIADO")
        filtros = self.vista.obtener_filtros_actuales()
        print(f"[DEBUG] Filtros actuales: {filtros}")
        
        eliminatoria = filtros.get("eliminatoria")
        estado = filtros.get("estado")
        
        if eliminatoria == "Todos":
            eliminatoria = None
        if estado == "Todos":
            estado = None
        elif estado == "Pendientes":
            estado = "Pendiente"
        elif estado == "Jugados":
            estado = "Jugado"
        
        print(f"[DEBUG] Llamando a MatchModel.listar_partidos(eliminatoria={eliminatoria}, estado={estado})")
        partidos = MatchModel.listar_partidos(
            eliminatoria=eliminatoria,
            estado=estado
        )
        print(f"[DEBUG] Partidos obtenidos: {len(partidos)}")
        
        if len(partidos) > 0:
            print(f"[DEBUG] Primeros 3 partidos:")
            for i, p in enumerate(partidos[:3], 1):
                print(f"  {i}. ID:{p.get('id')} Fase:{p.get('eliminatoria')} Estado:{p.get('estado')} Fecha:{p.get('fecha_hora')}")
        
        self.vista.actualizar_tabla(partidos)
        print("[DEBUG] ✅ Vista actualizada\n")
    
    def _on_filtros_changed(self, filtros: dict):
        """
        Maneja el cambio en los filtros.
        
        Args:
            filtros: Diccionario con los valores de los filtros
        """
        self.cargar_tabla()
    
    def _on_seleccionado(self, datos: dict):
        """
        Maneja la selección de un partido en la tabla.
        
        Args:
            datos: Diccionario con los datos del partido seleccionado
        """
        self.partido_actual_id = datos.get("id")
        
        # Obtener datos completos del partido
        self.partido_actual = MatchModel.obtener_partido_por_id(self.partido_actual_id)
        
        if self.partido_actual:
            # Rellenar detalle del partido
            self.vista.rellenar_detalle(self.partido_actual)
            
            # Cargar jugadores disponibles de ambos equipos
            self.cargar_jugadores_disponibles()
            
            # Cargar convocados existentes
            self.cargar_convocados()
            
            # Cargar estadísticas si existen
            self.cargar_stats()
            
            # Cargar goles guardados en el caché
            goles_guardados = GoalModel.obtener_goles_partido(self.partido_actual_id)
            print(f"[DEBUG _on_seleccionado] Cargados {len(goles_guardados)} goles desde BD para partido {self.partido_actual_id}")
            self.vista.goles_detalle_cache = goles_guardados
            
            # Determinar modo según estado del partido
            estado = self.partido_actual.get('estado', 'Pendiente')
            if estado == 'Jugado':
                # Partido ya jugado, permitir editar resultado
                self.vista.set_modo("editar_resultado")
            else:
                # Partido pendiente, modo ver
                self.vista.set_modo("ver")
    
    def cargar_jugadores_disponibles(self):
        """Carga los jugadores disponibles de ambos equipos del partido."""
        if not self.partido_actual:
            return
        
        local_id = self.partido_actual.get("local_id")
        visitante_id = self.partido_actual.get("visitante_id")
        local_nombre = self.partido_actual.get("local_nombre")
        visitante_nombre = self.partido_actual.get("visitante_nombre")
        
        if not local_id or not visitante_id:
            return
        
        # Obtener todos los jugadores de cada equipo
        jugadores_local_raw = ParticipantModel.listar_jugadores_por_equipo(local_id)
        jugadores_visitante_raw = ParticipantModel.listar_jugadores_por_equipo(visitante_id)
        
        # Filtrar solo jugadores válidos:
        # - tipo_jugador = "Jugador" o "Ambos"
        # - equipo_id debe coincidir (excluir sin equipo)
        jugadores_local = [
            j for j in jugadores_local_raw
            if j.get("tipo_jugador") in ("Jugador", "Ambos") and j.get("equipo_id") == local_id
        ]
        
        jugadores_visitante = [
            j for j in jugadores_visitante_raw
            if j.get("tipo_jugador") in ("Jugador", "Ambos") and j.get("equipo_id") == visitante_id
        ]
        
        # Verificar si algún equipo no tiene jugadores válidos
        tiene_error = False
        mensaje_error = ""
        
        if len(jugadores_local) == 0 and len(jugadores_visitante) == 0:
            tiene_error = True
            mensaje_error = (
                f"⚠️ ADVERTENCIA: Ninguno de los equipos tiene jugadores disponibles.\n"
                f"Asegúrese de que los jugadores estén asignados a sus equipos."
            )
        elif len(jugadores_local) == 0:
            tiene_error = True
            mensaje_error = (
                f"⚠️ ADVERTENCIA: El equipo local '{local_nombre}' no tiene jugadores disponibles.\n"
                f"Asigne jugadores a este equipo antes de continuar."
            )
        elif len(jugadores_visitante) == 0:
            tiene_error = True
            mensaje_error = (
                f"⚠️ ADVERTENCIA: El equipo visitante '{visitante_nombre}' no tiene jugadores disponibles.\n"
                f"Asigne jugadores a este equipo antes de continuar."
            )
        
        # Enviar a la vista
        self.vista.cargar_jugadores_disponibles(jugadores_local, jugadores_visitante)
        
        # Si hay error, deshabilitar guardado y mostrar aviso
        if tiene_error:
            self.vista.deshabilitar_guardar_resultado()
            self.vista.mostrar_aviso_sin_jugadores(mensaje_error)
        else:
            self.vista.habilitar_guardar_resultado()
            self.vista.ocultar_aviso_sin_jugadores()
    
    def cargar_convocados(self):
        """Carga los jugadores convocados para el partido actual."""
        if not self.partido_actual_id:
            return
        
        convocados = CallupModel.listar_convocados(self.partido_actual_id)
        
        # Separar por equipo
        convocados_local = []
        convocados_visitante = []
        
        local_id = self.partido_actual.get("local_id")
        
        for convocado in convocados:
            if convocado.get("equipo_id") == local_id:
                convocados_local.append(convocado)
            else:
                convocados_visitante.append(convocado)
        
        # Enviar a la vista
        self.vista.cargar_convocados(convocados_local, convocados_visitante)
    
    def cargar_stats(self):
        """Carga las estadísticas del partido si existen."""
        if not self.partido_actual_id:
            return
        
        print(f"[CONTROLLER cargar_stats] Cargando stats para partido {self.partido_actual_id}")
        
        stats = MatchStatsModel.obtener_stats(self.partido_actual_id)
        print(f"[CONTROLLER cargar_stats] Obtenidas {len(stats)} estadísticas de BD")
        
        if stats:
            self.vista.cargar_stats(stats)
            print(f"[CONTROLLER cargar_stats] Stats cargadas en vista")
        
        # Cargar goles detallados en el caché si existen
        goles = GoalModel.obtener_goles_partido(self.partido_actual_id)
        print(f"[CONTROLLER cargar_stats] Obtenidos {len(goles)} goles de BD")
        
        if goles:
            self.vista.goles_detalle_cache = goles
            # Sincronizar goles en la tabla de estadísticas
            self.vista.sincronizar_goles_en_stats()
            print(f"[CONTROLLER cargar_stats] ✓ Goles cargados y sincronizados")
        else:
            # Limpiar goles si no hay
            self.vista.goles_detalle_cache = []
            self.vista.sincronizar_goles_en_stats()
            print(f"[CONTROLLER cargar_stats] No hay goles, caché limpiado")
    
    def _on_convocatoria_cambiada(self, datos: dict):
        """
        Maneja los cambios en la convocatoria (añadir/quitar jugadores).
        
        Args:
            datos: Diccionario con accion, participante_id, equipo_id
        """
        if not self.partido_actual_id:
            return
        
        accion = datos.get("accion")
        participante_id = datos.get("participante_id")
        equipo_id = datos.get("equipo_id")
        
        if not participante_id or not equipo_id:
            return
        
        try:
            if accion == "convocar":
                # Añadir jugador a convocatoria
                CallupModel.convocar_jugador(
                    self.partido_actual_id,
                    participante_id,
                    equipo_id
                )
                
                # Inicializar stats para este jugador
                MatchStatsModel.inicializar_stats(
                    self.partido_actual_id,
                    [participante_id]
                )
                
            elif accion == "quitar":
                # Quitar jugador de convocatoria
                CallupModel.quitar_convocado(
                    self.partido_actual_id,
                    participante_id
                )
            
            # Recargar convocados y stats
            self.cargar_convocados()
            self.cargar_stats()
            
        except Exception as e:
            QMessageBox.warning(
                self.vista,
                "Error",
                f"Error al actualizar convocatoria: {str(e)}"
            )
    
    def _on_asignar_arbitro(self):
        """Maneja la asignación de un árbitro al partido actual."""
        if not self.partido_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un partido para asignar árbitro."
            )
            return
        
        # Obtener árbitro seleccionado del combo
        datos_formulario = self.vista.obtener_datos_formulario()
        arbitro_nombre = datos_formulario.get("arbitro_nombre", "Sin asignar")
        
        if arbitro_nombre == "Sin asignar":
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un árbitro válido."
            )
            return
        
        arbitro_id = self.arbitros_dict.get(arbitro_nombre)
        
        if not arbitro_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Árbitro no encontrado."
            )
            return
        
        try:
            MatchModel.asignar_arbitro(self.partido_actual_id, arbitro_id)
            self.cargar_tabla()
            
            # Recargar datos del partido
            partido = MatchModel.obtener_partido_por_id(self.partido_actual_id)
            if partido:
                self.vista.rellenar_detalle(partido)
            
            QMessageBox.information(
                self.vista,
                "Éxito",
                "Árbitro asignado correctamente."
            )
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al asignar árbitro: {str(e)}"
            )
    
    def _on_quitar_arbitro(self):
        """Maneja la eliminación de la asignación de árbitro del partido actual."""
        if not self.partido_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un partido para quitar árbitro."
            )
            return
        
        # Confirmación
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar",
            "¿Está seguro de que desea quitar el árbitro asignado?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                MatchModel.quitar_arbitro(self.partido_actual_id)
                self.cargar_tabla()
                
                # Recargar datos del partido
                partido = MatchModel.obtener_partido_por_id(self.partido_actual_id)
                if partido:
                    self.vista.rellenar_detalle(partido)
                
                QMessageBox.information(
                    self.vista,
                    "Éxito",
                    "Árbitro eliminado correctamente."
                )
            except Exception as e:
                QMessageBox.critical(
                    self.vista,
                    "Error",
                    f"Error al quitar árbitro: {str(e)}"
                )
    
    def _on_guardar_resultado(self):
        """Maneja la acción de guardar el resultado de un partido usando MatchService."""
        if not self.partido_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un partido para guardar resultado."
            )
            return
        
        # Cargar partido con MatchService para validación robusta
        match = MatchService.load_match(self.partido_actual_id)
        if not match:
            QMessageBox.critical(
                self.vista,
                "Error",
                "No se pudo cargar el partido.\n\nPor favor, seleccione el partido nuevamente."
            )
            return
        
        # Validar con MatchService
        es_valido, mensaje = MatchService.validate_for_result_save(match)
        if not es_valido:
            QMessageBox.warning(
                self.vista,
                "Validación",
                mensaje
            )
            return
        
        # Obtener datos del formulario usando el método correcto
        datos_formulario = self.vista.get_datos_resultado()
        
        goles_local = datos_formulario.get("goles_local", 0)
        goles_visitante = datos_formulario.get("goles_visitante", 0)
        penaltis_local = datos_formulario.get("penaltis_local")
        penaltis_visitante = datos_formulario.get("penaltis_visitante")
        
        print(f"\n[CONTROLLER] Datos del formulario:")
        print(f"  - Goles: {goles_local}-{goles_visitante}")
        print(f"  - Penaltis: {penaltis_local}-{penaltis_visitante}")
        print(f"  - Stats: {len(datos_formulario.get('stats', []))} jugadores")
        
        # Validar empate en goles y penaltis
        if goles_local != goles_visitante:
            # No es empate, ignorar penaltis
            penaltis_local = None
            penaltis_visitante = None
        else:
            # Es empate, validar penaltis
            if penaltis_local == penaltis_visitante:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    "No puede haber empate en goles y penaltis.\n"
                    "Debe haber un ganador definido en penaltis."
                )
                return
        
        # Obtener estadísticas
        stats = datos_formulario.get("stats", [])
        
        # Obtener goles con autor (nueva funcionalidad)
        goles_detalle = self.vista.get_goles_detalle()
        
        print(f"  - Goles detallados: {len(goles_detalle)}")
        if goles_detalle:
            print(f"[CONTROLLER] Primeros 3 goles detallados:")
            for i, gol in enumerate(goles_detalle[:3], 1):
                print(f"    {i}. Participante {gol.get('participante_id')} - Equipo {gol.get('equipo_id')} - Min {gol.get('minuto')}")
        
        # Confirmación
        msg_goles = f"\nSe registrarán {len(goles_detalle)} goles con autor." if goles_detalle else ""
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar",
            f"¿Está seguro de que desea guardar este resultado?\n"
            f"Esta acción marcará el partido como jugado y actualizará las estadísticas.{msg_goles}\n"
            f"El ganador será avanzado automáticamente a la siguiente ronda.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        try:
            print(f"\n[CONTROLLER] ========== GUARDANDO RESULTADO ==========")
            
            # Guardar resultado con MatchService (incluye goles con autor)
            resultado = MatchService.save_result_with_goals(
                partido_id=self.partido_actual_id,
                goles_local=goles_local,
                goles_visitante=goles_visitante,
                penaltis_local=penaltis_local,
                penaltis_visitante=penaltis_visitante,
                goles_detalle=goles_detalle,
                stats=stats
            )
            
            print(f"[CONTROLLER] ✓ Resultado guardado exitosamente")
            print(f"[CONTROLLER] Ganador: {resultado.get('ganador_equipo_id')}")
            print(f"[CONTROLLER] ============================================\n")
            
            # Actualizar acumulados de participantes
            try:
                ParticipantModel.actualizar_acumulados(self.partido_actual_id)
            except Exception as e:
                print(f"Advertencia: Error al actualizar acumulados: {str(e)}")
            
            # Limpiar dirty flags
            self.vista.clear_all_dirty_flags()
            
            print(f"[CONTROLLER] Recargando datos del partido...")
            
            # Recargar datos del partido
            self.partido_actual = MatchModel.obtener_partido_por_id(self.partido_actual_id)
            if self.partido_actual:
                self.vista.rellenar_detalle(self.partido_actual)
            
            # Recargar tabla de partidos
            self.cargar_tabla()
            
            # Recargar estadísticas Y goles (cargar_stats ahora también carga goles y sincroniza)
            self.cargar_stats()
            
            print(f"[CONTROLLER] Datos recargados exitosamente")
            
            # Mostrar mensaje de éxito
            msg_exito = "El resultado se ha guardado correctamente.\n"
            if goles_detalle:
                msg_exito += f"Se registraron {len(goles_detalle)} goles con autor.\n"
            msg_exito += "El ganador ha sido avanzado a la siguiente ronda automáticamente."
            
            QMessageBox.information(
                self.vista,
                "Éxito",
                msg_exito
            )
            
            # Mantener en modo editar_resultado para permitir correcciones
            self.vista.set_modo("editar_resultado")
            
        except ValueError as ve:
            # Error de validación o datos incorrectos
            print(f"[ERROR] ValueError al guardar resultado: {ve}")
            QMessageBox.critical(
                self.vista,
                "Error de validación",
                f"No se pudo guardar el resultado debido a datos incorrectos:\n\n{str(ve)}\n\n"
                "Por favor, verifique que:\n"
                "• Los equipos estén correctamente asignados\n"
                "• El árbitro esté asignado\n"
                "• Los goles y penaltis sean válidos"
            )
        except KeyError as ke:
            # Error de clave faltante en el diccionario del partido
            print(f"[ERROR] KeyError al guardar resultado: {ke}")
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(
                self.vista,
                "Error de datos",
                f"Falta información del partido (clave: {ke}).\n\n"
                "Esto puede ocurrir si:\n"
                "• El partido no se guardó correctamente en la pestaña 'Datos'\n"
                "• Faltan equipos asignados\n\n"
                "Solución:\n"
                "1. Vaya a la pestaña 'Datos'\n"
                "2. Verifique que equipo local y visitante estén asignados\n"
                "3. Pulse 'Guardar' para confirmar\n"
                "4. Intente guardar el resultado nuevamente"
            )
        except Exception as e:
            # Error general
            import traceback
            print(f"[ERROR] Error al guardar resultado: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(
                self.vista,
                "Error",
                f"No se pudo guardar el resultado:\n\n{str(e)}\n\n"
                "Si el problema persiste, consulte los logs de la aplicación."
            )
    
    def _on_cancelar(self):
        """Maneja la acción de cancelar cambios."""
        if self.partido_actual_id:
            # Recargar datos del partido actual
            self.partido_actual = MatchModel.obtener_partido_por_id(self.partido_actual_id)
            if self.partido_actual:
                self.vista.rellenar_detalle(self.partido_actual)
                self.cargar_convocados()
                self.cargar_stats()
        else:
            # Limpiar detalle
            self.vista.limpiar_detalle()
    
    def _on_fecha_hora_cambiada(self, nueva_fecha: str):
        """Maneja el cambio de fecha/hora del partido."""
        if not self.partido_actual_id:
            return
        
        try:
            MatchModel.actualizar_fecha_hora(self.partido_actual_id, nueva_fecha)
            self.cargar_tabla()
        except Exception as e:
            QMessageBox.warning(
                self.vista,
                "Error",
                f"Error al actualizar fecha/hora: {str(e)}"
            )
    
    def _on_arbitro_cambiado(self, nombre_arbitro: str):
        """Maneja el cambio de árbitro del partido."""
        if not self.partido_actual_id:
            return
        
        try:
            arbitro_id = self.arbitros_dict.get(nombre_arbitro)
            if arbitro_id:
                MatchModel.asignar_arbitro(self.partido_actual_id, arbitro_id)
                self.cargar_tabla()
        except Exception as e:
            QMessageBox.warning(
                self.vista,
                "Error",
                f"Error al asignar árbitro: {str(e)}"
            )
    
    def _on_generar_partidos(self):
        """Genera los partidos de octavos de final."""
        try:
            from app.models.team_model import TeamModel
            
            # Obtener todos los equipos
            equipos = TeamModel.listar_equipos()
            
            if len(equipos) != 16:
                QMessageBox.warning(
                    self.vista,
                    "Error",
                    f"Se necesitan exactamente 16 equipos para generar el torneo.\n"
                    f"Actualmente hay {len(equipos)} equipos registrados."
                )
                return
            
            # Confirmar con el usuario
            respuesta = QMessageBox.question(
                self.vista,
                "Generar Partidos",
                "¿Desea generar los partidos de octavos de final?\n\n"
                "Esto creará 8 partidos con emparejamientos aleatorios.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if respuesta != QMessageBox.Yes:
                return
            
            # Obtener solo los IDs de los equipos
            equipos_ids = [equipo['id'] for equipo in equipos]
            
            # Generar emparejamientos aleatorios
            emparejamientos = TournamentService.randomizar_octavos(equipos_ids)
            
            # Crear los partidos en la base de datos
            TournamentService.generar_octavos_desde_emparejamientos(emparejamientos)
            
            # Recargar la tabla
            self.cargar_tabla()
            
            # Actualizar el cuadro de eliminatorias si existe
            if self.bracket_controller:
                self.bracket_controller.cargar_cuadro()
            
            # Refresh calendar marks
            self.vista.calendario_partidos.refresh_calendar_marks()
            
            QMessageBox.information(
                self.vista,
                "Éxito",
                "Se han generado los partidos de octavos de final correctamente.\n\n"
                "Ahora puedes programar las fechas y horarios desde el calendario."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al generar los partidos: {str(e)}"
            )
    
    def _on_reiniciar_torneo(self):
        """Reinicia el torneo eliminando todos los partidos y convocatorias."""
        try:
            print("[CONTROLLER] _on_reiniciar_torneo ejecutado")
            
            # Confirmación con el usuario
            respuesta = QMessageBox.question(
                self.vista,
                "Reiniciar Torneo",
                "⚠️ ¿Está seguro de que desea reiniciar el torneo?\n\n"
                "Esto eliminará TODOS los partidos, convocatorias y resultados.\n"
                "Esta acción NO se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if respuesta != QMessageBox.StandardButton.Yes:
                print("[CONTROLLER] Reinicio cancelado por usuario")
                return
            
            print("[CONTROLLER] Eliminando convocatorias...")
            # Eliminar convocatorias primero
            from app.models.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM convocados")
            conn.commit()
            
            print("[CONTROLLER] Eliminando partidos...")
            # Eliminar todos los partidos
            MatchModel.borrar_todos_los_partidos()
            
            # Limpiar estado actual
            self.partido_actual_id = None
            self.partido_actual = None
            
            print("[CONTROLLER] Limpiando UI...")
            # Limpiar vista
            self.vista.limpiar_formulario_partido()
            self.vista.set_modo("ver")
            
            # Actualizar label
            if hasattr(self.vista, 'partido_titulo'):
                self.vista.partido_titulo.setText("Seleccione un partido")
            
            # Recargar la tabla (estará vacía)
            self.cargar_tabla()
            
            # Actualizar el cuadro de eliminatorias si existe
            if self.bracket_controller:
                self.bracket_controller.cargar_cuadro()
            
            # Refrescar calendario
            self.vista.calendario_partidos.refresh_calendar_marks()
            
            print("[CONTROLLER] Torneo reiniciado exitosamente")
            QMessageBox.information(
                self.vista,
                "Éxito",
                "El torneo ha sido reiniciado correctamente."
            )
            
        except Exception as e:
            print(f"[CONTROLLER ERROR] _on_reiniciar_torneo: {e}")
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al reiniciar el torneo: {str(e)}"
            )
    
    def _on_abrir_partido_desde_dialogo(self, partido_id: int):
        """Carga el partido seleccionado desde el diálogo en el panel derecho."""
        print(f"[CONTROLLER] _on_abrir_partido_desde_dialogo: partido_id={partido_id}")
        
        try:
            # Obtener datos completos del partido
            partido = MatchModel.obtener_partido_por_id(partido_id)
            
            if not partido:
                print(f"[ERROR] No se encontró el partido con ID {partido_id}")
                QMessageBox.warning(
                    self.vista,
                    "Error",
                    "No se pudo cargar el partido seleccionado."
                )
                return
            
            print(f"[CONTROLLER] Partido cargado: {partido.get('local_nombre')} vs {partido.get('visitante_nombre')}")
            
            # Guardar referencia en controlador Y en vista
            self.partido_actual_id = partido_id
            self.partido_actual = partido
            self.vista.partido_actual_id = partido_id
            self.vista.partido_actual = partido
            
            # Habilitar explícitamente todos los controles del panel derecho
            if hasattr(self.vista, 'grupo_detalle'):
                self.vista.grupo_detalle.setEnabled(True)
            if hasattr(self.vista, 'tabs_detalle'):
                self.vista.tabs_detalle.setEnabled(True)
            if hasattr(self.vista, 'fecha_hora'):
                self.vista.fecha_hora.setEnabled(True)
            if hasattr(self.vista, 'comboArbitro'):
                self.vista.comboArbitro.setEnabled(True)
            
            # Rellenar detalle del partido
            print("[CONTROLLER] Rellenando detalle del partido...")
            self.vista.rellenar_detalle(partido)
            
            # Cambiar a tab "Datos" automáticamente
            self.vista.tabs_detalle.setCurrentIndex(0)
            
            # Cargar jugadores disponibles de ambos equipos
            print("[CONTROLLER] Cargando jugadores disponibles...")
            self.cargar_jugadores_disponibles()
            
            # Cargar convocados existentes
            print("[CONTROLLER] Cargando convocados...")
            self.cargar_convocados()
            
            # Cargar estadísticas si existen
            print("[CONTROLLER] Cargando estadísticas...")
            self.cargar_stats()
            
            # Cambiar a modo edición
            self.vista.set_modo("editar")
            self.vista.actualizar_estado_botones()
            
            print(f"[CONTROLLER] Partido {partido_id} cargado exitosamente")
            
        except Exception as e:
            print(f"[ERROR CRÍTICO] Error al cargar el partido: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al cargar el partido: {str(e)}"
            )
    
    def cargar_equipos(self):
        """Carga la lista de equipos disponibles."""
        from app.models.team_model import TeamModel
        
        equipos = TeamModel.listar_equipos()
        
        # Guardar diccionario para conversión
        self.equipos_dict = {eq['id']: eq['nombre'] for eq in equipos}
        
        # Cargar en la vista
        self.vista.cargar_equipos_en_combos(equipos)
    
    def is_previous_round_complete(self, target_fase: str) -> tuple[bool, str]:
        """
        Verifica si la fase anterior está completa para permitir crear partidos de target_fase.
        
        Args:
            target_fase: Fase objetivo (octavos, cuartos, semifinal, final)
            
        Returns:
            Tupla (bool, str): (True, "") si se puede, (False, mensaje) si no
        """
        from app.constants import FASES_CONFIG
        
        # Obtener configuración de la fase objetivo
        if target_fase not in FASES_CONFIG:
            return (False, f"Fase '{target_fase}' no reconocida")
        
        config = FASES_CONFIG[target_fase]
        prev_fase = config.get("prev")
        
        # Si no hay fase previa (ej: octavos), siempre se puede
        if not prev_fase:
            return (True, "")
        
        # Verificar cuántos partidos programados hay en la fase anterior
        prev_config = FASES_CONFIG[prev_fase]
        required_count = prev_config["required"]
        
        # Consultar DB
        from app.models.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM partidos 
            WHERE eliminatoria = ? 
              AND equipo_local_id IS NOT NULL 
              AND equipo_visitante_id IS NOT NULL 
              AND fecha_hora IS NOT NULL 
              AND estado != 'Cancelado'
        """, (prev_fase,))
        
        actual_count = cursor.fetchone()[0]
        conn.close()
        
        if actual_count < required_count:
            fase_label = prev_config["label"]
            target_label = config["label"]
            mensaje = (
                f"No puedes programar {target_label} hasta que estén programados "
                f"los {required_count} partidos de {fase_label}.\n\n"
                f"Actualmente hay {actual_count}/{required_count} partidos programados."
            )
            return (False, mensaje)
        
        return (True, "")
    
    def _on_fase_changed(self, fase_id: str):
        """Maneja el cambio de fase y valida prerrequisitos."""
        print(f"[CONTROLLER] _on_fase_changed: {fase_id}")
        
        # Validar que la fase anterior esté completa
        puede, mensaje = self.is_previous_round_complete(fase_id)
        
        if not puede:
            # Mostrar advertencia
            QMessageBox.warning(
                self.vista,
                "Fase no disponible",
                mensaje
            )
            
            # Revertir a la primera fase (Octavos)
            from app.constants import FASE_OCTAVOS, FASES_ORDEN
            for i in range(self.vista.comboFase.count()):
                if self.vista.comboFase.itemData(i) == FASE_OCTAVOS:
                    self.vista.comboFase.blockSignals(True)
                    self.vista.comboFase.setCurrentIndex(i)
                    self.vista.comboFase.blockSignals(False)
                    break
    
    def _on_nuevo_partido(self):
        """Maneja la creación de un nuevo partido."""
        try:
            print("[CONTROLLER] _on_nuevo_partido ejecutado")
            
            # Resetear referencias
            self.partido_actual_id = None
            self.partido_actual = None
            
            # Asegurar que combos de equipos están cargados
            if not hasattr(self, 'equipos_dict') or not self.equipos_dict:
                self.cargar_equipos()
            
            # Limpiar formulario
            self.vista.limpiar_formulario_partido()
            
            # Cambiar a modo crear (esto habilitará campos y botones)
            self.vista.set_modo("crear")
            
            # Actualizar estado de botones
            self.vista.actualizar_estado_botones()
            
            # Actualizar label de cabecera
            if hasattr(self.vista, 'partido_titulo'):
                self.vista.partido_titulo.setText("Nuevo partido")
            
        except Exception as e:
            print(f"[CONTROLLER ERROR] _on_nuevo_partido: {e}")
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al iniciar nuevo partido: {str(e)}"
            )
    
    def _on_guardar_partido(self):
        """Maneja el guardado (creación o actualización) de un partido."""
        try:
            # Obtener datos del formulario
            datos = self.vista.obtener_datos_partido()
            
            # Validaciones básicas
            if not datos['ronda'] or datos['ronda'].strip() == "":
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    "Debe especificar una fase válida."
                )
                return
            
            # 🔴 VALIDACIÓN DE FASE: Verificar que la fase anterior esté completa
            fase_id = datos['ronda']
            puede, mensaje = self.is_previous_round_complete(fase_id)
            if not puede:
                QMessageBox.warning(
                    self.vista,
                    "Fase no disponible",
                    mensaje
                )
                return
            
            if not datos['local_id']:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    "Debe seleccionar un equipo local."
                )
                return
            
            if not datos['visitante_id']:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    "Debe seleccionar un equipo visitante."
                )
                return
            
            if datos['local_id'] == datos['visitante_id']:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    "El equipo local y visitante deben ser diferentes."
                )
                return
            
            # 🔴 VALIDACIÓN DE CONVOCATORIA MÍNIMA (Fútbol 7)
            # Solo validar si el partido ya existe (tiene convocatoria) y estado es Programado o Jugado
            if self.partido_actual_id and datos['estado'] in ['Programado', 'Jugado']:
                es_valido, mensaje_error = self.vista.validar_convocatoria_minima()
                if not es_valido:
                    QMessageBox.warning(
                        self.vista,
                        "Convocatoria incompleta",
                        f"{mensaje_error}\n\nNo se puede establecer el partido como '{datos['estado']}' sin cumplir este requisito."
                    )
                    return
            
            # Resolver árbitro si no hay ID pero hay nombre
            arbitro_id = datos['arbitro_id']
            if arbitro_id is None and datos.get('arbitro_nombre'):
                arbitro_nombre = datos['arbitro_nombre']
                if arbitro_nombre != "Sin árbitro":
                    arbitro_id = self.arbitros_dict.get(arbitro_nombre)
            
            # Guardar en DB
            if self.partido_actual_id:
                # Actualizar partido existente
                MatchModel.actualizar_partido(
                    self.partido_actual_id,
                    datos['ronda'],
                    datos['fecha_hora'],
                    datos['local_id'],
                    datos['visitante_id'],
                    datos['estado'],
                    arbitro_id
                )
                mensaje = "Partido actualizado correctamente."
                
                # 🔧 CRITICAL: Emitir eventos para actualizar otras vistas
                self.event_bus.emit_match_updated(self.partido_actual_id)
            else:
                # Crear nuevo partido
                partido_id = MatchModel.insertar_partido(
                    datos['ronda'],
                    datos['fecha_hora'],
                    datos['local_id'],
                    datos['visitante_id'],
                    datos['estado'],
                    arbitro_id
                )
                self.partido_actual_id = partido_id
                mensaje = "Partido creado correctamente."
                
                # 🔧 CRITICAL: Emitir eventos para actualizar otras vistas
                self.event_bus.emit_match_created(partido_id)
            
            # Recargar tabla
            self.cargar_tabla()
            
            # Refrescar calendario
            self.vista.calendario_partidos.refresh_calendar_marks()
            
            # Recargar datos del partido
            if self.partido_actual_id:
                partido = MatchModel.obtener_partido_por_id(self.partido_actual_id)
                if partido:
                    self.partido_actual = partido
                    self.vista.rellenar_detalle(partido)
                    # Cargar jugadores y convocatoria
                    self.cargar_jugadores_disponibles()
                    self.cargar_convocados()
            
            # Cambiar a modo ver
            self.vista.set_modo("ver")
            
            # Actualizar estado de botones
            self.vista.actualizar_estado_botones()
            
            QMessageBox.information(
                self.vista,
                "Éxito",
                mensaje
            )
            
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al guardar partido: {str(e)}"
            )
    
    def _on_eliminar_partido(self):
        """Maneja la eliminación de un partido."""
        if not self.partido_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe seleccionar un partido para eliminar."
            )
            return
        
        # Confirmación
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar",
            "¿Está seguro de que desea eliminar este partido?\n\n"
            "Se eliminarán también las convocatorias y estadísticas asociadas.\n"
            "Esta acción NO se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                MatchModel.eliminar_partido(self.partido_actual_id)
                
                # Recargar tabla
                self.cargar_tabla()
                
                # Refrescar calendario
                self.vista.calendario_partidos.refresh_calendar_marks()
                
                # Limpiar formulario
                self.vista.limpiar_formulario_partido()
                self.partido_actual_id = None
                self.partido_actual = None
                
                # Cambiar a modo ver
                self.vista.set_modo("ver")
                
                # Actualizar estado de botones
                self.vista.actualizar_estado_botones()
                
                QMessageBox.information(
                    self.vista,
                    "Éxito",
                    "Partido eliminado correctamente."
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self.vista,
                    "Error",
                    f"Error al eliminar partido: {str(e)}"
                )
    
    def _on_cancelar_partido(self):
        """Maneja la cancelación de la edición/creación de un partido."""
        if self.partido_actual_id:
            # Si hay un partido seleccionado, recargar sus datos
            partido = MatchModel.obtener_partido_por_id(self.partido_actual_id)
            if partido:
                self.partido_actual = partido
                self.vista.rellenar_detalle(partido)
        else:
            # Si no hay partido seleccionado, limpiar formulario
            self.vista.limpiar_formulario_partido()
        
        # Cambiar a modo ver
        self.vista.set_modo("ver")
        
        # Actualizar estado de botones
        self.vista.actualizar_estado_botones()
        
        # Cambiar a modo ver
        self.vista.set_modo("ver")
    
    def _on_convocatoria_changed(self, equipo: str, accion: str):
        """Maneja los cambios en la convocatoria."""
        if not self.partido_actual_id:
            QMessageBox.warning(
                self.vista,
                "Aviso",
                "Debe guardar el partido antes de gestionar convocatorias."
            )
            return
        
        try:
            if equipo == "local":
                equipo_id = self.partido_actual.get("local_id")
                if accion == "anadir":
                    tabla_disponibles = self.vista.jugadores_disponibles_local
                    selected = tabla_disponibles.currentRow()
                    if selected >= 0:
                        item = tabla_disponibles.item(selected, 0)
                        participante_id = item.data(Qt.ItemDataRole.UserRole)
                        CallupModel.convocar_jugador(
                            self.partido_actual_id,
                            participante_id,
                            equipo_id
                        )
                        MatchStatsModel.inicializar_stats(
                            self.partido_actual_id,
                            [participante_id]
                        )
                elif accion == "quitar":
                    tabla_convocados = self.vista.jugadores_convocados_local
                    selected = tabla_convocados.currentRow()
                    if selected >= 0:
                        item = tabla_convocados.item(selected, 0)
                        participante_id = item.data(Qt.ItemDataRole.UserRole)
                        CallupModel.quitar_convocado(
                            self.partido_actual_id,
                            participante_id
                        )
            
            elif equipo == "visitante":
                equipo_id = self.partido_actual.get("visitante_id")
                if accion == "anadir":
                    tabla_disponibles = self.vista.jugadores_disponibles_visitante
                    selected = tabla_disponibles.currentRow()
                    if selected >= 0:
                        item = tabla_disponibles.item(selected, 0)
                        participante_id = item.data(Qt.ItemDataRole.UserRole)
                        CallupModel.convocar_jugador(
                            self.partido_actual_id,
                            participante_id,
                            equipo_id
                        )
                        MatchStatsModel.inicializar_stats(
                            self.partido_actual_id,
                            [participante_id]
                        )
                elif accion == "quitar":
                    tabla_convocados = self.vista.jugadores_convocados_visitante
                    selected = tabla_convocados.currentRow()
                    if selected >= 0:
                        item = tabla_convocados.item(selected, 0)
                        participante_id = item.data(Qt.ItemDataRole.UserRole)
                        CallupModel.quitar_convocado(
                            self.partido_actual_id,
                            participante_id
                        )
            
            # Recargar convocados y stats
            self.cargar_convocados()
            self.cargar_stats()
            
        except Exception as e:
            QMessageBox.warning(
                self.vista,
                "Error",
                f"Error al actualizar convocatoria: {str(e)}"
            )
    
    def _on_generar_partidos(self):
        """Genera partidos automáticamente (MVP simplificado)."""
        from app.models.team_model import TeamModel
        from datetime import datetime, timedelta
        
        try:
            # Obtener todos los equipos
            equipos = TeamModel.listar_equipos()
            
            if len(equipos) < 2:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    "Se necesitan al menos 2 equipos para generar partidos."
                )
                return
            
            # Confirmación
            respuesta = QMessageBox.question(
                self.vista,
                "Generar partidos",
                f"Se generarán partidos para {len(equipos)} equipos.\n\n"
                f"¿Desea continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta != QMessageBox.StandardButton.Yes:
                return
            
            # Generar emparejamientos simples
            num_equipos = len(equipos)
            fecha_base = datetime.now()
            
            partidos_creados = 0
            for i in range(0, num_equipos - 1, 2):
                local = equipos[i]
                visitante = equipos[i + 1]
                
                # Calcular fecha (separar 1 día por partido)
                fecha_partido = fecha_base + timedelta(days=partidos_creados)
                fecha_partido = fecha_partido.replace(hour=9, minute=0, second=0)
                fecha_str = fecha_partido.strftime("%Y-%m-%d %H:%M:%S")
                
                # Insertar partido
                MatchModel.insertar_partido(
                    eliminatoria="Jornada 1",
                    fecha_hora=fecha_str,
                    local_id=local['id'],
                    visitante_id=visitante['id'],
                    estado='Programado',
                    arbitro_id=None
                )
                partidos_creados += 1
            
            # Recargar tabla
            self.cargar_tabla()
            
            # Refrescar calendario
            self.vista.calendario_partidos.refresh_calendar_marks()
            
            QMessageBox.information(
                self.vista,
                "Éxito",
                f"Se generaron {partidos_creados} partidos correctamente.\n\n"
                f"Puede editarlos desde la pestaña Datos."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al generar partidos: {str(e)}"
            )
