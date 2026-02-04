"""
Controlador para el cuadro de eliminatorias.
"""
from PySide6.QtWidgets import QMessageBox
from app.models.team_model import TeamModel
from app.models.match_model import MatchModel
from app.services.tournament_service import TournamentService
from app.services.event_bus import EventBus


class ControladorCuadroEliminatorias:
    """Controlador para conectar la vista del cuadro con los modelos y servicios."""
    
    def __init__(self, vista):
        """
        Inicializa el controlador y conecta las señales de la vista.
        
        Args:
            vista: Instancia de PageCuadroEliminatorias
        """
        self.vista = vista
        self.matches_controller = None  # Referencia al controlador de partidos
        
        # Obtener instancia del Event Bus
        self.event_bus = EventBus.get_instance()
        
        # Conectar señales
        self._conectar_senales()
        self._conectar_event_bus()
        
        # Cargar datos iniciales
        self.cargar_equipos()
        self.cargar_cuadro()
    
    def set_matches_controller(self, matches_controller):
        """
        Establece la referencia al controlador de partidos.
        
        Args:
            matches_controller: Instancia de ControladorCalendarioPartidos
        """
        self.matches_controller = matches_controller
    
    def _conectar_senales(self):
        """Conecta todas las señales de la vista con los métodos del controlador."""
        print("[BRACKET CONTROLLER] Conectando señales...")
        
        # Conectar señal de randomización (puede tener diferentes nombres según la vista)
        try:
            if hasattr(self.vista, 'randomizar_octavos_signal'):
                print("[BRACKET CONTROLLER] Conectando randomizar_octavos_signal...")
                self.vista.randomizar_octavos_signal.connect(self._on_randomizar)
                print("[BRACKET CONTROLLER] ✅ randomizar_octavos_signal conectada")
            elif hasattr(self.vista, 'randomizar_emparejamientos_signal'):
                print("[BRACKET CONTROLLER] Conectando randomizar_emparejamientos_signal...")
                self.vista.randomizar_emparejamientos_signal.connect(self._on_randomizar)
                print("[BRACKET CONTROLLER] ✅ randomizar_emparejamientos_signal conectada")
            elif hasattr(self.vista, 'reiniciar_emparejamientos_signal'):
                print("[BRACKET CONTROLLER] Conectando reiniciar_emparejamientos_signal...")
                self.vista.reiniciar_emparejamientos_signal.connect(self._on_randomizar)
                print("[BRACKET CONTROLLER] ✅ reiniciar_emparejamientos_signal conectada")
            else:
                print("[BRACKET CONTROLLER] ⚠️ NO se encontró señal de randomización")
        except Exception as e:
            print(f"[BRACKET CONTROLLER] ❌ Error conectando randomizar: {e}")
        
        try:
            if hasattr(self.vista, 'guardar_emparejamientos_signal'):
                self.vista.guardar_emparejamientos_signal.connect(self._on_guardar_emparejamientos)
        except Exception as e:
            print(f"[BRACKET CONTROLLER] Error conectando guardar: {e}")
        
        try:
            if hasattr(self.vista, 'reiniciar_cuadro_signal'):
                self.vista.reiniciar_cuadro_signal.connect(self._on_reiniciar)
        except Exception as e:
            print(f"[BRACKET CONTROLLER] Error conectando reiniciar: {e}")
    
    def _conectar_event_bus(self):
        """Conecta el Event Bus para escuchar cambios externos."""
        # Escuchar cambios en equipos
        self.event_bus.team_created.connect(self._on_team_changed_external)
        self.event_bus.team_updated.connect(self._on_team_changed_external)
        self.event_bus.team_deleted.connect(self._on_team_changed_external)
        
        # Escuchar cambios en partidos y resultados
        self.event_bus.match_created.connect(self._on_match_changed_external)
        self.event_bus.match_updated.connect(self._on_match_changed_external)
        self.event_bus.result_saved.connect(self._on_result_saved_external)
        self.event_bus.bracket_updated.connect(self._on_bracket_updated_external)
    
    def cargar_equipos(self):
        """Carga la lista de equipos en los combos de emparejamientos."""
        equipos = TeamModel.listar_equipos()
        
        # Crear lista de nombres para los combos
        lista_equipos = [eq["nombre"] for eq in equipos]
        
        # Guardar diccionario para conversión nombre -> id
        self.equipos_dict = {eq["nombre"]: eq["id"] for eq in equipos}
        self.equipos_list = equipos
        
        # La vista ya carga los equipos en su setup_ui() llamando a su propio
        # método cargar_equipos_en_combos() sin parámetros. No necesitamos duplicar.
        # self.vista.cargar_equipos_en_combos(lista_equipos)  # REMOVIDO
    
    def cargar_cuadro(self):
        """Carga el cuadro de eliminatorias desde la base de datos."""
        from app.constants import FASE_OCTAVOS, FASE_CUARTOS, FASE_SEMIFINAL, FASE_FINAL, FASES_CONFIG
        
        # Obtener todos los partidos
        todos_partidos = MatchModel.listar_partidos()
        
        if not todos_partidos:
            # No hay partidos, modo configurable
            self.vista.set_modo("configurable")
            self.vista.limpiar_cuadro()
            return
        
        # Hay partidos, modo solo lectura
        self.vista.set_modo("solo_lectura")
        
        # Organizar partidos por ronda (usar minúsculas de la BD)
        # Normalizar nombres de fase para búsqueda case-insensitive
        cuadro_data = {
            "Octavos": [],
            "Cuartos": [],
            "Semifinal": [],
            "Final": []
        }
        
        for partido in todos_partidos:
            eliminatoria = partido.get("eliminatoria", "").lower()  # Normalizar a minúsculas
            # Mapear minúsculas a etiquetas con mayúsculas para la vista
            if eliminatoria == FASE_OCTAVOS:
                cuadro_data["Octavos"].append(partido)
            elif eliminatoria == FASE_CUARTOS:
                cuadro_data["Cuartos"].append(partido)
            elif eliminatoria == FASE_SEMIFINAL:
                cuadro_data["Semifinal"].append(partido)
            elif eliminatoria == FASE_FINAL:
                cuadro_data["Final"].append(partido)
        
        # Ordenar cada ronda por slot
        for ronda in cuadro_data:
            cuadro_data[ronda].sort(key=lambda p: p.get("slot", 0))
        
        # Enviar a la vista
        self.vista.set_cuadro(cuadro_data)
    
    def _on_randomizar(self):
        """Maneja la acción de randomizar emparejamientos con persistencia en BD."""
        print("\n" + "="*60)
        print("[BRACKET CONTROLLER] _on_randomizar INICIADO")
        print("="*60)
        
        # 1. Verificar que haya al menos 16 equipos
        print(f"[DEBUG] Equipos disponibles: {len(self.equipos_list)}")
        if len(self.equipos_list) < 16:
            QMessageBox.warning(
                self.vista,
                "Equipos insuficientes",
                f"Se requieren 16 equipos para generar octavos de final.\n"
                f"Actualmente hay {len(self.equipos_list)} equipos."
            )
            return
        
        # 2. Verificar si ya existen octavos
        print("[DEBUG] Verificando si ya existen octavos...")
        if TournamentService.octavos_already_exist():
            print("[DEBUG] ⚠️ Ya existen octavos, preguntando si desea regenerar...")
            respuesta_overwrite = QMessageBox.question(
                self.vista,
                "Octavos ya existentes",
                "Los octavos ya están creados.\n\n"
                "Si continúas, se eliminarán los partidos de octavos existentes "
                "(incluidos convocatorias y resultados) y se generarán nuevos emparejamientos aleatorios.\n\n"
                "⚠️ Esta acción NO se puede deshacer.\n\n"
                "¿Deseas regenerar los octavos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if respuesta_overwrite != QMessageBox.StandardButton.Yes:
                print("[DEBUG] Usuario canceló la regeneración")
                return
            print("[DEBUG] ✅ Usuario aceptó regenerar octavos")
        else:
            print("[DEBUG] ✅ No existen octavos, se puede continuar")
        
        # 3. Confirmación antes de crear
        print("[DEBUG] Solicitando confirmación al usuario...")
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar randomización",
            "Se generarán los 8 partidos de octavos con emparejamientos aleatorios "
            "y fechas automáticas.\n\n"
            "Los partidos aparecerán en Calendario/Partidos.\n\n"
            "¿Deseas continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            print("[DEBUG] Usuario canceló la operación")
            return
        print("[DEBUG] Usuario confirmó, continuando...")
        
        try:
            # 4. Obtener IDs de los primeros 16 equipos
            equipos_ids = [eq["id"] for eq in self.equipos_list[:16]]
            print(f"[DEBUG] IDs de equipos seleccionados: {equipos_ids}")
            
            # 5. Randomizar Y crear partidos en BD con fechas automáticas
            print("[DEBUG] Llamando a TournamentService.randomize_and_create_octavos...")
            TournamentService.randomize_and_create_octavos(equipos_ids)
            print("[DEBUG] ✅ randomize_and_create_octavos completado")
            
            # 6. VERIFICACIÓN POST-CREACIÓN
            from app.constants import FASE_OCTAVOS
            print("\n[DEBUG] === VERIFICACIÓN POST-CREACIÓN ===")
            partidos_creados = MatchModel.listar_partidos(eliminatoria=FASE_OCTAVOS)
            print(f"[DEBUG] Partidos 'Octavos' en BD: {len(partidos_creados)}")
            
            if len(partidos_creados) != 8:
                print(f"[ERROR] ❌ FALLO: Se esperaban 8 partidos pero hay {len(partidos_creados)}")
                QMessageBox.critical(
                    self.vista,
                    "Error de verificación",
                    f"Se generó el bracket pero no se registraron correctamente los partidos.\n\n"
                    f"Se esperaban 8 partidos de octavos pero se encontraron {len(partidos_creados)}.\n\n"
                    f"Revisa inserciones en BD y filtros del calendario."
                )
                return
            
            print("[DEBUG] ✅ Verificación exitosa: 8 partidos en BD")
            
            # Verificar que el calendario puede verlos
            print("\n[DEBUG] Verificando query del calendario...")
            todos_partidos = MatchModel.listar_partidos()
            print(f"[DEBUG] Total de partidos (sin filtros): {len(todos_partidos)}")
            
            partidos_programados = MatchModel.listar_partidos(estado="Programado")
            print(f"[DEBUG] Partidos con estado='Programado': {len(partidos_programados)}")
            
            # 7. Recargar cuadro para mostrar los partidos creados
            print("\n[DEBUG] Recargando cuadro...")
            self.cargar_cuadro()
            print("[DEBUG] ✅ Cuadro recargado")
            
            # 8. Notificar éxito
            mensaje_exito = (
                f"Los 8 partidos de octavos han sido creados correctamente.\n\n"
                f"✓ Partidos en BD: {len(partidos_creados)}\n"
                f"✓ Partidos programados: {len(partidos_programados)}\n\n"
                f"Puedes verlos en la pestaña Calendario/Partidos."
            )
            print(f"[DEBUG] Mostrando mensaje de éxito: {mensaje_exito}")
            QMessageBox.information(
                self.vista,
                "Octavos generados",
                mensaje_exito
            )
            
            print("\n" + "="*60)
            print("[BRACKET CONTROLLER] _on_randomizar COMPLETADO EXITOSAMENTE")
            print("="*60 + "\n")
            
        except ValueError as e:
            print(f"[ERROR] ValueError: {e}")
            QMessageBox.warning(
                self.vista,
                "Error",
                f"Error al randomizar: {str(e)}"
            )
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception inesperada: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error inesperado al crear octavos:\n\n{str(e)}"
            )
    
    def _on_guardar_emparejamientos(self):
        """Maneja la acción de guardar los emparejamientos configurados."""
        # Obtener emparejamientos de la vista
        emparejamientos_vista = self.vista.obtener_emparejamientos()
        
        if not emparejamientos_vista:
            QMessageBox.warning(
                self.vista,
                "Error",
                "No se pudieron obtener los emparejamientos de la vista."
            )
            return
        
        # Validar que hay exactamente 8 emparejamientos
        if len(emparejamientos_vista) != 8:
            QMessageBox.warning(
                self.vista,
                "Validación",
                f"Se requieren 8 emparejamientos para octavos.\n"
                f"Se obtuvieron {len(emparejamientos_vista)}."
            )
            return
        
        # Validar y convertir a IDs
        emparejamientos_ids = []
        equipos_usados = set()
        
        for i, emp in enumerate(emparejamientos_vista, start=1):
            local_nombre = emp.get("local", "").strip()
            visitante_nombre = emp.get("visitante", "").strip()
            
            # Validar que no estén vacíos
            if not local_nombre or not visitante_nombre:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    f"El emparejamiento {i} tiene equipos vacíos.\n"
                    f"Por favor, seleccione equipos válidos."
                )
                return
            
            # Validar que no sea el mismo equipo
            if local_nombre == visitante_nombre:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    f"El emparejamiento {i} tiene el mismo equipo como local y visitante.\n"
                    f"Equipo: {local_nombre}"
                )
                return
            
            # Obtener IDs
            local_id = self.equipos_dict.get(local_nombre)
            visitante_id = self.equipos_dict.get(visitante_nombre)
            
            if not local_id or not visitante_id:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    f"El emparejamiento {i} tiene equipos inválidos."
                )
                return
            
            # Validar que no se repitan equipos
            if local_id in equipos_usados:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    f"El equipo '{local_nombre}' está repetido en los emparejamientos."
                )
                return
            if visitante_id in equipos_usados:
                QMessageBox.warning(
                    self.vista,
                    "Validación",
                    f"El equipo '{visitante_nombre}' está repetido en los emparejamientos."
                )
                return
            
            equipos_usados.add(local_id)
            equipos_usados.add(visitante_id)
            
            emparejamientos_ids.append({
                "local_id": local_id,
                "visitante_id": visitante_id
            })
        
        # Validar que se usen exactamente 16 equipos
        if len(equipos_usados) != 16:
            QMessageBox.warning(
                self.vista,
                "Validación",
                f"Se requieren 16 equipos únicos para octavos.\n"
                f"Se encontraron {len(equipos_usados)} equipos."
            )
            return
        
        # Confirmación
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar",
            "¿Está seguro de que desea guardar estos emparejamientos?\n"
            "Esta acción generará el cuadro de octavos de final.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Generar octavos
            TournamentService.generar_octavos_desde_emparejamientos(emparejamientos_ids)
            
            # Recargar cuadro
            self.cargar_cuadro()
            
            QMessageBox.information(
                self.vista,
                "Éxito",
                "Los emparejamientos de octavos se han guardado correctamente."
            )
            
        except ValueError as e:
            QMessageBox.warning(
                self.vista,
                "Error",
                f"Error al guardar emparejamientos: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error inesperado: {str(e)}"
            )
    
    def _on_reiniciar(self):
        """Maneja la acción de reiniciar el cuadro de eliminatorias."""
        # Confirmación
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar reinicio",
            "¿Está seguro de que desea reiniciar el cuadro?\n\n"
            "ADVERTENCIA: Se eliminarán todos los partidos y resultados del torneo.\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Resetear cuadro
            TournamentService.resetear_cuadro()
            
            # Recargar cuadro
            self.cargar_cuadro()
            
            QMessageBox.information(
                self.vista,
                "Éxito",
                "El cuadro ha sido reiniciado correctamente."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al reiniciar cuadro: {str(e)}"
            )
    
    # ==================== LISTENERS DEL EVENT BUS ====================
    
    def _on_team_changed_external(self, team_id: int):
        """
        Escucha cambios en equipos desde otros módulos.
        Recarga los equipos disponibles en combos.
        """
        print(f"[BracketController] Cambio en equipo {team_id}, recargando equipos...")
        self.cargar_equipos()
    
    def _on_match_changed_external(self, match_id: int):
        """
        Escucha cambios en partidos desde otros módulos.
        Recarga el cuadro si es necesario.
        """
        print(f"[BracketController] Cambio en partido {match_id}, recargando cuadro...")
        self.cargar_cuadro()
    
    def _on_result_saved_external(self, match_id: int):
        """
        Escucha cuando se guarda un resultado desde otros módulos.
        Recarga el cuadro para mostrar la propagación del ganador.
        """
        print(f"\n{'='*60}")
        print(f"[BRACKET_CONTROLLER] ✓ Evento result_saved recibido")
        print(f"[BRACKET_CONTROLLER] Partido ID: {match_id}")
        print(f"[BRACKET_CONTROLLER] Recargando cuadro...")
        print(f"{'='*60}\n")
        self.cargar_cuadro()
        print(f"[BRACKET_CONTROLLER] ✓ Cuadro recargado\n")
    
    def _on_bracket_updated_external(self):
        """
        Escucha cuando el cuadro completo ha sido actualizado.
        Recarga toda la vista del cuadro.
        """
        print("[BracketController] Bracket actualizado externamente, recargando...")
        self.cargar_cuadro()

