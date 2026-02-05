"""Controlador para la gestión de equipos."""
import shutil
from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtCore import QObject

from app.views.page_teams import PageGestionEquipos
from app.views.dialogs.dialog_jugadores_equipo import DialogJugadoresEquipo
from app.models.team_model import TeamModel
from app.models.participant_model import ParticipantModel
from app.models.db import DbError
from app.services.event_bus import get_event_bus
from app.config import DATA_DIR


class ControladorGestionEquipos(QObject):
    """Controlador para conectar la vista de equipos con el modelo."""
    
    def __init__(self, vista: PageGestionEquipos):
        """
        Inicializa el controlador.
        
        Args:
            vista: Instancia de PageGestionEquipos
        """
        super().__init__()
        self.vista = vista
        self.equipo_actual_id = None
        self.escudo_temporal = None
        
        # Obtener event bus
        self.event_bus = get_event_bus()
        
        # Conectar señales de la vista
        self.conectar_senales()
        
        # Cargar datos iniciales
        self.cargar_tabla()
        
        # Establecer modo inicial
        self.vista.set_modo("ver")
    
    def conectar_senales(self):
        """Conecta las señales de la vista con los slots del controlador."""
        self.vista.nuevo_equipo_signal.connect(self._on_nuevo)
        self.vista.editar_equipo_signal.connect(self._on_editar)
        self.vista.eliminar_equipo_signal.connect(self._on_eliminar)
        self.vista.guardar_equipo_signal.connect(self._on_guardar)
        self.vista.cancelar_edicion_signal.connect(self._on_cancelar)
        self.vista.buscar_equipo_changed_signal.connect(self._on_buscar)
        self.vista.equipo_seleccionado_signal.connect(self._on_equipo_seleccionado)
        self.vista.seleccionar_escudo_signal.connect(self._on_seleccionar_escudo)
        self.vista.ver_jugadores_equipo_signal.connect(self._on_ver_jugadores)
    
    def cargar_tabla(self, busqueda: str = None):
        """
        Carga los equipos en la tabla de la vista.
        
        Args:
            busqueda: Texto de búsqueda opcional
        """
        try:
            equipos = TeamModel.listar_equipos(busqueda)
            
            # Preparar datos para la vista
            equipos_vista = []
            for equipo in equipos:
                equipos_vista.append({
                    'id': equipo['id'],
                    'nombre': equipo['nombre'],
                    'colores': equipo['color'],
                    'escudo': equipo['escudo_path'] or 'Sin escudo',
                    'num_jugadores': str(equipo['num_jugadores'])
                })
            
            self.vista.set_filas_tabla(equipos_vista)
            
        except DbError as e:
            QMessageBox.critical(
                self.vista,
                "Error de base de datos",
                f"No se pudieron cargar los equipos:\n{str(e)}"
            )
    
    def _on_buscar(self, texto: str):
        """
        Maneja la búsqueda de equipos.
        
        Args:
            texto: Texto de búsqueda
        """
        busqueda = texto.strip() if texto.strip() else None
        self.cargar_tabla(busqueda)
    
    def _on_nuevo(self):
        """Inicia la creación de un nuevo equipo."""
        self.equipo_actual_id = None
        self.escudo_temporal = None
        # Primero limpiar selección de tabla para evitar confusión
        self.vista.tabla_equipos.clearSelection()
        # Luego limpiar formulario
        self.vista.limpiar_formulario()
        self.vista.set_modo("crear")
    
    def _on_editar(self):
        """Inicia la edición del equipo seleccionado."""
        if self.equipo_actual_id is None:
            QMessageBox.warning(
                self.vista,
                "Seleccionar equipo",
                "Debe seleccionar un equipo de la tabla para editarlo."
            )
            return
        
        self.vista.set_modo("editar")
    
    def _on_eliminar(self):
        """Elimina el equipo seleccionado."""
        if self.equipo_actual_id is None:
            QMessageBox.warning(
                self.vista,
                "Seleccionar equipo",
                "Debe seleccionar un equipo de la tabla para eliminarlo."
            )
            return
        
        # Confirmar eliminación
        respuesta = QMessageBox.question(
            self.vista,
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar este equipo?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                team_id_to_delete = self.equipo_actual_id
                TeamModel.eliminar_equipo(team_id_to_delete)
                
                # Emitir evento de equipo eliminado
                self.event_bus.emit_team_deleted(team_id_to_delete)
                
                QMessageBox.information(
                    self.vista,
                    "Equipo eliminado",
                    "El equipo ha sido eliminado correctamente."
                )
                
                self.equipo_actual_id = None
                self.vista.limpiar_formulario()
                self.cargar_tabla()
                
            except DbError as e:
                QMessageBox.critical(
                    self.vista,
                    "Error al eliminar",
                    f"No se pudo eliminar el equipo:\n{str(e)}"
                )
    
    def _on_guardar(self):
        """Guarda el equipo (nuevo o editado)."""
        # Obtener datos del formulario
        datos = self.vista.get_datos_formulario()
        nombre = datos['nombre'].strip()
        colores = datos['colores'].strip()
        
        # Validar campos obligatorios
        if not nombre:
            QMessageBox.warning(
                self.vista,
                "Datos incompletos",
                "El nombre del equipo es obligatorio."
            )
            return
        
        if not colores:
            QMessageBox.warning(
                self.vista,
                "Datos incompletos",
                "Los colores del equipo son obligatorios."
            )
            return
        
        # Usar escudo temporal si se seleccionó uno nuevo
        escudo_path = self.escudo_temporal if self.escudo_temporal else datos.get('escudo', '')
        if escudo_path == 'Sin escudo':
            escudo_path = None
        
        try:
            if self.equipo_actual_id is None:
                # Crear nuevo equipo
                # Por ahora curso es fijo, podría añadirse al formulario
                equipo_id = TeamModel.crear_equipo(
                    nombre=nombre,
                    curso="1º ESO",  # Valor por defecto
                    color=colores,
                    escudo_path=escudo_path
                )
                
                # Emitir evento de equipo creado
                self.event_bus.emit_team_created(equipo_id)
                
                QMessageBox.information(
                    self.vista,
                    "Equipo creado",
                    f"El equipo '{nombre}' ha sido creado correctamente."
                )
                
                self.equipo_actual_id = equipo_id
            else:
                # Actualizar equipo existente
                # Obtener curso actual del equipo
                equipo_actual = TeamModel.obtener_equipo_por_id(self.equipo_actual_id)
                curso_actual = equipo_actual['curso'] if equipo_actual else "1º ESO"
                
                TeamModel.actualizar_equipo(
                    equipo_id=self.equipo_actual_id,
                    nombre=nombre,
                    curso=curso_actual,
                    color=colores,
                    escudo_path=escudo_path
                )
                
                # Emitir evento de equipo actualizado
                self.event_bus.emit_team_updated(self.equipo_actual_id)
                
                QMessageBox.information(
                    self.vista,
                    "Equipo actualizado",
                    f"El equipo '{nombre}' ha sido actualizado correctamente."
                )
            
            # Recargar tabla y volver a modo ver
            self.escudo_temporal = None
            self.cargar_tabla()
            self.vista.set_modo("ver")
            
            # Recargar el equipo en el formulario
            if self.equipo_actual_id:
                self._cargar_equipo_en_formulario(self.equipo_actual_id)
            
        except ValueError as e:
            # Error de validación (nombre duplicado)
            QMessageBox.warning(
                self.vista,
                "Nombre duplicado",
                str(e)
            )
        except DbError as e:
            QMessageBox.critical(
                self.vista,
                "Error al guardar",
                f"No se pudo guardar el equipo:\n{str(e)}"
            )
    
    def _on_cancelar(self):
        """Cancela la creación o edición del equipo."""
        self.escudo_temporal = None
        
        if self.equipo_actual_id is not None:
            # Si había un equipo seleccionado, recargar sus datos
            self._cargar_equipo_en_formulario(self.equipo_actual_id)
        else:
            # Si no había selección, limpiar formulario
            self.vista.limpiar_formulario()
        
        self.vista.set_modo("ver")
    
    def _on_equipo_seleccionado(self, datos: dict):
        """
        Maneja la selección de un equipo en la tabla.
        
        Args:
            datos: Datos del equipo seleccionado
        """
        # Buscar el ID del equipo por nombre
        try:
            equipos = TeamModel.listar_equipos()
            equipo_encontrado = None
            
            for equipo in equipos:
                if equipo['nombre'] == datos.get('nombre'):
                    equipo_encontrado = equipo
                    break
            
            if equipo_encontrado:
                self.equipo_actual_id = equipo_encontrado['id']
                self._cargar_equipo_en_formulario(self.equipo_actual_id)
                self.vista.set_modo("ver")
            
        except DbError as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"No se pudo cargar el equipo:\n{str(e)}"
            )
    
    def _cargar_equipo_en_formulario(self, equipo_id: int):
        """
        Carga los datos de un equipo en el formulario.
        
        Args:
            equipo_id: ID del equipo a cargar
        """
        try:
            equipo = TeamModel.obtener_equipo_por_id(equipo_id)
            
            if equipo:
                self.vista.set_datos_formulario({
                    'nombre': equipo['nombre'],
                    'colores': equipo['color'],
                    'escudo': equipo['escudo_path'] or 'Sin escudo'
                })
        except DbError as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"No se pudo cargar el equipo:\n{str(e)}"
            )
    
    def _on_seleccionar_escudo(self):
        """Abre un diálogo para seleccionar una imagen de escudo."""
        # Abrir diálogo de archivo
        archivo, _ = QFileDialog.getOpenFileName(
            self.vista,
            "Seleccionar escudo del equipo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.svg)"
        )
        
        if archivo:
            try:
                # Crear directorio de escudos si no existe
                dir_escudos = DATA_DIR / "escudos"
                dir_escudos.mkdir(parents=True, exist_ok=True)
                
                # Generar nombre único para el escudo
                archivo_original = Path(archivo)
                extension = archivo_original.suffix
                nombre_base = archivo_original.stem
                
                # Usar timestamp para evitar colisiones
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_nuevo = f"{nombre_base}_{timestamp}{extension}"
                
                ruta_destino = dir_escudos / nombre_nuevo
                
                # Copiar archivo
                shutil.copy2(archivo, ruta_destino)
                
                # Guardar ruta relativa desde DATA_DIR
                self.escudo_temporal = str(ruta_destino.relative_to(DATA_DIR.parent))
                
                # Actualizar preview en la vista (cargar imagen)
                self.vista.cargar_escudo(self.escudo_temporal)
                
                QMessageBox.information(
                    self.vista,
                    "Escudo seleccionado",
                    f"Escudo '{nombre_nuevo}' seleccionado correctamente.\n\n"
                    "Recuerde guardar los cambios del equipo."
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self.vista,
                    "Error al copiar escudo",
                    f"No se pudo copiar el archivo del escudo:\n{str(e)}"
                )    
    def _on_ver_jugadores(self, id_equipo: int, nombre_equipo: str):
        """
        Muestra un diálogo con los jugadores del equipo.
        
        Args:
            id_equipo: ID del equipo
            nombre_equipo: Nombre del equipo
        """
        try:
            # Obtener jugadores del equipo
            jugadores = ParticipantModel.listar_jugadores_por_equipo(id_equipo)
            
            # Mostrar diálogo
            dialogo = DialogJugadoresEquipo(nombre_equipo, jugadores, self.vista)
            dialogo.exec()
            
        except DbError as e:
            QMessageBox.critical(
                self.vista,
                "Error",
                f"Error al cargar los jugadores del equipo:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.vista,
                "Error inesperado",
                f"Error al mostrar jugadores:\n{str(e)}"
            )