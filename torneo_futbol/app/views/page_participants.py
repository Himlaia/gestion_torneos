"""Página de gestión de participantes."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QSplitter,
    QGroupBox, QHeaderView, QComboBox, QCheckBox, QDateEdit,
    QSpinBox, QTabWidget, QFrame
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from typing import Optional


def formatear_fecha_display(fecha_str: str) -> str:
    if not fecha_str:
        return ""
    fecha_str = str(fecha_str).strip()
    if not fecha_str:
        return ""
    
    if " " in fecha_str:
        fecha_str = fecha_str.split(" ")[0]
    
    fecha = QDate.fromString(fecha_str, "yyyy-MM-dd")
    if fecha.isValid():
        return fecha.toString("dd/MM/yyyy")
    
    fecha = QDate.fromString(fecha_str, "dd/MM/yyyy")
    if fecha.isValid():
        return fecha.toString("dd/MM/yyyy")
    
    return fecha_str


class PageGestionParticipantes(QWidget):
    """Página para la gestión de participantes."""
    
    # Señales personalizadas
    nuevo_participante_signal = Signal()
    editar_participante_signal = Signal()
    eliminar_participante_signal = Signal()
    guardar_participante_signal = Signal()
    cancelar_edicion_signal = Signal()
    buscar_participante_changed_signal = Signal(str)
    filtros_changed_signal = Signal(dict)
    participante_seleccionado_signal = Signal(dict)
    guardar_equipo_signal = Signal()
    quitar_equipo_signal = Signal()
    
    # Umbral de ancho para activar modo compacto (en píxeles)
    UMBRAL_COMPACTO = 1050
    
    def __init__(self):
        """Inicializa la página de participantes."""
        super().__init__()
        self.modo_actual = "ver"
        self.participante_seleccionado_id = None
        self._splitter_initialized = False
        self.splitter = None
        self._modo_compacto_activo = False
        self._layout_grid_barra = None
        self._widget_botones = None
        self.setup_ui()
        self.conectar_senales()
        self.aplicar_validaciones_iniciales()
        
        # Aplicar tamaños del splitter después de que el layout esté listo
        QTimer.singleShot(0, self._apply_splitter_sizes)
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Establecer objectName para el widget raíz
        self.setObjectName("pageRoot")
        
        # Establecer ancho mínimo para evitar layouts rotos
        self.setMinimumWidth(800)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(12)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Cabecera
        self.crear_cabecera(layout_principal)
        
        # Contenedor de contenido (card)
        content_card = QFrame()
        content_card.setObjectName("contentCard")
        content_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        # Barra de filtros y botones de acción
        self.crear_barra_filtros(card_layout)
        
        # Zona central con splitter
        self.crear_zona_central(card_layout)
        
        layout_principal.addWidget(content_card)
        
        self.setLayout(layout_principal)
    
    def _apply_splitter_sizes(self):
        """Aplica los tamaños iniciales al splitter (80% tabla, 20% panel detalle)."""
        if self._splitter_initialized or self.splitter is None:
            return
        
        ancho_total = self.splitter.width()
        
        # Si el ancho aún no está calculado, reintentar una vez después de 50ms
        if ancho_total <= 100:
            if not hasattr(self, '_splitter_retry_attempted'):
                self._splitter_retry_attempted = True
                QTimer.singleShot(50, self._apply_splitter_sizes)
            return
        
        # Establecer proporción inicial: 80% tabla, 20% panel detalle
        left = int(ancho_total * 0.80)
        right = ancho_total - left
        self.splitter.setSizes([left, right])
        self._splitter_initialized = True
    
    def crear_cabecera(self, layout_padre: QVBoxLayout):
        """Crea la cabecera con el título."""
        titulo = QLabel("Gestión de participantes")
        titulo.setObjectName("titleLabel")
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_padre.addWidget(titulo)
    
    def crear_barra_filtros(self, layout_padre: QVBoxLayout):
        """Crea la barra de filtros, búsqueda y botones de acción con layout responsive."""
        from PySide6.QtWidgets import QSizePolicy, QGridLayout
        
        # Contenedor con GridLayout para permitir dos filas
        widget_barra = QWidget()
        self._layout_grid_barra = QGridLayout(widget_barra)
        self._layout_grid_barra.setContentsMargins(0, 0, 0, 10)
        self._layout_grid_barra.setSpacing(8)
        
        # Configurar proporciones de columnas
        self._layout_grid_barra.setColumnStretch(0, 2)  # Búsqueda
        self._layout_grid_barra.setColumnStretch(1, 1)  # Rol
        self._layout_grid_barra.setColumnStretch(2, 1)  # Equipo
        self._layout_grid_barra.setColumnStretch(3, 1)  # Curso
        self._layout_grid_barra.setColumnStretch(4, 0)  # Botones sin stretch
        
        # === FILA 0: Búsqueda y filtros ===
        # Campo de búsqueda
        self.buscar_participante = QLineEdit()
        self.buscar_participante.setPlaceholderText("Buscar por nombre…")
        self.buscar_participante.setMinimumWidth(150)
        self.buscar_participante.setMaximumWidth(300)
        self._layout_grid_barra.addWidget(self.buscar_participante, 0, 0)
        
        # Filtro Rol
        widget_rol = QWidget()
        layout_rol = QHBoxLayout(widget_rol)
        layout_rol.setContentsMargins(0, 0, 0, 0)
        layout_rol.setSpacing(4)
        layout_rol.addWidget(QLabel("Rol:"))
        self.filtro_rol = QComboBox()
        self.filtro_rol.addItems(["Todos", "Jugadores", "Árbitros", "Ambos"])
        self.filtro_rol.setMinimumWidth(90)
        self.filtro_rol.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout_rol.addWidget(self.filtro_rol)
        self._layout_grid_barra.addWidget(widget_rol, 0, 1)
        
        # Filtro Equipo
        widget_equipo = QWidget()
        layout_equipo = QHBoxLayout(widget_equipo)
        layout_equipo.setContentsMargins(0, 0, 0, 0)
        layout_equipo.setSpacing(4)
        layout_equipo.addWidget(QLabel("Equipo:"))
        self.filtro_equipo = QComboBox()
        self.filtro_equipo.addItem("Todos")
        self.filtro_equipo.setMinimumWidth(100)
        self.filtro_equipo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout_equipo.addWidget(self.filtro_equipo)
        self._layout_grid_barra.addWidget(widget_equipo, 0, 2)
        
        # Filtro Curso
        widget_curso = QWidget()
        layout_curso = QHBoxLayout(widget_curso)
        layout_curso.setContentsMargins(0, 0, 0, 0)
        layout_curso.setSpacing(4)
        layout_curso.addWidget(QLabel("Curso:"))
        self.filtro_curso = QComboBox()
        self.filtro_curso.addItems(["Todos", "1º ESO", "2º ESO", "3º ESO", "4º ESO"])
        self.filtro_curso.setMinimumWidth(80)
        self.filtro_curso.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout_curso.addWidget(self.filtro_curso)
        self._layout_grid_barra.addWidget(widget_curso, 0, 3)
        
        # === BOTONES (inicialmente en fila 0, columna 4) ===
        self._widget_botones = QWidget()
        layout_botones = QHBoxLayout(self._widget_botones)
        layout_botones.setContentsMargins(0, 0, 0, 0)
        layout_botones.setSpacing(6)
        
        self.nuevo_participante = QPushButton("Nuevo")
        self.nuevo_participante.setMinimumWidth(65)
        self.nuevo_participante.setMaximumWidth(80)
        self.nuevo_participante.setToolTip("Nuevo participante")
        layout_botones.addWidget(self.nuevo_participante)
        
        self.editar_participante = QPushButton("Editar")
        self.editar_participante.setMinimumWidth(65)
        self.editar_participante.setMaximumWidth(80)
        self.editar_participante.setToolTip("Editar participante seleccionado")
        layout_botones.addWidget(self.editar_participante)
        
        self.eliminar_participante = QPushButton("Eliminar")
        self.eliminar_participante.setObjectName("dangerButton")
        self.eliminar_participante.setMinimumWidth(65)
        self.eliminar_participante.setMaximumWidth(85)
        self.eliminar_participante.setToolTip("Eliminar participante seleccionado")
        layout_botones.addWidget(self.eliminar_participante)
        
        self._widget_botones.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Añadir botones en fila 0, columna 4 inicialmente (modo ancho)
        self._layout_grid_barra.addWidget(self._widget_botones, 0, 4, Qt.AlignmentFlag.AlignRight)
        
        layout_padre.addWidget(widget_barra)
    
    def resizeEvent(self, event):
        """Maneja el cambio de tamaño para mover botones a segunda fila si es necesario."""
        super().resizeEvent(event)
        
        if not hasattr(self, '_layout_grid_barra') or not hasattr(self, '_widget_botones'):
            return
        
        ancho_actual = self.width()
        # Umbral más alto para asegurar que no se solapen
        necesita_segunda_fila = ancho_actual < 1100
        
        # Verificar posición actual de los botones
        index = self._layout_grid_barra.indexOf(self._widget_botones)
        if index == -1:
            return
        
        try:
            row, col, rowspan, colspan = self._layout_grid_barra.getItemPosition(index)
            
            # Si necesita estar en fila 1 pero está en fila 0, mover
            if necesita_segunda_fila and row == 0:
                self._layout_grid_barra.removeWidget(self._widget_botones)
                self._layout_grid_barra.addWidget(self._widget_botones, 1, 0, 1, 5, Qt.AlignmentFlag.AlignRight)
            # Si necesita estar en fila 0 pero está en fila 1, mover
            elif not necesita_segunda_fila and row == 1:
                self._layout_grid_barra.removeWidget(self._widget_botones)
                self._layout_grid_barra.addWidget(self._widget_botones, 0, 4, Qt.AlignmentFlag.AlignRight)
        except:
            # Si hay algún error, no hacer nada
            pass
    
    def crear_zona_central(self, layout_padre: QVBoxLayout):
        """Crea la zona central con splitter (tabla + detalle)."""
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Ocultar el handle del splitter para eliminar barra visible
        self.splitter.setHandleWidth(0)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background: transparent;
                width: 0px;
            }
        """)
        
        # Panel izquierdo: tabla de participantes
        self.crear_panel_tabla(self.splitter)
        
        # Panel derecho: detalle del participante
        self.crear_panel_detalle(self.splitter)
        
        # Configurar proporciones del splitter para que la tabla tenga más peso
        self.splitter.setStretchFactor(0, 4)  # Tabla izquierda: mayor peso
        self.splitter.setStretchFactor(1, 1)  # Panel derecho: menor peso
        
        # Evitar colapso completo de los paneles
        self.splitter.setCollapsible(0, False)  # Tabla no colapsable
        self.splitter.setCollapsible(1, False)  # Detalle no colapsable
        
        layout_padre.addWidget(self.splitter, 1)
    
    def crear_panel_tabla(self, splitter: QSplitter):
        """Crea el panel con la tabla de participantes."""
        widget_tabla = QWidget()
        widget_tabla.setMinimumWidth(350)
        from PySide6.QtWidgets import QSizePolicy
        widget_tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_tabla = QVBoxLayout()
        layout_tabla.setContentsMargins(0, 0, 10, 0)
        
        # Tabla de participantes
        self.tabla_participantes = QTableWidget()
        self.tabla_participantes.setColumnCount(9)
        self.tabla_participantes.setHorizontalHeaderLabels([
            "Nombre", "Nacimiento", "Curso", "Rol", "Equipo",
            "Posición", "Goles", "Amarillas", "Rojas"
        ])
        
        # Configurar tabla
        self.tabla_participantes.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_participantes.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.tabla_participantes.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        
        # Estirar columnas
        header = self.tabla_participantes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setMinimumSectionSize(80)  # Ancho mínimo para evitar cortar "Nombre"
        for i in range(1, 9):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        layout_tabla.addWidget(self.tabla_participantes)
        widget_tabla.setLayout(layout_tabla)
        splitter.addWidget(widget_tabla)
    
    def crear_panel_detalle(self, splitter: QSplitter):
        """Crea el panel de detalle con tabs."""
        self.grupo_detalle = QGroupBox("Detalle del participante")
        self.grupo_detalle.setMinimumWidth(400)
        from PySide6.QtWidgets import QSizePolicy
        self.grupo_detalle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_detalle = QVBoxLayout()
        
        # Tabs
        self.tabs_detalle = QTabWidget()
        
        # Tab 1: Datos
        self.crear_tab_datos()
        
        # Tab 2: Estadísticas
        self.crear_tab_estadisticas()
        
        # Tab 3: Asignaciones
        self.crear_tab_asignaciones()
        
        layout_detalle.addWidget(self.tabs_detalle)
        
        # Botones de acción del formulario (Guardar/Cancelar)
        layout_botones_detalle = QHBoxLayout()
        layout_botones_detalle.setSpacing(10)
        
        self.guardar_participante = QPushButton("Guardar")
        self.guardar_participante.setObjectName("successButton")
        self.cancelar_edicion = QPushButton("Cancelar")
        
        layout_botones_detalle.addStretch()
        layout_botones_detalle.addWidget(self.guardar_participante)
        layout_botones_detalle.addWidget(self.cancelar_edicion)
        
        layout_detalle.addLayout(layout_botones_detalle)
        
        self.grupo_detalle.setLayout(layout_detalle)
        splitter.addWidget(self.grupo_detalle)
    
    def crear_tab_datos(self):
        """Crea el tab de datos personales."""
        tab_datos = QWidget()
        layout_datos = QVBoxLayout()
        layout_datos.setSpacing(10)
        
        # Nombre completo
        layout_nombre = QVBoxLayout()
        layout_nombre.setSpacing(5)
        layout_nombre.addWidget(QLabel("Nombre completo:"))
        self.nombre_completo = QLineEdit()
        self.nombre_completo.setPlaceholderText("Nombre y apellidos del participante")
        layout_nombre.addWidget(self.nombre_completo)
        layout_datos.addLayout(layout_nombre)
        
        # Fecha de nacimiento
        layout_fecha = QVBoxLayout()
        layout_fecha.setSpacing(5)
        layout_fecha.addWidget(QLabel("Fecha de nacimiento:"))
        self.fecha_nacimiento = QDateEdit()
        self.fecha_nacimiento.setCalendarPopup(True)
        self.fecha_nacimiento.setDisplayFormat("dd/MM/yyyy")
        self.fecha_nacimiento.setDate(QDate(2010, 1, 1))
        layout_fecha.addWidget(self.fecha_nacimiento)
        layout_datos.addLayout(layout_fecha)
        
        # Curso
        layout_curso = QVBoxLayout()
        layout_curso.setSpacing(5)
        layout_curso.addWidget(QLabel("Curso:"))
        self.curso = QComboBox()
        self.curso.addItems(["1º ESO", "2º ESO", "3º ESO", "4º ESO"])
        layout_curso.addWidget(self.curso)
        layout_datos.addLayout(layout_curso)
        
        # Checkboxes de rol
        layout_rol = QVBoxLayout()
        layout_rol.setSpacing(5)
        layout_rol.addWidget(QLabel("Roles:"))
        layout_checkboxes = QHBoxLayout()
        layout_checkboxes.setSpacing(20)
        self.es_jugador = QCheckBox("Es jugador")
        self.es_arbitro = QCheckBox("Es árbitro")
        layout_checkboxes.addWidget(self.es_jugador)
        layout_checkboxes.addWidget(self.es_arbitro)
        layout_checkboxes.addStretch()
        layout_rol.addLayout(layout_checkboxes)
        layout_datos.addLayout(layout_rol)
        
        # Equipo asignado (solo si es jugador)
        layout_equipo = QVBoxLayout()
        layout_equipo.setSpacing(5)
        layout_equipo.addWidget(QLabel("Equipo asignado:"))
        self.equipo_asignado = QComboBox()
        self.equipo_asignado.addItem("Sin equipo")
        layout_equipo.addWidget(self.equipo_asignado)
        layout_datos.addLayout(layout_equipo)
        
        # Posición (solo si es jugador)
        layout_posicion = QVBoxLayout()
        layout_posicion.setSpacing(5)
        layout_posicion.addWidget(QLabel("Posición:"))
        self.posicion = QComboBox()
        self.posicion.addItems([
            "Sin definir", "Portero", "Defensa",
            "Centrocampista", "Delantero"
        ])
        layout_posicion.addWidget(self.posicion)
        layout_datos.addLayout(layout_posicion)
        
        layout_datos.addStretch()
        tab_datos.setLayout(layout_datos)
        self.tabs_detalle.addTab(tab_datos, "Datos")
    
    def crear_tab_estadisticas(self):
        """Crea el tab de estadísticas."""
        tab_stats = QWidget()
        layout_stats = QVBoxLayout()
        layout_stats.setSpacing(15)
        
        # Goles
        layout_goles = QVBoxLayout()
        layout_goles.setSpacing(5)
        layout_goles.addWidget(QLabel("Goles:"))
        self.goles = QSpinBox()
        self.goles.setRange(0, 99)
        self.goles.setValue(0)
        layout_goles.addWidget(self.goles)
        layout_stats.addLayout(layout_goles)
        
        # Tarjetas amarillas
        layout_amarillas = QVBoxLayout()
        layout_amarillas.setSpacing(5)
        layout_amarillas.addWidget(QLabel("Tarjetas amarillas:"))
        self.tarjetas_amarillas = QSpinBox()
        self.tarjetas_amarillas.setRange(0, 99)
        self.tarjetas_amarillas.setValue(0)
        layout_amarillas.addWidget(self.tarjetas_amarillas)
        layout_stats.addLayout(layout_amarillas)
        
        # Tarjetas rojas
        layout_rojas = QVBoxLayout()
        layout_rojas.setSpacing(5)
        layout_rojas.addWidget(QLabel("Tarjetas rojas:"))
        self.tarjetas_rojas = QSpinBox()
        self.tarjetas_rojas.setRange(0, 99)
        self.tarjetas_rojas.setValue(0)
        layout_rojas.addWidget(self.tarjetas_rojas)
        layout_stats.addLayout(layout_rojas)
        
        layout_stats.addStretch()
        tab_stats.setLayout(layout_stats)
        self.tabs_detalle.addTab(tab_stats, "Estadísticas")
    
    def crear_tab_asignaciones(self):
        """Crea el tab de asignaciones."""
        tab_asignaciones = QWidget()
        layout_asignaciones = QVBoxLayout()
        layout_asignaciones.setSpacing(15)
        
        # Grupo Equipo
        grupo_equipo = QGroupBox("Equipo")
        layout_grupo_equipo = QVBoxLayout()
        layout_grupo_equipo.setSpacing(10)
        
        # Label de estado
        self.equipo_actual = QLabel("Equipo actual: Sin equipo")
        self.equipo_actual.setStyleSheet("font-weight: bold;")
        layout_grupo_equipo.addWidget(self.equipo_actual)
        
        # ComboBox para seleccionar equipo
        label_combo = QLabel("Seleccionar equipo:")
        layout_grupo_equipo.addWidget(label_combo)
        self.comboEquipo = QComboBox()
        self.comboEquipo.addItem("-- Selecciona equipo --", None)
        layout_grupo_equipo.addWidget(self.comboEquipo)
        
        # Botones de acción
        layout_botones_equipo = QHBoxLayout()
        self.btnGuardarEquipo = QPushButton("Guardar asignación")
        self.btnGuardarEquipo.setObjectName("successButton")
        self.btnQuitarEquipo = QPushButton("Quitar equipo")
        layout_botones_equipo.addWidget(self.btnGuardarEquipo)
        layout_botones_equipo.addWidget(self.btnQuitarEquipo)
        layout_grupo_equipo.addLayout(layout_botones_equipo)
        
        grupo_equipo.setLayout(layout_grupo_equipo)
        layout_asignaciones.addWidget(grupo_equipo)
        
        # Grupo Árbitro
        grupo_arbitro = QGroupBox("Partidos arbitrados")
        layout_grupo_arbitro = QVBoxLayout()
        
        self.partidos_arbitrados = QTableWidget()
        self.partidos_arbitrados.setColumnCount(4)
        self.partidos_arbitrados.setHorizontalHeaderLabels([
            "Ronda", "Fecha", "Local", "Visitante"
        ])
        self.partidos_arbitrados.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.partidos_arbitrados.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        
        header_arbitro = self.partidos_arbitrados.horizontalHeader()
        header_arbitro.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_arbitro.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_arbitro.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header_arbitro.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        layout_grupo_arbitro.addWidget(self.partidos_arbitrados)
        
        # Mensaje informativo en lugar de botones
        self.label_info_arbitros = QLabel("La asignación de árbitros se gestiona desde la sección Partidos.")
        self.label_info_arbitros.setStyleSheet("font-size: 11px; color: #666; opacity: 0.8;")
        self.label_info_arbitros.setWordWrap(True)
        layout_grupo_arbitro.addWidget(self.label_info_arbitros)
        
        grupo_arbitro.setLayout(layout_grupo_arbitro)
        layout_asignaciones.addWidget(grupo_arbitro)
        
        layout_asignaciones.addStretch()
        tab_asignaciones.setLayout(layout_asignaciones)
        self.tabs_detalle.addTab(tab_asignaciones, "Asignaciones")
    
    def conectar_senales(self):
        """Conecta las señales de los widgets."""
        # Botones de acción
        self.nuevo_participante.clicked.connect(self.nuevo_participante_signal.emit)
        self.editar_participante.clicked.connect(self.editar_participante_signal.emit)
        self.eliminar_participante.clicked.connect(self.eliminar_participante_signal.emit)
        self.guardar_participante.clicked.connect(self.guardar_participante_signal.emit)
        self.cancelar_edicion.clicked.connect(self.cancelar_edicion_signal.emit)
        
        # Botones de asignación de equipo
        self.btnGuardarEquipo.clicked.connect(self.guardar_equipo_signal.emit)
        self.btnQuitarEquipo.clicked.connect(self.quitar_equipo_signal.emit)
        
        # Conexión para actualizar estado de botones cuando cambia el combo
        self.comboEquipo.currentIndexChanged.connect(self.on_combo_equipo_changed)
        
        # Búsqueda
        self.buscar_participante.textChanged.connect(
            self.buscar_participante_changed_signal.emit
        )
        
        # Filtros
        self.filtro_rol.currentTextChanged.connect(self.on_filtros_changed)
        self.filtro_equipo.currentTextChanged.connect(self.on_filtros_changed)
        self.filtro_curso.currentTextChanged.connect(self.on_filtros_changed)
        
        # Selección en tabla
        self.tabla_participantes.itemSelectionChanged.connect(
            self.on_seleccion_tabla_changed
        )
        
        # Checkboxes de rol
        self.es_jugador.stateChanged.connect(self.on_es_jugador_changed)
        self.es_arbitro.stateChanged.connect(self.on_es_arbitro_changed)
    
    def aplicar_validaciones_iniciales(self):
        """Aplica las validaciones iniciales de la interfaz."""
        # Por defecto, campos de jugador deshabilitados
        self.equipo_asignado.setEnabled(False)
        self.posicion.setEnabled(False)
        self.comboEquipo.setEnabled(False)
        self.btnGuardarEquipo.setEnabled(False)
        self.btnQuitarEquipo.setEnabled(False)
        
        # Por defecto, campos de árbitro deshabilitados
        self.partidos_arbitrados.setEnabled(False)
    
    def on_filtros_changed(self):
        """Maneja el cambio en los filtros."""
        filtros = {
            'rol': self.filtro_rol.currentText(),
            'equipo': self.filtro_equipo.currentText(),
            'curso': self.filtro_curso.currentText()
        }
        self.filtros_changed_signal.emit(filtros)
    
    def on_seleccion_tabla_changed(self):
        """Maneja el cambio de selección en la tabla."""
        fila_seleccionada = self.tabla_participantes.currentRow()
        if fila_seleccionada >= 0:
            item_nombre = self.tabla_participantes.item(fila_seleccionada, 0)
            if item_nombre:
                self.participante_seleccionado_id = item_nombre.data(Qt.ItemDataRole.UserRole)
            datos = self.obtener_datos_fila(fila_seleccionada)
            self.participante_seleccionado_signal.emit(datos)
        else:
            self.participante_seleccionado_id = None
    
    def on_es_jugador_changed(self, state: int):
        """Maneja el cambio en el checkbox es_jugador."""
        es_jugador = (state == Qt.CheckState.Checked.value)
        
        # Habilitar/deshabilitar campos de jugador
        self.equipo_asignado.setEnabled(es_jugador and self.modo_actual != "ver")
        self.posicion.setEnabled(es_jugador and self.modo_actual != "ver")
        
        # Actualizar UI del tab de asignaciones
        if self.participante_seleccionado_id:
            self.refresh_equipo_ui(self.participante_seleccionado_id)
        
        # Si se desmarca, limpiar campos
        if not es_jugador:
            self.equipo_asignado.setCurrentIndex(0)
            self.posicion.setCurrentIndex(0)
            self.equipo_actual.setText("Equipo actual: Sin equipo")
    
    def on_es_arbitro_changed(self, state: int):
        """Maneja el cambio en el checkbox es_arbitro."""
        es_arbitro = (state == Qt.CheckState.Checked.value)
        
        # Habilitar/deshabilitar campos de árbitro
        self.partidos_arbitrados.setEnabled(es_arbitro)
        
        # Si se desmarca, limpiar tabla
        if not es_arbitro:
            self.partidos_arbitrados.setRowCount(0)
    
    def obtener_datos_fila(self, fila: int) -> dict:
        """Obtiene los datos de una fila de la tabla."""
        datos = {}
        if fila >= 0 and fila < self.tabla_participantes.rowCount():
            # Obtener ID desde UserRole
            item_nombre = self.tabla_participantes.item(fila, 0)
            if item_nombre:
                datos['id'] = item_nombre.data(Qt.ItemDataRole.UserRole)
            
            datos['nombre'] = self.tabla_participantes.item(fila, 0).text()
            fecha_display = self.tabla_participantes.item(fila, 1).text()
            fecha_qdate = QDate.fromString(fecha_display, "dd/MM/yyyy")
            if not fecha_qdate.isValid():
                fecha_qdate = QDate.fromString(fecha_display, "yyyy-MM-dd")
            datos['fecha_nacimiento'] = fecha_qdate.toString("yyyy-MM-dd") if fecha_qdate.isValid() else fecha_display
            datos['curso'] = self.tabla_participantes.item(fila, 2).text()
            datos['tipo_jugador'] = self.tabla_participantes.item(fila, 3).text()
            datos['equipo_nombre'] = self.tabla_participantes.item(fila, 4).text()
            datos['posicion'] = self.tabla_participantes.item(fila, 5).text()
            datos['goles'] = int(self.tabla_participantes.item(fila, 6).text())
            datos['t_amarillas'] = int(self.tabla_participantes.item(fila, 7).text())
            datos['t_rojas'] = int(self.tabla_participantes.item(fila, 8).text())
        return datos
    
    # ========== Métodos públicos obligatorios ==========
    
    def set_filas_tabla(self, participantes: list[dict]):
        """Establece las filas de la tabla con los datos de participantes."""
        self.tabla_participantes.setRowCount(0)
        
        for participante in participantes:
            fila = self.tabla_participantes.rowCount()
            self.tabla_participantes.insertRow(fila)
            
            self.tabla_participantes.setItem(
                fila, 0, QTableWidgetItem(str(participante.get('nombre', '')))
            )
            self.tabla_participantes.setItem(
                fila, 1, QTableWidgetItem(str(participante.get('nacimiento', '')))
            )
            self.tabla_participantes.setItem(
                fila, 2, QTableWidgetItem(str(participante.get('curso', '')))
            )
            self.tabla_participantes.setItem(
                fila, 3, QTableWidgetItem(str(participante.get('rol', '')))
            )
            self.tabla_participantes.setItem(
                fila, 4, QTableWidgetItem(str(participante.get('equipo', '')))
            )
            self.tabla_participantes.setItem(
                fila, 5, QTableWidgetItem(str(participante.get('posicion', '')))
            )
            self.tabla_participantes.setItem(
                fila, 6, QTableWidgetItem(str(participante.get('goles', '0')))
            )
            self.tabla_participantes.setItem(
                fila, 7, QTableWidgetItem(str(participante.get('amarillas', '0')))
            )
            self.tabla_participantes.setItem(
                fila, 8, QTableWidgetItem(str(participante.get('rojas', '0')))
            )
    
    def set_lista_equipos(self, equipos: list[str]):
        """Establece la lista de equipos en los combos."""
        # Actualizar filtro de equipos
        self.filtro_equipo.clear()
        self.filtro_equipo.addItem("Todos")
        self.filtro_equipo.addItems(equipos)
        
        # Actualizar combo de equipo asignado
        self.equipo_asignado.clear()
        self.equipo_asignado.addItem("Sin equipo")
        self.equipo_asignado.addItems(equipos)
    
    def cargar_combo_equipos_filtro(self, equipos: list[str]):
        """Carga la lista de equipos en el combo de filtro."""
        self.filtro_equipo.clear()
        self.filtro_equipo.addItems(equipos)
    
    def cargar_combo_equipos_asignacion(self, equipos: list[str]):
        """Carga la lista de equipos en el combo de asignación."""
        self.equipo_asignado.clear()
        self.equipo_asignado.addItems(equipos)
    
    def cargar_combo_cursos(self, cursos: list[str]):
        """Carga la lista de cursos en el combo de filtro."""
        self.filtro_curso.clear()
        self.filtro_curso.addItems(cursos)
    
    def load_equipos_into_combo(self, equipos_dict: dict):
        """
        Carga los equipos en el comboEquipo del tab de asignaciones.
        
        Args:
            equipos_dict: Diccionario con {nombre_equipo: id_equipo}
        """
        self.comboEquipo.clear()
        self.comboEquipo.addItem("-- Selecciona equipo --", None)
        
        for nombre, equipo_id in equipos_dict.items():
            self.comboEquipo.addItem(nombre, equipo_id)
    
    def refresh_equipo_ui(self, participante_id: Optional[int] = None):
        """
        Actualiza la UI del grupo Equipo en el tab Asignaciones.
        Actualiza el label de estado, la selección del combo y el estado de los botones.
        """
        # Obtener datos actuales del formulario
        datos = self.get_datos_formulario()
        equipo_nombre = datos.get('equipo_nombre', 'Sin equipo')
        es_jugador = datos.get('es_jugador', False)
        
        # Actualizar label de estado
        if equipo_nombre and equipo_nombre != 'Sin equipo':
            self.equipo_actual.setText(f"Equipo actual: {equipo_nombre}")
        else:
            self.equipo_actual.setText("Equipo actual: Sin equipo")
        
        # Preseleccionar equipo en combo si tiene uno asignado
        if equipo_nombre and equipo_nombre != 'Sin equipo':
            # Buscar y seleccionar el equipo en el combo
            for i in range(self.comboEquipo.count()):
                if self.comboEquipo.itemText(i) == equipo_nombre:
                    self.comboEquipo.setCurrentIndex(i)
                    break
        else:
            # Sin equipo: poner en primera opción
            self.comboEquipo.setCurrentIndex(0)
        
        # Actualizar estado de botones
        self._update_equipo_buttons_state()
    
    def on_combo_equipo_changed(self, index: int):
        """Maneja el cambio en el comboEquipo para actualizar botones."""
        self._update_equipo_buttons_state()
    
    def _update_equipo_buttons_state(self):
        """Actualiza el estado habilitado/deshabilitado de los botones de equipo."""
        # Obtener equipo actual y seleccionado
        datos = self.get_datos_formulario()
        equipo_actual = datos.get('equipo_nombre', 'Sin equipo')
        es_jugador = datos.get('es_jugador', False)
        
        equipo_seleccionado_id = self.comboEquipo.currentData()
        equipo_seleccionado_nombre = self.comboEquipo.currentText()
        
        tiene_equipo = (equipo_actual and equipo_actual != 'Sin equipo')
        
        # Habilitar comboEquipo solo si es jugador
        self.comboEquipo.setEnabled(es_jugador)
        
        # btnQuitarEquipo: habilitado solo si tiene equipo asignado
        self.btnQuitarEquipo.setEnabled(tiene_equipo and es_jugador)
        
        # btnGuardarEquipo: habilitado solo si:
        # - Es jugador
        # - Hay un equipo válido seleccionado en el combo (no "-- Selecciona equipo --")
        # - El equipo seleccionado es diferente al actual
        equipo_valido_seleccionado = (equipo_seleccionado_id is not None)
        equipo_diferente = (equipo_seleccionado_nombre != equipo_actual)
        
        self.btnGuardarEquipo.setEnabled(
            es_jugador and equipo_valido_seleccionado and equipo_diferente
        )
    
    def obtener_filtros_actuales(self) -> dict:
        """Obtiene los valores actuales de los filtros."""
        return {
            'busqueda': self.buscar_participante.text().strip(),
            'rol': self.filtro_rol.currentText(),
            'equipo': self.filtro_equipo.currentText(),
            'curso': self.filtro_curso.currentText()
        }
    
    def set_datos_formulario(self, datos: dict):
        """Establece los datos en el formulario de detalle."""
        nombre = datos.get('nombre', '')
        apellidos = datos.get('apellidos', '')
        nombre_completo = f"{nombre} {apellidos}".strip()
        self.nombre_completo.setText(nombre_completo)
        
        # Fecha de nacimiento
        fecha_str = datos.get('fecha_nacimiento', '')
        if fecha_str:
            try:
                fecha = QDate.fromString(fecha_str, "dd/MM/yyyy")
                if fecha.isValid():
                    self.fecha_nacimiento.setDate(fecha)
            except:
                pass
        
        # Curso
        curso = datos.get('curso', '')
        if curso:
            index = self.curso.findText(curso)
            if index >= 0:
                self.curso.setCurrentIndex(index)
        
        # Roles
        self.es_jugador.setChecked(datos.get('es_jugador', False))
        self.es_arbitro.setChecked(datos.get('es_arbitro', False))
        
        # Equipo y posición
        equipo = datos.get('equipo', 'Sin equipo')
        index_equipo = self.equipo_asignado.findText(equipo)
        if index_equipo >= 0:
            self.equipo_asignado.setCurrentIndex(index_equipo)
        
        posicion = datos.get('posicion', 'Sin definir')
        index_posicion = self.posicion.findText(posicion)
        if index_posicion >= 0:
            self.posicion.setCurrentIndex(index_posicion)
        
        # Actualizar label de equipo actual
        equipo_mostrar = equipo if equipo and equipo != 'Sin equipo' else 'Sin equipo'
        self.equipo_actual.setText(f"Equipo actual: {equipo_mostrar}")
        
        # Actualizar UI del tab Asignaciones
        self.refresh_equipo_ui()
        
        # Estadísticas
        self.goles.setValue(int(datos.get('goles', 0)))
        self.tarjetas_amarillas.setValue(int(datos.get('amarillas', 0)))
        self.tarjetas_rojas.setValue(int(datos.get('rojas', 0)))
    
    def get_datos_formulario(self) -> dict:
        """Obtiene los datos del formulario de detalle."""
        nombre_completo = self.nombre_completo.text().strip()
        partes = nombre_completo.rsplit(' ', 1)
        nombre = partes[0] if len(partes) > 0 else ''
        apellidos = partes[1] if len(partes) > 1 else ''
        
        return {
            'nombre': nombre,
            'apellidos': apellidos,
            'fecha_nacimiento': self.fecha_nacimiento.date().toString("yyyy-MM-dd"),
            'curso': self.curso.currentText(),
            'es_jugador': self.es_jugador.isChecked(),
            'es_arbitro': self.es_arbitro.isChecked(),
            'equipo_nombre': self.equipo_asignado.currentText(),
            'equipo_asignado_texto': self.equipo_asignado.currentText(),
            'equipo_asignado_indice': self.equipo_asignado.currentIndex(),
            'posicion': self.posicion.currentText(),
            't_amarillas': self.tarjetas_amarillas.value(),
            't_rojas': self.tarjetas_rojas.value(),
            'goles': self.goles.value()
        }
    
    def obtener_datos_formulario(self) -> dict:
        """Alias de get_datos_formulario para compatibilidad."""
        return self.get_datos_formulario()
    
    def actualizar_tabla(self, participantes: list[dict]):
        """Actualiza la tabla con la lista de participantes."""
        self.tabla_participantes.setRowCount(0)
        
        for participante in participantes:
            fila = self.tabla_participantes.rowCount()
            self.tabla_participantes.insertRow(fila)
            
            # Guardar ID en la fila (oculto)
            nombre_completo = f"{participante.get('nombre', '')} {participante.get('apellidos', '')}".strip()
            item_nombre = QTableWidgetItem(nombre_completo)
            item_nombre.setData(Qt.ItemDataRole.UserRole, participante.get('id'))
            self.tabla_participantes.setItem(fila, 0, item_nombre)
            
            fecha_nac = participante.get('fecha_nacimiento', '')
            fecha_formateada = formatear_fecha_display(fecha_nac)
            self.tabla_participantes.setItem(fila, 1, QTableWidgetItem(fecha_formateada))
            
            # Curso
            self.tabla_participantes.setItem(fila, 2, QTableWidgetItem(participante.get('curso', '')))
            
            # Rol (tipo_jugador)
            self.tabla_participantes.setItem(fila, 3, QTableWidgetItem(participante.get('tipo_jugador', '')))
            
            # Equipo
            equipo_nombre = participante.get('equipo_nombre') or 'Sin equipo'
            self.tabla_participantes.setItem(fila, 4, QTableWidgetItem(equipo_nombre))
            
            # Posición
            self.tabla_participantes.setItem(fila, 5, QTableWidgetItem(participante.get('posicion', '')))
            
            # Estadísticas
            self.tabla_participantes.setItem(fila, 6, QTableWidgetItem(str(participante.get('goles', 0))))
            self.tabla_participantes.setItem(fila, 7, QTableWidgetItem(str(participante.get('t_amarillas', 0))))
            self.tabla_participantes.setItem(fila, 8, QTableWidgetItem(str(participante.get('t_rojas', 0))))
    
    def rellenar_formulario(self, datos: dict, modo: str = "ver"):
        """Rellena el formulario con los datos proporcionados y establece el modo."""
        nombre = datos.get('nombre', '')
        apellidos = datos.get('apellidos', '')
        nombre_completo = f"{nombre} {apellidos}".strip()
        self.nombre_completo.setText(nombre_completo)
        
        fecha_str = datos.get('fecha_nacimiento', '')
        if fecha_str:
            try:
                if " " in fecha_str:
                    fecha_str = fecha_str.split(" ")[0]
                fecha = QDate.fromString(fecha_str, "yyyy-MM-dd")
                if not fecha.isValid():
                    fecha = QDate.fromString(fecha_str, "dd/MM/yyyy")
                if fecha.isValid():
                    self.fecha_nacimiento.setDate(fecha)
            except:
                pass
        
        curso = datos.get('curso', '')
        if curso:
            index = self.curso.findText(curso)
            if index >= 0:
                self.curso.setCurrentIndex(index)
        
        self.es_jugador.setChecked(datos.get('es_jugador', False))
        self.es_arbitro.setChecked(datos.get('es_arbitro', False))
        
        equipo_nombre = datos.get('equipo_nombre', 'Sin equipo')
        index_equipo = self.equipo_asignado.findText(equipo_nombre)
        if index_equipo >= 0:
            self.equipo_asignado.setCurrentIndex(index_equipo)
        else:
            self.equipo_asignado.setCurrentIndex(0)
        
        equipo_mostrar = equipo_nombre if equipo_nombre and equipo_nombre != 'Sin equipo' else 'Sin equipo'
        self.equipo_actual.setText(f"Equipo actual: {equipo_mostrar}")
        
        posicion = datos.get('posicion', 'Sin definir')
        index_posicion = self.posicion.findText(posicion)
        if index_posicion >= 0:
            self.posicion.setCurrentIndex(index_posicion)
        
        self.goles.setValue(int(datos.get('goles', 0)))
        self.tarjetas_amarillas.setValue(int(datos.get('t_amarillas', 0)))
        self.tarjetas_rojas.setValue(int(datos.get('t_rojas', 0)))
        
        # Actualizar UI del tab Asignaciones
        self.refresh_equipo_ui()
        
        self.set_modo(modo)
    
    def cambiar_modo_formulario(self, modo: str):
        """Cambia el modo del formulario sin modificar los datos."""
        self.set_modo(modo)
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.nombre_completo.clear()
        self.fecha_nacimiento.setDate(QDate(2010, 1, 1))
        self.curso.setCurrentIndex(0)
        self.es_jugador.setChecked(False)
        self.es_arbitro.setChecked(False)
        self.equipo_asignado.setCurrentIndex(0)
        self.posicion.setCurrentIndex(0)
        self.goles.setValue(0)
        self.tarjetas_amarillas.setValue(0)
        self.tarjetas_rojas.setValue(0)
        self.equipo_actual.setText("Equipo actual: Sin equipo")
        self.comboEquipo.setCurrentIndex(0)
        self.partidos_arbitrados.setRowCount(0)
        self.tabla_participantes.clearSelection()
        self.participante_seleccionado_id = None
    
    def set_modo(self, modo: str):
        """Establece el modo de operación del formulario."""
        self.modo_actual = modo
        
        if modo == "ver":
            # Modo lectura
            self.nombre_completo.setReadOnly(True)
            self.fecha_nacimiento.setEnabled(False)
            self.curso.setEnabled(False)
            self.es_jugador.setEnabled(False)
            self.es_arbitro.setEnabled(False)
            self.equipo_asignado.setEnabled(False)
            self.posicion.setEnabled(False)
            self.goles.setEnabled(False)
            self.tarjetas_amarillas.setEnabled(False)
            self.tarjetas_rojas.setEnabled(False)
            
            # Deshabilitar combo y botones de equipo en modo ver
            self.comboEquipo.setEnabled(False)
            self.btnGuardarEquipo.setEnabled(False)
            self.btnQuitarEquipo.setEnabled(False)
            
            # Habilitar botones de acción
            self.nuevo_participante.setEnabled(True)
            self.editar_participante.setEnabled(True)
            self.eliminar_participante.setEnabled(True)
            self.guardar_participante.setEnabled(False)
            self.cancelar_edicion.setEnabled(False)
            
        elif modo in ["crear", "editar"]:
            # Modo edición
            self.nombre_completo.setReadOnly(False)
            self.fecha_nacimiento.setEnabled(True)
            self.curso.setEnabled(True)
            self.es_jugador.setEnabled(True)
            self.es_arbitro.setEnabled(True)
            self.goles.setEnabled(True)
            self.tarjetas_amarillas.setEnabled(True)
            self.tarjetas_rojas.setEnabled(True)
            
            # Habilitar campos según checkboxes
            es_jugador = self.es_jugador.isChecked()
            es_arbitro = self.es_arbitro.isChecked()
            
            self.equipo_asignado.setEnabled(es_jugador)
            self.posicion.setEnabled(es_jugador)
            
            # Actualizar estado de botones de equipo
            self._update_equipo_buttons_state()
            
            # Deshabilitar botones de acción
            self.nuevo_participante.setEnabled(False)
            self.editar_participante.setEnabled(False)
            self.eliminar_participante.setEnabled(False)
            self.guardar_participante.setEnabled(True)
            self.cancelar_edicion.setEnabled(True)
    
    def set_partidos_arbitrados(self, partidos: list[dict]):
        """Llena la tabla de partidos arbitrados."""
        self.partidos_arbitrados.setRowCount(0)
        
        for partido in partidos:
            fila = self.partidos_arbitrados.rowCount()
            self.partidos_arbitrados.insertRow(fila)
            
            self.partidos_arbitrados.setItem(
                fila, 0, QTableWidgetItem(str(partido.get('ronda', '')))
            )
            self.partidos_arbitrados.setItem(
                fila, 1, QTableWidgetItem(str(partido.get('fecha', '')))
            )
            self.partidos_arbitrados.setItem(
                fila, 2, QTableWidgetItem(str(partido.get('local', '')))
            )
            self.partidos_arbitrados.setItem(
                fila, 3, QTableWidgetItem(str(partido.get('visitante', '')))
            )


# Alias para mantener compatibilidad con código existente
PageParticipants = PageGestionParticipantes
