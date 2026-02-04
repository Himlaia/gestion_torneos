"""Página de calendario y partidos."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QSplitter,
    QGroupBox, QHeaderView, QComboBox, QDateTimeEdit,
    QSpinBox, QTabWidget, QMessageBox, QFrame, QGridLayout,
    QSizePolicy, QCompleter, QListWidget, QListWidgetItem, QDialog
)
from PySide6.QtCore import Qt, Signal, QDateTime, QDate, QTimer, QEvent, QObject
from typing import Optional
from app.views.widgets.widget_calendario_partidos import CalendarioPartidos
from app.views.dialogs.dialog_partidos_dia import DialogPartidosDia
import traceback


class ButtonDebugEventFilter(QObject):
    """EventFilter para debug de eventos de botones."""
    
    def __init__(self, button_name: str):
        super().__init__()
        self.button_name = button_name
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Captura eventos de mouse para debug."""
        if event.type() == QEvent.Type.MouseButtonPress:
            print(f"[EVENT FILTER] {self.button_name} - MouseButtonPress detectado")
        elif event.type() == QEvent.Type.MouseButtonRelease:
            print(f"[EVENT FILTER] {self.button_name} - MouseButtonRelease detectado")
        return False  # No consumir el evento


class PageCalendarioPartidos(QWidget):
    """Página para el calendario y gestión de partidos."""
    
    # Señales personalizadas
    filtros_changed_signal = Signal(dict)
    partido_seleccionado_signal = Signal(dict)
    guardar_resultado_signal = Signal()
    cancelar_cambios_signal = Signal()
    abrir_partido_desde_dialogo_signal = Signal(int)
    
    # Señales de acciones principales
    nuevo_partido_signal = Signal()
    reiniciar_torneo_signal = Signal()
    
    # Señales de edición de partido
    guardar_partido_signal = Signal()
    eliminar_partido_signal = Signal()
    cancelar_partido_signal = Signal()
    
    # Señales de convocatoria
    anadir_convocado_local_signal = Signal()
    quitar_convocado_local_signal = Signal()
    anadir_convocado_visitante_signal = Signal()
    quitar_convocado_visitante_signal = Signal()
    convocatoria_changed_signal = Signal(dict)  # {accion, participante_id, equipo_id}
    
    # Señal de cambio de fase (para validación)
    fase_changed_signal = Signal(str)  # Emite fase_id
    
    def __init__(self):
        """Inicializa la página de partidos."""
        super().__init__()
        self.modo_actual = "ver"
        self.partidos_cache = []
        self._cargado_inicial = False
        self._splitter_initialized = False
        self.splitter = None
        self.partido_actual_id = None  # Referencia al partido seleccionado
        self.partido_actual = None  # Datos completos del partido
        self._convocatoria_loading = False  # Flag para evitar señales durante carga inicial
        
        # Cache de goles detallados (CRÍTICO: debe inicializarse aquí)
        self.goles_detalle_cache = []
        
        # Dirty state tracking
        self.datos_dirty = False
        self.convocatoria_dirty = False
        self.resultado_dirty = False
        
        self.setup_ui()
        self.conectar_senales()
        self.aplicar_validaciones_iniciales()
        
        # Aplicar tamaños del splitter después de que el layout esté listo
        QTimer.singleShot(0, self._apply_splitter_sizes)
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Establecer objectName para el widget raíz
        self.setObjectName("pageRoot")
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 4, 20, 12)
        layout_principal.setSpacing(8)
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
        
        # Barra superior de filtros y acciones
        self.crear_barra_filtros_acciones(card_layout)
        
        # Zona central con splitter
        self.crear_zona_central(card_layout)
        
        layout_principal.addWidget(content_card)
        
        self.setLayout(layout_principal)
        
        # Debug buttons
        self.debug_buttons()
        
        # 🔴 AUDIT: Instalar probe slots directos
        self.install_probe_slots()
        
        # 🔴 AUDIT: Instalar eventFilters
        self.install_event_filters()
    
    def _apply_splitter_sizes(self):
        """Aplica los tamaños iniciales al splitter (80% calendario, 20% detalle)."""
        if self._splitter_initialized or self.splitter is None:
            return
        
        ancho_total = self.splitter.width()
        
        # Si el ancho aún no está calculado, reintentar una vez después de 50ms
        if ancho_total <= 100:
            if not hasattr(self, '_splitter_retry_attempted'):
                self._splitter_retry_attempted = True
                QTimer.singleShot(50, self._apply_splitter_sizes)
            return
        
        # Establecer proporción inicial: 80% calendario, 20% detalle
        left = int(ancho_total * 0.80)
        right = ancho_total - left
        self.splitter.setSizes([left, right])
        self._splitter_initialized = True
    
    def crear_cabecera(self, layout_padre: QVBoxLayout):
        """Crea la cabecera con el título."""
        titulo = QLabel("Calendario / Partidos")
        titulo.setObjectName("titleLabel")
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_padre.addWidget(titulo)
    
    def crear_barra_filtros_acciones(self, layout_padre: QVBoxLayout):
        """Crea la barra de filtros y botones de acción."""
        layout_barra = QHBoxLayout()
        layout_barra.setSpacing(10)
        
        # === IZQUIERDA: FILTROS ===
        # Filtro por ronda
        layout_barra.addWidget(QLabel("Ronda:"))
        self.filtro_ronda = QComboBox()
        self.filtro_ronda.addItems(["Todos", "Octavos", "Cuartos", "Semifinales", "Final"])
        self.filtro_ronda.setMinimumWidth(120)
        layout_barra.addWidget(self.filtro_ronda)
        
        # Filtro por estado
        layout_barra.addWidget(QLabel("Estado:"))
        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems(["Todos", "Pendientes", "Jugados"])
        self.filtro_estado.setMinimumWidth(120)
        layout_barra.addWidget(self.filtro_estado)
        
        # Espaciador
        layout_barra.addStretch()
        
        # === DERECHA: ACCIONES ===
        # Botón Nuevo partido (primario)
        self.btnNuevoPartidoTop = QPushButton("Nuevo partido")
        self.btnNuevoPartidoTop.setObjectName("successButton")
        layout_barra.addWidget(self.btnNuevoPartidoTop)
        
        # Botón Reiniciar torneo (destructivo)
        self.btnReiniciarTorneo = QPushButton("Reiniciar torneo")
        self.btnReiniciarTorneo.setObjectName("dangerButton")
        layout_barra.addWidget(self.btnReiniciarTorneo)
        
        layout_padre.addLayout(layout_barra)
    
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
        
        # Panel izquierdo: tabla de partidos
        self.crear_panel_tabla(self.splitter)
        
        # Panel derecho: detalle del partido
        self.crear_panel_detalle(self.splitter)
        
        # Configurar proporciones del splitter
        self.splitter.setStretchFactor(0, 0)  # Calendario: no se estira
        self.splitter.setStretchFactor(1, 1)  # Detalle: se estira
        self.splitter.setCollapsible(1, False)  # Panel derecho no colapsable
        
        layout_padre.addWidget(self.splitter, 1)  # stretch factor 1 para ocupar espacio restante
    
    def crear_panel_tabla(self, splitter: QSplitter):
        """Crea el panel con el calendario de partidos."""
        widget_calendario = QWidget()
        layout_calendario = QVBoxLayout()
        layout_calendario.setContentsMargins(0, 0, 10, 0)
        
        titulo_calendario = QLabel("Calendario mensual")
        titulo_calendario.setObjectName("subtitleLabel")
        layout_calendario.addWidget(titulo_calendario)
        
        self.calendario_partidos = CalendarioPartidos()
        self.calendario_partidos.setMinimumHeight(400)
        layout_calendario.addWidget(self.calendario_partidos)
        
        info_label = QLabel("💡 Haga clic en un día con partidos para ver detalles")
        info_label.setStyleSheet("color: rgba(128, 128, 128, 0.7); font-size: 9pt;")
        layout_calendario.addWidget(info_label)
        
        widget_calendario.setLayout(layout_calendario)
        splitter.addWidget(widget_calendario)
    
    def crear_panel_detalle(self, splitter: QSplitter):
        """Crea el panel de detalle con tabs y botones fijos en footer."""
        # Contenedor exterior con marco glass pastel
        self.grupo_detalle = QGroupBox("Detalle del partido")
        self.grupo_detalle.setObjectName("glassCard")
        self.grupo_detalle.setMinimumWidth(520)
        self.grupo_detalle.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Layout principal del panel derecho
        layout_panel_derecho = QVBoxLayout()
        layout_panel_derecho.setContentsMargins(0, 0, 0, 0)
        layout_panel_derecho.setSpacing(0)
        
        # Widget de contenido para el scroll (solo tabs, sin botones)
        detalleContent = QWidget()
        detalleContent.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        detalleContent.setStyleSheet("background: transparent;")
        layout_detalle = QVBoxLayout()
        layout_detalle.setContentsMargins(0, 0, 12, 12)  # Padding derecho e inferior
        
        # Tabs
        self.tabs_detalle = QTabWidget()
        
        # Tab 1: Datos (sin botones)
        self.crear_tab_datos()
        
        # Tab 2: Convocatoria
        self.crear_tab_convocatoria()
        
        # Tab 3: Resultado
        self.crear_tab_resultado()
        
        layout_detalle.addWidget(self.tabs_detalle)
        detalleContent.setLayout(layout_detalle)
        
        # Agregar tabs directamente sin scroll (layout compacto)
        layout_panel_derecho.addWidget(self.tabs_detalle, 1)
        
        # Footer con botones (siempre visible, fuera del scroll)
        self.footerButtonsWidget = QWidget()
        self.footerButtonsWidget.setMinimumHeight(64)
        footerLayout = QHBoxLayout()
        footerLayout.setContentsMargins(10, 10, 10, 10)
        footerLayout.setSpacing(10)
        
        # Crear botones de edición (solo una vez, aquí en el footer)
        self.btnGuardar = QPushButton("Guardar")
        self.btnGuardar.setObjectName("successButton")
        self.btnEliminar = QPushButton("Eliminar")
        self.btnEliminar.setObjectName("dangerButton")
        self.btnCancelar = QPushButton("Cancelar")
        
        footerLayout.addStretch()
        footerLayout.addWidget(self.btnGuardar)
        footerLayout.addWidget(self.btnEliminar)
        footerLayout.addWidget(self.btnCancelar)
        
        self.footerButtonsWidget.setLayout(footerLayout)
        layout_panel_derecho.addWidget(self.footerButtonsWidget, 0)
        
        self.grupo_detalle.setLayout(layout_panel_derecho)
        splitter.addWidget(self.grupo_detalle)
    
    def crear_tab_datos(self):
        """Crea el tab de datos del partido (layout compacto sin scroll)."""
        tab_datos = QWidget()
        layout_datos = QVBoxLayout()
        layout_datos.setContentsMargins(18, 22, 18, 16)
        layout_datos.setSpacing(10)
        
        # Título del partido
        self.partido_titulo = QLabel("Seleccione un partido")
        self.partido_titulo.setObjectName("subtitleLabel")
        self.partido_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_datos.addWidget(self.partido_titulo)
        
        # FILA 1: Equipos Local y Visitante (lado a lado)
        layout_equipos = QHBoxLayout()
        layout_equipos.setSpacing(10)
        layout_equipos.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)
        
        # Equipo Local
        container_local = QVBoxLayout()
        container_local.setSpacing(5)
        container_local.addWidget(QLabel("Equipo Local:"))
        self.comboLocal = QComboBox()
        self.comboLocal.setObjectName("ComboAccent")
        self.comboLocal.addItem("-- Seleccionar --", None)
        self.comboLocal.setEditable(False)
        self.comboLocal.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.comboLocal.setMaxVisibleItems(8)
        self.comboLocal.setMinimumHeight(34)
        self.comboLocal.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        container_local.addWidget(self.comboLocal)
        layout_equipos.addLayout(container_local)
        
        # Equipo Visitante
        container_visitante = QVBoxLayout()
        container_visitante.setSpacing(5)
        container_visitante.addWidget(QLabel("Equipo Visitante:"))
        self.comboVisitante = QComboBox()
        self.comboVisitante.setObjectName("ComboAccent")
        self.comboVisitante.addItem("-- Seleccionar --", None)
        self.comboVisitante.setEditable(False)
        self.comboVisitante.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.comboVisitante.setMaxVisibleItems(8)
        self.comboVisitante.setMinimumHeight(34)
        self.comboVisitante.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        container_visitante.addWidget(self.comboVisitante)
        layout_equipos.addLayout(container_visitante)
        
        layout_datos.addLayout(layout_equipos)
        
        # FILA 2: Fase + Estado (lado a lado)
        layout_fase_estado = QHBoxLayout()
        layout_fase_estado.setSpacing(10)
        layout_fase_estado.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)
        
        # Fase
        container_fase = QVBoxLayout()
        container_fase.setSpacing(5)
        container_fase.addWidget(QLabel("Fase:"))
        self.comboFase = QComboBox()
        self.comboFase.setObjectName("ComboAccent")
        self.comboFase.setMaxVisibleItems(6)
        self.comboFase.setMinimumHeight(34)
        self.comboFase.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Importar constantes de fases
        from app.constants import FASES_ORDEN, FASES_CONFIG
        for fase_id in FASES_ORDEN:
            config = FASES_CONFIG[fase_id]
            self.comboFase.addItem(config["label"], fase_id)
        
        # Conectar cambio de fase para validación
        self.comboFase.currentIndexChanged.connect(self._on_fase_changed)
        container_fase.addWidget(self.comboFase)
        layout_fase_estado.addLayout(container_fase)
        
        # Estado
        container_estado = QVBoxLayout()
        container_estado.setSpacing(5)
        container_estado.addWidget(QLabel("Estado:"))
        self.comboEstado = QComboBox()
        self.comboEstado.setMinimumHeight(34)
        self.comboEstado.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.comboEstado.addItems(["Programado", "Jugado", "Cancelado"])
        self.comboEstado.setMaxVisibleItems(6)
        container_estado.addWidget(self.comboEstado)
        layout_fase_estado.addLayout(container_estado)
        
        layout_datos.addLayout(layout_fase_estado)
        
        # FILA 3: Fecha y hora (ancho completo)
        layout_fecha = QVBoxLayout()
        layout_fecha.setSpacing(5)
        layout_fecha.addWidget(QLabel("Fecha y hora:"))
        self.fecha_hora = QDateTimeEdit()
        self.fecha_hora.setCalendarPopup(True)
        self.fecha_hora.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.fecha_hora.setDateTime(QDateTime.currentDateTime())
        self.fecha_hora.setMinimumHeight(34)
        self.fecha_hora.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout_fecha.addWidget(self.fecha_hora)
        layout_datos.addLayout(layout_fecha)
        
        # FILA 4: Árbitro (ancho completo)
        layout_arbitro = QVBoxLayout()
        layout_arbitro.setSpacing(5)
        layout_arbitro.addWidget(QLabel("Árbitro:"))
        self.comboArbitro = QComboBox()
        self.comboArbitro.setObjectName("ComboAccent")
        self.comboArbitro.addItem("Sin árbitro", None)
        self.comboArbitro.setEditable(False)
        self.comboArbitro.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.comboArbitro.setMaxVisibleItems(8)
        self.comboArbitro.setMinimumHeight(34)
        self.comboArbitro.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout_arbitro.addWidget(self.comboArbitro)
        layout_datos.addLayout(layout_arbitro)
        
        layout_datos.addStretch()
        
        tab_datos.setLayout(layout_datos)
        self.tabs_detalle.addTab(tab_datos, "Datos")
    
    def crear_tab_convocatoria(self):
        """Crea el tab de convocatoria (diseño compacto con lista única por equipo)."""
        tab_convocatoria = QWidget()
        layout_convocatoria_principal = QVBoxLayout()
        layout_convocatoria_principal.setContentsMargins(18, 22, 18, 16)
        layout_convocatoria_principal.setSpacing(10)
        
        # Label informativo
        self.label_info_convocatoria = QLabel("Guarda el partido para gestionar convocatoria.")
        self.label_info_convocatoria.setStyleSheet("font-size: 12px; color: #666; padding: 10px;")
        self.label_info_convocatoria.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_info_convocatoria.setWordWrap(True)
        layout_convocatoria_principal.addWidget(self.label_info_convocatoria)
        
        # Layout horizontal para Local y Visitante
        layout_convocatoria = QHBoxLayout()
        layout_convocatoria.setSpacing(15)
        
        # Columna Local
        self.crear_grupo_convocatoria_compacto(layout_convocatoria, "Local", es_local=True)
        
        # Columna Visitante
        self.crear_grupo_convocatoria_compacto(layout_convocatoria, "Visitante", es_local=False)
        
        layout_convocatoria_principal.addLayout(layout_convocatoria)
        tab_convocatoria.setLayout(layout_convocatoria_principal)
        self.tabs_detalle.addTab(tab_convocatoria, "Convocatoria")
    
    def crear_grupo_convocatoria_compacto(self, layout_padre: QHBoxLayout, titulo: str, es_local: bool):
        """Crea un grupo de convocatoria compacto con una sola lista y checkboxes."""
        grupo = QGroupBox(titulo)
        layout_grupo = QVBoxLayout()
        layout_grupo.setSpacing(10)
        
        # Label de equipo
        label_equipo = QLabel("Equipo: -")
        label_equipo.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout_grupo.addWidget(label_equipo)
        
        # Label de contador de convocados
        label_contador = QLabel("Convocados: 0 / 0")
        label_contador.setStyleSheet("font-size: 11px; color: #666;")
        layout_grupo.addWidget(label_contador)
        
        # Lista única con checkboxes
        lista_jugadores = QListWidget()
        lista_jugadores.setMinimumHeight(200)
        lista_jugadores.setMaximumHeight(400)
        lista_jugadores.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_grupo.addWidget(lista_jugadores)
        
        # Label de ayuda
        label_ayuda = QLabel("✓ Marcar para convocar | Doble click para alternar")
        label_ayuda.setStyleSheet("font-size: 10px; color: #888; font-style: italic;")
        label_ayuda.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_grupo.addWidget(label_ayuda)
        
        grupo.setLayout(layout_grupo)
        layout_padre.addWidget(grupo)
        
        # Guardar referencias
        if es_local:
            self.equipo_local_label = label_equipo
            self.jugadores_lista_local = lista_jugadores
            self.contador_local_label = label_contador
            # Conectar doble click para toggle
            lista_jugadores.itemDoubleClicked.connect(
                lambda item: self._toggle_convocado_item(item, es_local=True)
            )
            # Conectar itemChanged para persistir cambios automáticamente
            lista_jugadores.itemChanged.connect(
                lambda item: self._on_checkbox_changed(item, es_local=True)
            )
        else:
            self.equipo_visitante_label = label_equipo
            self.jugadores_lista_visitante = lista_jugadores
            self.contador_visitante_label = label_contador
            # Conectar doble click para toggle
            lista_jugadores.itemDoubleClicked.connect(
                lambda item: self._toggle_convocado_item(item, es_local=False)
            )
            # Conectar itemChanged para persistir cambios automáticamente
            lista_jugadores.itemChanged.connect(
                lambda item: self._on_checkbox_changed(item, es_local=False)
            )
    
    def _toggle_convocado_item(self, item: QListWidgetItem, es_local: bool):
        """Alterna el estado de convocado de un jugador (checkbox)."""
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        
        # Actualizar contador
        self._actualizar_contador_convocados(es_local)
    
    def _on_checkbox_changed(self, item: QListWidgetItem, es_local: bool):
        """Maneja cambios en los checkboxes de convocatoria y persiste en BD."""
        # Ignorar si estamos cargando datos inicialmente
        if self._convocatoria_loading:
            return
        
        # Ignorar si no hay partido seleccionado
        if not self.partido_actual_id or not self.partido_actual:
            return
        
        participante_id = item.data(Qt.ItemDataRole.UserRole)
        if not participante_id:
            return
        
        # Determinar equipo_id según si es local o visitante
        if es_local:
            equipo_id = self.partido_actual.get('local_id')
        else:
            equipo_id = self.partido_actual.get('visitante_id')
        
        if not equipo_id:
            return
        
        # Determinar acción según el estado del checkbox
        accion = 'convocar' if item.checkState() == Qt.CheckState.Checked else 'quitar'
        
        # Emitir señal para que el controlador persista el cambio
        self.convocatoria_changed_signal.emit({
            'accion': accion,
            'participante_id': participante_id,
            'equipo_id': equipo_id
        })
        
        # Actualizar contador
        self._actualizar_contador_convocados(es_local)
    
    def _actualizar_contador_convocados(self, es_local: bool):
        """Actualiza el contador de convocados."""
        if es_local:
            lista = self.jugadores_lista_local
            label = self.contador_local_label
        else:
            lista = self.jugadores_lista_visitante
            label = self.contador_visitante_label
        
        total = lista.count()
        convocados = sum(1 for i in range(total) if lista.item(i).checkState() == Qt.CheckState.Checked)
        label.setText(f"Convocados: {convocados} / {total}")
    
    def crear_grupo_convocatoria_equipo(
        self, layout_padre: QHBoxLayout, titulo: str, es_local: bool
    ):
        """DEPRECATED: Método antiguo mantenido por compatibilidad. Usa crear_grupo_convocatoria_compacto."""
        # Redirigir al nuevo método
        self.crear_grupo_convocatoria_compacto(layout_padre, titulo, es_local)
    
    def crear_tab_resultado(self):
        """Crea el tab de resultado."""
        tab_resultado = QWidget()
        layout_resultado = QVBoxLayout()
        layout_resultado.setSpacing(15)
        layout_resultado.setContentsMargins(10, 10, 10, 10)
        
        # Layout horizontal contenedor para Marcador y Penaltis
        layout_horizontal_scores = QHBoxLayout()
        layout_horizontal_scores.setSpacing(12)
        layout_horizontal_scores.setContentsMargins(0, 0, 0, 0)
        
        # Grupo Marcador
        grupo_marcador = QGroupBox("Marcador")
        layout_marcador = QHBoxLayout()
        layout_marcador.setSpacing(20)
        layout_marcador.setContentsMargins(10, 15, 10, 15)
        
        # Goles local
        layout_goles_local = QVBoxLayout()
        layout_goles_local.setSpacing(5)
        layout_goles_local.addWidget(QLabel("Goles Local:"))
        self.goles_local = QSpinBox()
        self.goles_local.setRange(0, 99)
        self.goles_local.setValue(0)
        self.goles_local.setMinimumWidth(80)
        layout_goles_local.addWidget(self.goles_local)
        layout_marcador.addLayout(layout_goles_local)
        
        layout_marcador.addWidget(QLabel("-"))
        
        # Goles visitante
        layout_goles_visitante = QVBoxLayout()
        layout_goles_visitante.setSpacing(5)
        layout_goles_visitante.addWidget(QLabel("Goles Visitante:"))
        self.goles_visitante = QSpinBox()
        self.goles_visitante.setRange(0, 99)
        self.goles_visitante.setValue(0)
        self.goles_visitante.setMinimumWidth(80)
        layout_goles_visitante.addWidget(self.goles_visitante)
        layout_marcador.addLayout(layout_goles_visitante)
        
        layout_marcador.addStretch()
        grupo_marcador.setLayout(layout_marcador)
        grupo_marcador.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Grupo Penaltis
        self.grupo_penaltis = QGroupBox("Penaltis")
        layout_penaltis = QHBoxLayout()
        layout_penaltis.setSpacing(20)
        layout_penaltis.setContentsMargins(10, 15, 10, 15)
        
        # Penaltis local
        layout_pen_local = QVBoxLayout()
        layout_pen_local.setSpacing(5)
        layout_pen_local.addWidget(QLabel("Penaltis Local:"))
        self.penaltis_local = QSpinBox()
        self.penaltis_local.setRange(0, 99)
        self.penaltis_local.setValue(0)
        self.penaltis_local.setMinimumWidth(80)
        layout_pen_local.addWidget(self.penaltis_local)
        layout_penaltis.addLayout(layout_pen_local)
        
        layout_penaltis.addWidget(QLabel("-"))
        
        # Penaltis visitante
        layout_pen_visitante = QVBoxLayout()
        layout_pen_visitante.setSpacing(5)
        layout_pen_visitante.addWidget(QLabel("Penaltis Visitante:"))
        self.penaltis_visitante = QSpinBox()
        self.penaltis_visitante.setRange(0, 99)
        self.penaltis_visitante.setValue(0)
        self.penaltis_visitante.setMinimumWidth(80)
        layout_pen_visitante.addWidget(self.penaltis_visitante)
        layout_penaltis.addLayout(layout_pen_visitante)
        
        layout_penaltis.addStretch()
        self.grupo_penaltis.setLayout(layout_penaltis)
        self.grupo_penaltis.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Añadir ambos grupos al layout horizontal con mismo ancho
        layout_horizontal_scores.addWidget(grupo_marcador, 1)
        layout_horizontal_scores.addWidget(self.grupo_penaltis, 1)
        
        # Añadir el layout horizontal al layout principal
        layout_resultado.addLayout(layout_horizontal_scores)
        
        # Tabla de estadísticas del partido
        layout_resultado.addWidget(QLabel("Estadísticas del partido:"))
        self.tabla_stats_partido = QTableWidget()
        self.tabla_stats_partido.setColumnCount(5)
        self.tabla_stats_partido.setHorizontalHeaderLabels([
            "Jugador", "Equipo", "Goles", "Amarillas", "Rojas"
        ])
        self.tabla_stats_partido.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        
        # Configurar columnas editables/no editables
        header_stats = self.tabla_stats_partido.horizontalHeader()
        header_stats.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_stats.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_stats.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header_stats.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header_stats.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout_resultado.addWidget(self.tabla_stats_partido)
        
        # Botones inferiores
        layout_botones_resultado = QHBoxLayout()
        
        # Botón para gestionar goles con autor (abre diálogo)
        self.btn_detalles_goles = QPushButton("Detalles de goles...")
        self.btn_detalles_goles.setToolTip("Asignar autores y minutos a los goles (opcional)")
        self.btn_detalles_goles.setObjectName("secondaryButton")
        layout_botones_resultado.addWidget(self.btn_detalles_goles)
        
        layout_botones_resultado.addStretch()
        
        # Botón para activar edición de resultado
        self.editar_resultado_btn = QPushButton("Editar resultado")
        self.editar_resultado_btn.setObjectName("primaryButton")
        layout_botones_resultado.addWidget(self.editar_resultado_btn)
        
        layout_botones_resultado.addStretch()
        
        self.guardar_resultado = QPushButton("Guardar resultado")
        self.guardar_resultado.setObjectName("successButton")
        self.cancelar_cambios = QPushButton("Cancelar cambios")
        layout_botones_resultado.addWidget(self.guardar_resultado)
        layout_botones_resultado.addWidget(self.cancelar_cambios)
        layout_resultado.addLayout(layout_botones_resultado)
        
        tab_resultado.setLayout(layout_resultado)
        self.tabs_detalle.addTab(tab_resultado, "Resultado")
    
    def conectar_senales(self):
        """Conecta las señales de los widgets."""
        print("[DEBUG] PageCalendarioPartidos.conectar_senales() - Iniciando...")
        
        # Desconectar señales previas para evitar duplicados
        try:
            self.btnNuevoPartidoTop.clicked.disconnect()
        except:
            pass
        try:
            self.btnReiniciarTorneo.clicked.disconnect()
        except:
            pass
        
        # Botones de la barra superior
        try:
            self.btnNuevoPartidoTop.clicked.connect(self._emit_nuevo_partido_signal)
            print("  - btnNuevoPartidoTop.clicked conectado a _emit_nuevo_partido_signal")
        except Exception as e:
            print(f"  - ERROR conectando btnNuevoPartidoTop: {e}")
            print(traceback.format_exc())
        
        try:
            self.btnReiniciarTorneo.clicked.connect(self._emit_reiniciar_torneo_signal)
            print("  - btnReiniciarTorneo.clicked conectado a _emit_reiniciar_torneo_signal")
        except Exception as e:
            print(f"  - ERROR conectando btnReiniciarTorneo: {e}")
            print(traceback.format_exc())
        
        # Filtros
        self.filtro_ronda.currentTextChanged.connect(self.on_filtros_changed)
        self.filtro_estado.currentTextChanged.connect(self.on_filtros_changed)
        
        # Calendario
        self.calendario_partidos.dia_clicked_signal.connect(self.on_dia_calendario_clicked)
        
        # Botones de edición en tab Datos
        self.btnGuardar.clicked.connect(self.guardar_partido_signal.emit)
        self.btnEliminar.clicked.connect(self.eliminar_partido_signal.emit)
        self.btnCancelar.clicked.connect(self.cancelar_partido_signal.emit)
        
        # Detectar cambios en tab Datos para dirty state
        self.comboFase.currentIndexChanged.connect(lambda: self.mark_datos_dirty())
        self.comboLocal.currentIndexChanged.connect(lambda: self.mark_datos_dirty())
        self.comboVisitante.currentIndexChanged.connect(lambda: self.mark_datos_dirty())
        self.fecha_hora.dateTimeChanged.connect(lambda: self.mark_datos_dirty())
        self.comboArbitro.currentIndexChanged.connect(lambda: self.mark_datos_dirty())
        
        # Convocatoria: las listas con checkboxes manejan su propio estado
        # (no necesitan señales de añadir/quitar porque usan checkboxes)
        
        # Resultado: detectar cambios para dirty state
        self.editar_resultado_btn.clicked.connect(self.on_editar_resultado_clicked)
        self.goles_local.valueChanged.connect(self.on_goles_changed)
        self.goles_local.valueChanged.connect(lambda: self.mark_resultado_dirty())
        self.goles_visitante.valueChanged.connect(self.on_goles_changed)
        self.goles_visitante.valueChanged.connect(lambda: self.mark_resultado_dirty())
        self.penaltis_local.valueChanged.connect(self.validar_guardar_resultado)
        self.penaltis_local.valueChanged.connect(lambda: self.mark_resultado_dirty())
        self.penaltis_visitante.valueChanged.connect(self.validar_guardar_resultado)
        self.penaltis_visitante.valueChanged.connect(lambda: self.mark_resultado_dirty())
        self.guardar_resultado.clicked.connect(self.on_guardar_resultado_clicked)
        self.cancelar_cambios.clicked.connect(self.cancelar_cambios_signal.emit)
        
        # Botón de detalles de goles
        self.btn_detalles_goles.clicked.connect(self.on_detalles_goles)
    
    def debug_buttons(self):
        """Verifica que los botones superiores existen correctamente."""
        DEBUG = True  # Cambiar a False en producción
        if DEBUG:
            print("[DEBUG] PageCalendarioPartidos - Verificación de botones:")
            print(f"  - btnNuevoPartidoTop existe: {hasattr(self, 'btnNuevoPartidoTop') and self.btnNuevoPartidoTop is not None}")
            print(f"  - btnReiniciarTorneo existe: {hasattr(self, 'btnReiniciarTorneo') and self.btnReiniciarTorneo is not None}")
            if hasattr(self, 'btnNuevoPartidoTop') and self.btnNuevoPartidoTop:
                print(f"  - btnNuevoPartidoTop text: '{self.btnNuevoPartidoTop.text()}'")
                print(f"  - btnNuevoPartidoTop isVisible: {self.btnNuevoPartidoTop.isVisible()}")
                print(f"  - btnNuevoPartidoTop isEnabled: {self.btnNuevoPartidoTop.isEnabled()}")
                print(f"  - btnNuevoPartidoTop geometry: {self.btnNuevoPartidoTop.geometry()}")
                print(f"  - btnNuevoPartidoTop objectName: {self.btnNuevoPartidoTop.objectName()}")
            if hasattr(self, 'btnReiniciarTorneo') and self.btnReiniciarTorneo:
                print(f"  - btnReiniciarTorneo text: '{self.btnReiniciarTorneo.text()}'")
                print(f"  - btnReiniciarTorneo isVisible: {self.btnReiniciarTorneo.isVisible()}")
                print(f"  - btnReiniciarTorneo isEnabled: {self.btnReiniciarTorneo.isEnabled()}")
    
    def install_probe_slots(self):
        """🔴 AUDIT: Instala slots de prueba directos para verificar que los clicks llegan."""
        print("[AUDIT] Instalando probe slots...")
        try:
            # Probe slot para Nuevo Partido
            self.btnNuevoPartidoTop.clicked.connect(
                lambda: print("✅ [PROBE SLOT] CLICK NUEVO PARTIDO DETECTADO!")
            )
            print("  - Probe slot 'Nuevo partido' instalado")
            
            # Probe slot para Reiniciar Torneo
            self.btnReiniciarTorneo.clicked.connect(
                lambda: print("✅ [PROBE SLOT] CLICK REINICIAR TORNEO DETECTADO!")
            )
            print("  - Probe slot 'Reiniciar torneo' instalado")
        except Exception as e:
            print(f"[AUDIT ERROR] Error instalando probe slots: {e}")
            print(traceback.format_exc())
    
    def install_event_filters(self):
        """🔴 AUDIT: Instala eventFilters para capturar eventos de mouse."""
        print("[AUDIT] Instalando eventFilters...")
        try:
            # EventFilter para Nuevo Partido
            self.filter_nuevo = ButtonDebugEventFilter("btnNuevoPartidoTop")
            self.btnNuevoPartidoTop.installEventFilter(self.filter_nuevo)
            print("  - EventFilter 'Nuevo partido' instalado")
            
            # EventFilter para Reiniciar Torneo
            self.filter_reiniciar = ButtonDebugEventFilter("btnReiniciarTorneo")
            self.btnReiniciarTorneo.installEventFilter(self.filter_reiniciar)
            print("  - EventFilter 'Reiniciar torneo' instalado")
        except Exception as e:
            print(f"[AUDIT ERROR] Error instalando eventFilters: {e}")
            print(traceback.format_exc())
    
    def _emit_nuevo_partido_signal(self):
        """🔴 AUDIT: Wrapper para emitir nuevo_partido_signal con debug."""
        try:
            print("🔵 [SIGNAL EMIT] nuevo_partido_signal.emit() ejecutándose...")
            self.nuevo_partido_signal.emit()
            print("🔵 [SIGNAL EMIT] nuevo_partido_signal.emit() completado")
        except Exception as e:
            print(f"❌ [SIGNAL EMIT ERROR] nuevo_partido_signal: {e}")
            print(traceback.format_exc())
    
    def _emit_reiniciar_torneo_signal(self):
        """🔴 AUDIT: Wrapper para emitir reiniciar_torneo_signal con debug."""
        try:
            print("🔵 [SIGNAL EMIT] reiniciar_torneo_signal.emit() ejecutándose...")
            self.reiniciar_torneo_signal.emit()
            print("🔵 [SIGNAL EMIT] reiniciar_torneo_signal.emit() completado")
        except Exception as e:
            print(f"❌ [SIGNAL EMIT ERROR] reiniciar_torneo_signal: {e}")
            print(traceback.format_exc())
    
    def _on_fase_changed(self, index):
        """Valida que la fase seleccionada sea válida (fase anterior completa)."""
        if index < 0:
            return
        
        fase_id = self.comboFase.itemData(index)
        if not fase_id:
            return
        
        # Validar que la fase anterior esté completa
        from app.constants import FASES_CONFIG
        from app.models.match_model import MatchModel
        
        fase_config = FASES_CONFIG.get(fase_id)
        if not fase_config:
            return
        
        fase_anterior = fase_config.get("prev")
        
        # Si hay fase anterior, verificar que esté completa
        if fase_anterior:
            config_anterior = FASES_CONFIG.get(fase_anterior)
            partidos_requeridos = config_anterior.get("required", 0)
            
            # Contar partidos programados/jugados en la fase anterior
            try:
                partidos_anteriores = MatchModel.obtener_partidos_por_fase(fase_anterior)
                count_programados = len([p for p in partidos_anteriores if p.get('estado') in ['Programado', 'Jugado']])
                
                if count_programados < partidos_requeridos:
                    # Revertir cambio
                    self.comboFase.blockSignals(True)
                    # Buscar índice de fase anterior
                    for i in range(self.comboFase.count()):
                        if self.comboFase.itemData(i) == fase_anterior:
                            self.comboFase.setCurrentIndex(i)
                            break
                    self.comboFase.blockSignals(False)
                    
                    # Mostrar mensaje
                    QMessageBox.warning(
                        self,
                        "Fase no disponible",
                        f"No se puede crear partidos de {fase_config['label']}.\n\n"
                        f"Primero debes programar todos los partidos de {config_anterior['label']}\n"
                        f"({count_programados}/{partidos_requeridos} programados)."
                    )
                    return
            except Exception as e:
                print(f"[ERROR] Validación de fase: {e}")
        
        # Emitir señal para que el controlador sepa que cambió
        if hasattr(self, 'fase_changed_signal'):
            self.fase_changed_signal.emit(fase_id)
    
    def aplicar_validaciones_iniciales(self):
        """Aplica las validaciones iniciales de la interfaz."""
        # Deshabilitar grupo de penaltis por defecto
        self.grupo_penaltis.setEnabled(False)
        
        # Modo inicial: ver
        self.set_modo("ver")
    
    # ==================== DIRTY STATE TRACKING ====================
    
    def mark_datos_dirty(self):
        """Marca que los datos han cambiado."""
        self.datos_dirty = True
        self.update_guardar_button_state()
    
    def mark_convocatoria_dirty(self):
        """Marca que la convocatoria ha cambiado."""
        self.convocatoria_dirty = True
        self.update_guardar_button_state()
    
    def mark_resultado_dirty(self):
        """Marca que el resultado ha cambiado."""
        self.resultado_dirty = True
        self.update_guardar_button_state()
    
    def clear_all_dirty_flags(self):
        """Limpia todos los flags de cambio."""
        self.datos_dirty = False
        self.convocatoria_dirty = False
        self.resultado_dirty = False
        self.update_guardar_button_state()
    
    def has_unsaved_changes(self) -> bool:
        """Verifica si hay cambios sin guardar."""
        return self.datos_dirty or self.convocatoria_dirty or self.resultado_dirty
    
    def update_guardar_button_state(self):
        """Actualiza el estado del botón Guardar según el dirty state y modo actual."""
        if not hasattr(self, 'btnGuardar'):
            return
        
        # En modo ver, nunca habilitado
        if self.modo_actual == "ver":
            self.btnGuardar.setEnabled(False)
            return
        
        # En modo editar, habilitar si hay cambios o si es nuevo partido
        if self.modo_actual in ["crear", "editar"]:
            self.btnGuardar.setEnabled(self.datos_dirty or not self.partido_actual_id)
            return
        
        # En modo editar_resultado, habilitar si hay cambios
        if self.modo_actual == "editar_resultado":
            self.btnGuardar.setEnabled(self.resultado_dirty)
            return
    
    def puede_guardar_resultado(self) -> tuple[bool, str]:
        """
        Valida si se puede guardar el resultado.
        
        Returns:
            (puede_guardar, mensaje_error)
        """
        if not self.partido_actual:
            return False, "No hay partido cargado"
        
        # Validar equipos
        local_id = self.partido_actual.get('local_id') or self.partido_actual.get('equipo_local_id')
        visitante_id = self.partido_actual.get('visitante_id') or self.partido_actual.get('equipo_visitante_id')
        
        if not local_id or not visitante_id:
            return False, "El partido no tiene equipos asignados.\n\nVaya a 'Datos' y asigne ambos equipos."
        
        # Validar árbitro
        arbitro = self.comboArbitro.currentText()
        if arbitro == "Sin árbitro" or not arbitro or arbitro == "Sin asignar":
            return False, "Debe asignar un árbitro antes de guardar el resultado."
        
        # Validar empate total
        goles_local = self.goles_local.value()
        goles_visitante = self.goles_visitante.value()
        penaltis_local = self.penaltis_local.value()
        penaltis_visitante = self.penaltis_visitante.value()
        
        if (goles_local == goles_visitante and 
            penaltis_local == penaltis_visitante):
            return False, "No puede haber empate en goles y penaltis.\nDebe haber un ganador."
        
        return True, ""
    
    # ==================== END DIRTY STATE TRACKING ====================
    
    def on_filtros_changed(self):
        """Maneja el cambio en los filtros."""
        filtros = {
            'ronda': self.filtro_ronda.currentText(),
            'estado': self.filtro_estado.currentText()
        }
        self.filtros_changed_signal.emit(filtros)
    
    def on_fecha_hora_changed(self):
        """Maneja el cambio de fecha/hora del partido."""
        if self.partido_actual_id and self.modo_actual == "editar_resultado":
            nueva_fecha = self.fecha_hora.dateTime().toString("yyyy-MM-dd HH:mm")
            self.fecha_hora_cambiada_signal.emit(nueva_fecha)
    
    def on_arbitro_changed(self, index: int):
        """Maneja el cambio de árbitro del partido."""
        if self.partido_actual_id and self.modo_actual == "editar_resultado":
            nuevo_arbitro = self.comboArbitro.currentText()
            if nuevo_arbitro and nuevo_arbitro != "Sin asignar" and nuevo_arbitro != "Sin árbitro":
                self.arbitro_cambiado_signal.emit(nuevo_arbitro)
    
    def obtener_filtros_actuales(self) -> dict:
        return {
            'eliminatoria': self.filtro_ronda.currentText(),
            'estado': self.filtro_estado.currentText()
        }
    
    def on_dia_calendario_clicked(self, fecha: QDate):
        """Maneja el clic en un día del calendario."""
        from app.models.match_model import MatchModel
        from app.models.participant_model import ParticipantModel
        
        # Obtener partidos programados para esa fecha
        fecha_str = fecha.toString("yyyy-MM-dd")
        partidos_dia = MatchModel.obtener_partidos_por_fecha(fecha_str)
        
        # Obtener partidos pendientes (sin fecha)
        partidos_pendientes = MatchModel.obtener_partidos_pendientes()
        
        # Obtener árbitros
        arbitros = ParticipantModel.listar_arbitros()
        
        # Abrir diálogo editable
        dialog = DialogPartidosDia(fecha, partidos_dia, partidos_pendientes, arbitros, self)
        dialog.abrir_detalle_signal.connect(self.on_abrir_partido_desde_dialogo)
        dialog.partido_programado_signal.connect(self.on_partido_programado)
        dialog.exec()
    
    def on_partido_programado(self):
        """Refresca el calendario tras programar un partido."""
        self.filtros_changed_signal.emit(self.obtener_filtros_actuales())
        # Refresh calendar marks immediately
        self.calendario_partidos.refresh_calendar_marks()
    
    def on_abrir_partido_desde_dialogo(self, partido_id: int):
        """Maneja la señal de abrir partido desde el diálogo."""
        try:
            # Emitir señal para que el controlador cargue el partido
            self.abrir_partido_desde_dialogo_signal.emit(partido_id)
            # Cambiar a la pestaña Datos
            self.tabs_detalle.setCurrentIndex(0)
        except Exception as e:
            print(f"[ERROR] Error al abrir partido {partido_id} desde diálogo: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el partido en el panel de detalle.\n\nError: {str(e)}"
            )
    
    def on_editar_resultado_clicked(self):
        """Activa el modo de edición de resultado."""
        if not self.partido_actual_id:
            QMessageBox.warning(
                self,
                "Aviso",
                "Debe seleccionar un partido primero."
            )
            return
        
        # Cambiar a modo editar_resultado
        self.set_modo("editar_resultado")
        
        # Cambiar a la pestaña Resultado
        self.tabs_detalle.setCurrentIndex(2)
    
    def on_goles_changed(self):
        """Maneja el cambio en los goles para habilitar/deshabilitar penaltis."""
        empate = (self.goles_local.value() == self.goles_visitante.value())
        self.grupo_penaltis.setEnabled(empate and self.modo_actual == "editar_resultado")
        
        if not empate:
            self.penaltis_local.setValue(0)
            self.penaltis_visitante.setValue(0)
        
        # Validar botón guardar
        self.validar_guardar_resultado()
    
    def validar_guardar_resultado(self):
        """Valida si se puede guardar el resultado."""
        if self.modo_actual != "editar_resultado":
            return
        
        # Verificar que hay árbitro asignado
        arbitro = self.comboArbitro.currentText()
        sin_arbitro = (arbitro == "Sin árbitro" or not arbitro)
        
        # Verificar empate en goles y penaltis
        goles_local = self.goles_local.value()
        goles_visitante = self.goles_visitante.value()
        penaltis_local = self.penaltis_local.value()
        penaltis_visitante = self.penaltis_visitante.value()
        
        empate_total = (
            goles_local == goles_visitante and 
            penaltis_local == penaltis_visitante
        )
        
        # Deshabilitar si no hay árbitro o si hay empate total
        puede_guardar = not sin_arbitro and not empate_total
        self.guardar_resultado.setEnabled(puede_guardar)
    
    def on_guardar_resultado_clicked(self):
        """Maneja el clic en guardar resultado con validación."""
        # Validar que hay árbitro
        arbitro = self.comboArbitro.currentText()
        if arbitro == "Sin árbitro" or not arbitro:
            QMessageBox.warning(
                self,
                "Árbitro requerido",
                "Debe asignar un árbitro antes de guardar el resultado del partido."
            )
            return
        
        # Validar empate total
        goles_local = self.goles_local.value()
        goles_visitante = self.goles_visitante.value()
        penaltis_local = self.penaltis_local.value()
        penaltis_visitante = self.penaltis_visitante.value()
        
        if (goles_local == goles_visitante and 
            penaltis_local == penaltis_visitante):
            QMessageBox.warning(
                self,
                "Resultado no válido",
                "No puede haber empate en goles y penaltis. Debe haber un ganador."
            )
            return
        
        # Si pasa las validaciones, emitir señal
        self.guardar_resultado_signal.emit()
    
    def on_convocatoria_changed(self, equipo: str, accion: str):
        """Maneja los cambios en la convocatoria."""
        if equipo == "local":
            if accion == "anadir":
                tabla_disponibles = self.jugadores_disponibles_local
                selected = tabla_disponibles.currentRow()
                if selected >= 0:
                    item = tabla_disponibles.item(selected, 0)
                    participante_id = item.data(Qt.ItemDataRole.UserRole)
                    if hasattr(self, '_partido_actual_local_id'):
                        equipo_id = self._partido_actual_local_id
                        self.convocatoria_cambiada_signal.emit({
                            'accion': 'convocar',
                            'participante_id': participante_id,
                            'equipo_id': equipo_id
                        })
            elif accion == "quitar":
                tabla_convocados = self.jugadores_convocados_local
                selected = tabla_convocados.currentRow()
                if selected >= 0:
                    item = tabla_convocados.item(selected, 0)
                    participante_id = item.data(Qt.ItemDataRole.UserRole)
                    self.convocatoria_cambiada_signal.emit({
                        'accion': 'quitar',
                        'participante_id': participante_id,
                        'equipo_id': None
                    })
        elif equipo == "visitante":
            if accion == "anadir":
                tabla_disponibles = self.jugadores_disponibles_visitante
                selected = tabla_disponibles.currentRow()
                if selected >= 0:
                    item = tabla_disponibles.item(selected, 0)
                    participante_id = item.data(Qt.ItemDataRole.UserRole)
                    if hasattr(self, '_partido_actual_visitante_id'):
                        equipo_id = self._partido_actual_visitante_id
                        self.convocatoria_cambiada_signal.emit({
                            'accion': 'convocar',
                            'participante_id': participante_id,
                            'equipo_id': equipo_id
                        })
            elif accion == "quitar":
                tabla_convocados = self.jugadores_convocados_visitante
                selected = tabla_convocados.currentRow()
                if selected >= 0:
                    item = tabla_convocados.item(selected, 0)
                    participante_id = item.data(Qt.ItemDataRole.UserRole)
                    self.convocatoria_cambiada_signal.emit({
                        'accion': 'quitar',
                        'participante_id': participante_id,
                        'equipo_id': None
                    })
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self._cargado_inicial:
            self._cargado_inicial = True
            self.filtros_changed_signal.emit(self.obtener_filtros_actuales())
        # Refresh calendar marks on show
        self.calendario_partidos.refresh_calendar_marks()
    
    def set_filas_tabla(self, partidos: list[dict]):
        self.partidos_cache = partidos
        self.calendario_partidos.set_partidos(partidos)
        # Also refresh marks after setting partidos
        self.calendario_partidos.refresh_calendar_marks()
    
    def actualizar_tabla(self, partidos: list[dict]):
        self.set_filas_tabla(partidos)
    
    def cargar_arbitros_en_combo(self, arbitros: list[str]):
        self.comboArbitro.clear()
        self.comboArbitro.addItems(arbitros)
    
    def set_lista_arbitros(self, arbitros: list[str]):
        """Establece la lista de árbitros en el combo."""
        self.comboArbitro.clear()
        self.comboArbitro.addItem("Sin árbitro")
        self.comboArbitro.addItems(arbitros)
    
    def set_datos_partido(self, datos: dict):
        """Establece los datos en el panel de detalle."""
        # Datos básicos
        local = datos.get('local', '')
        visitante = datos.get('visitante', '')
        self.partido_titulo.setText(f"{local} vs {visitante}")
        self.ronda_label.setText(datos.get('ronda', '-'))
        
        # Fecha y hora
        fecha_str = datos.get('fecha_hora', '')
        if fecha_str:
            try:
                fecha = QDateTime.fromString(fecha_str, "dd/MM/yyyy HH:mm")
                if fecha.isValid():
                    self.fecha_hora.setDateTime(fecha)
            except:
                pass
        
        # Árbitro
        arbitro = datos.get('arbitro', 'Sin árbitro')
        index_arbitro = self.comboArbitro.findText(arbitro)
        if index_arbitro >= 0:
            self.comboArbitro.setCurrentIndex(index_arbitro)
        
        # Equipos en convocatoria
        self.equipo_local_label.setText(f"Equipo: {local}")
        self.equipo_visitante_label.setText(f"Equipo: {visitante}")
        
        # Resultado
        self.goles_local.setValue(int(datos.get('goles_local', 0)))
        self.goles_visitante.setValue(int(datos.get('goles_visitante', 0)))
        self.penaltis_local.setValue(int(datos.get('penaltis_local', 0)))
        self.penaltis_visitante.setValue(int(datos.get('penaltis_visitante', 0)))
    
    def get_datos_resultado(self) -> dict:
        """Obtiene los datos del resultado."""
        # Obtener estadísticas de la tabla
        stats = []
        for fila in range(self.tabla_stats_partido.rowCount()):
            # Obtener participante_id desde el UserRole del item de jugador
            item_jugador = self.tabla_stats_partido.item(fila, 0)
            participante_id = item_jugador.data(Qt.ItemDataRole.UserRole) if item_jugador else None
            
            stat = {
                'participante_id': participante_id,
                'jugador': self.tabla_stats_partido.item(fila, 0).text(),
                'equipo': self.tabla_stats_partido.item(fila, 1).text(),
                'goles': int(self.tabla_stats_partido.item(fila, 2).text() or 0),
                'amarillas': int(self.tabla_stats_partido.item(fila, 3).text() or 0),
                'rojas': int(self.tabla_stats_partido.item(fila, 4).text() or 0)
            }
            stats.append(stat)
        
        return {
            'arbitro': self.comboArbitro.currentText(),
            'arbitro_nombre': self.comboArbitro.currentText(),
            'goles_local': self.goles_local.value(),
            'goles_visitante': self.goles_visitante.value(),
            'penaltis_local': self.penaltis_local.value(),
            'penaltis_visitante': self.penaltis_visitante.value(),
            'stats': stats
        }
    
    # ==================== GESTIÓN GOLES CON AUTOR ====================
    
    def get_goles_detalle(self) -> list[dict]:
        """Obtiene los goles detallados desde el caché del diálogo."""
        return getattr(self, 'goles_detalle_cache', [])
    
    def on_detalles_goles(self):
        """Abre el diálogo de detalles de goles."""
        if not self.partido_actual:
            QMessageBox.warning(self, "Aviso", "Debe cargar un partido primero")
            return
        
        from app.views.dialogs.dialog_goles_detalle import DialogGolesDetalle
        
        # Obtener goles actuales desde el spinbox
        goles_local = self.goles_local.value()
        goles_visitante = self.goles_visitante.value()
        
        # Debug: verificar caché
        cache_actual = getattr(self, 'goles_detalle_cache', [])
        print(f"\n[VIEW on_detalles_goles] Abriendo diálogo de goles")
        print(f"[VIEW on_detalles_goles] Cache actual: {len(cache_actual)} goles")
        print(f"[VIEW on_detalles_goles] Marcador: {goles_local}-{goles_visitante}")
        
        # Crear el diálogo
        dialog = DialogGolesDetalle(
            parent=self,
            partido_actual=self.partido_actual,
            goles_local=goles_local,
            goles_visitante=goles_visitante,
            goles_detalle_iniciales=cache_actual
        )
        
        # Si el usuario acepta el diálogo, guardar los goles detallados
        if dialog.exec() == QDialog.DialogCode.Accepted:
            goles_retornados = dialog.get_goles_detalle()
            print(f"[VIEW on_detalles_goles] Usuario aceptó, goles retornados: {len(goles_retornados)}")
            self.goles_detalle_cache = goles_retornados
            self.mark_resultado_dirty()
            # Sincronizar goles en la tabla de estadísticas
            self.sincronizar_goles_en_stats()
            print(f"[VIEW on_detalles_goles] ✓ Goles sincronizados\n")
        else:
            print(f"[VIEW on_detalles_goles] Usuario canceló\n")
    
    # ==================== FIN GESTIÓN GOLES CON AUTOR ====================
    
    def set_jugadores_disponibles(self, local: list[str], visitante: list[str]):
        """Establece los jugadores disponibles para cada equipo."""
        # Local
        self.jugadores_disponibles_local.setRowCount(0)
        for jugador in local:
            fila = self.jugadores_disponibles_local.rowCount()
            self.jugadores_disponibles_local.insertRow(fila)
            self.jugadores_disponibles_local.setItem(
                fila, 0, QTableWidgetItem(jugador)
            )
        
        # Visitante
        self.jugadores_disponibles_visitante.setRowCount(0)
        for jugador in visitante:
            fila = self.jugadores_disponibles_visitante.rowCount()
            self.jugadores_disponibles_visitante.insertRow(fila)
            self.jugadores_disponibles_visitante.setItem(
                fila, 0, QTableWidgetItem(jugador)
            )
    
    def set_jugadores_convocados(self, local: list[str], visitante: list[str]):
        """Establece los jugadores convocados para cada equipo."""
        # Local
        self.jugadores_convocados_local.setRowCount(0)
        for jugador in local:
            fila = self.jugadores_convocados_local.rowCount()
            self.jugadores_convocados_local.insertRow(fila)
            self.jugadores_convocados_local.setItem(
                fila, 0, QTableWidgetItem(jugador)
            )
        
        # Visitante
        self.jugadores_convocados_visitante.setRowCount(0)
        for jugador in visitante:
            fila = self.jugadores_convocados_visitante.rowCount()
            self.jugadores_convocados_visitante.insertRow(fila)
            self.jugadores_convocados_visitante.setItem(
                fila, 0, QTableWidgetItem(jugador)
            )
    
    def set_stats_partido(self, filas: list[dict]):
        """Rellena la tabla de estadísticas del partido."""
        self.tabla_stats_partido.setRowCount(0)
        
        for stat in filas:
            fila = self.tabla_stats_partido.rowCount()
            self.tabla_stats_partido.insertRow(fila)
            
            # Jugador y equipo no editables
            item_jugador = QTableWidgetItem(str(stat.get('jugador', '')))
            item_jugador.setFlags(item_jugador.flags() & ~Qt.ItemFlag.ItemIsEditable)
            # Guardar participante_id en UserRole para sincronizar goles
            item_jugador.setData(Qt.ItemDataRole.UserRole, stat.get('participante_id'))
            self.tabla_stats_partido.setItem(fila, 0, item_jugador)
            
            item_equipo = QTableWidgetItem(str(stat.get('equipo', '')))
            item_equipo.setFlags(item_equipo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_stats_partido.setItem(fila, 1, item_equipo)
            
            # Goles: NO editable, se sincroniza desde detalles
            item_goles = QTableWidgetItem(str(stat.get('goles', '0')))
            item_goles.setFlags(item_goles.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_goles.setToolTip("Los goles se gestionan desde 'Detalles de goles...'")
            self.tabla_stats_partido.setItem(fila, 2, item_goles)
            
            # Amarillas y rojas editables
            self.tabla_stats_partido.setItem(
                fila, 3, QTableWidgetItem(str(stat.get('amarillas', '0')))
            )
            self.tabla_stats_partido.setItem(
                fila, 4, QTableWidgetItem(str(stat.get('rojas', '0')))
            )
    
    def sincronizar_goles_en_stats(self):
        """Sincroniza los goles desde goles_detalle_cache a la tabla de estadísticas."""
        print(f"[VIEW sincronizar_goles_en_stats] Iniciando sincronización...")
        
        if not hasattr(self, 'goles_detalle_cache'):
            print(f"[VIEW sincronizar_goles_en_stats] No hay caché de goles")
            return
        
        print(f"[VIEW sincronizar_goles_en_stats] Caché tiene {len(self.goles_detalle_cache)} goles")
        
        # Contar goles por jugador desde el caché
        goles_por_jugador = {}
        for gol in self.goles_detalle_cache:
            participante_id = gol.get('participante_id')
            if participante_id:
                goles_por_jugador[participante_id] = goles_por_jugador.get(participante_id, 0) + 1
        
        print(f"[VIEW sincronizar_goles_en_stats] Distribución: {goles_por_jugador}")
        
        # Actualizar TODAS las filas de la tabla de stats
        actualizados = 0
        for fila in range(self.tabla_stats_partido.rowCount()):
            item_jugador = self.tabla_stats_partido.item(fila, 0)
            if item_jugador:
                participante_id = item_jugador.data(Qt.ItemDataRole.UserRole)
                # Obtener goles para este jugador (0 si no tiene)
                goles = goles_por_jugador.get(participante_id, 0)
                
                item_goles = self.tabla_stats_partido.item(fila, 2)
                if item_goles:
                    item_goles.setText(str(goles))
                    actualizados += 1
        
        # CRÍTICO: Forzar actualización visual de la tabla
        self.tabla_stats_partido.viewport().update()
        
        print(f"[VIEW sincronizar_goles_en_stats] ✓ {actualizados} filas actualizadas y tabla refrescada")
    
    def limpiar_detalle(self):
        """Limpia todos los campos del detalle."""
        self.partido_titulo.setText("Seleccione un partido")
        self.ronda_label.setText("-")
        self.fecha_hora.setDateTime(QDateTime.currentDateTime())
        self.comboArbitro.setCurrentIndex(0)
        
        self.equipo_local_label.setText("Equipo: -")
        self.equipo_visitante_label.setText("Equipo: -")
        self.jugadores_disponibles_local.setRowCount(0)
        self.jugadores_disponibles_visitante.setRowCount(0)
        self.jugadores_convocados_local.setRowCount(0)
        self.jugadores_convocados_visitante.setRowCount(0)
        
        self.goles_local.setValue(0)
        self.goles_visitante.setValue(0)
        self.penaltis_local.setValue(0)
        self.penaltis_visitante.setValue(0)
        self.tabla_stats_partido.setRowCount(0)
        
        # Limpiar caché de goles detallados
        self.goles_detalle_cache = []
    
    def rellenar_detalle(self, partido: dict):
        """Rellena el detalle con los datos del partido."""
        # Guardar ID del partido actual y referencia completa
        self.partido_actual_id = partido.get('id')
        self.partido_actual = partido
        
        local = partido.get('local_nombre', '')
        visitante = partido.get('visitante_nombre', '')
        self.partido_titulo.setText(f"{local} vs {visitante}")
        
        self._partido_actual_local_id = partido.get('local_id')
        self._partido_actual_visitante_id = partido.get('visitante_id')
        
        # Rellenar combo de fase
        fase = partido.get('eliminatoria', '')
        if fase:
            # Buscar por userData (fase_id)
            for i in range(self.comboFase.count()):
                if self.comboFase.itemData(i) == fase:
                    self.comboFase.setCurrentIndex(i)
                    break
        
        # Rellenar combos de equipos
        local_id = partido.get('local_id')
        visitante_id = partido.get('visitante_id')
        
        for i in range(self.comboLocal.count()):
            if self.comboLocal.itemData(i) == local_id:
                self.comboLocal.setCurrentIndex(i)
                break
        
        for i in range(self.comboVisitante.count()):
            if self.comboVisitante.itemData(i) == visitante_id:
                self.comboVisitante.setCurrentIndex(i)
                break
        
        # Rellenar fecha y hora
        fecha_str = partido.get('fecha_hora', '')
        if fecha_str:
            try:
                if ' ' in fecha_str:
                    qdatetime = QDateTime.fromString(fecha_str, "yyyy-MM-dd HH:mm")
                    if not qdatetime.isValid():
                        qdatetime = QDateTime.fromString(fecha_str, "yyyy-MM-dd HH:mm:ss")
                else:
                    qdatetime = QDateTime.fromString(fecha_str, "yyyy-MM-dd")
                if qdatetime.isValid():
                    self.fecha_hora.setDateTime(qdatetime)
            except:
                pass
        
        # Rellenar estado
        estado = partido.get('estado', 'Programado')
        index_estado = self.comboEstado.findText(estado)
        if index_estado >= 0:
            self.comboEstado.setCurrentIndex(index_estado)
        
        # Rellenar árbitro
        arbitro_id = partido.get('arbitro_id')
        arbitro_nombre = partido.get('arbitro_nombre')
        if arbitro_nombre:
            for i in range(self.comboArbitro.count()):
                if self.comboArbitro.itemText(i) == arbitro_nombre:
                    self.comboArbitro.setCurrentIndex(i)
                    break
        else:
            self.comboArbitro.setCurrentIndex(0)  # Sin árbitro
        
        # Labels de equipo en convocatoria
        self.equipo_local_label.setText(f"Equipo: {local}")
        self.equipo_visitante_label.setText(f"Equipo: {visitante}")
        
        # Resultado
        goles_local = partido.get('goles_local')
        goles_visitante = partido.get('goles_visitante')
        self.goles_local.setValue(goles_local if goles_local is not None else 0)
        self.goles_visitante.setValue(goles_visitante if goles_visitante is not None else 0)
        
        penaltis_local = partido.get('penaltis_local')
        penaltis_visitante = partido.get('penaltis_visitante')
        self.penaltis_local.setValue(penaltis_local if penaltis_local is not None else 0)
        self.penaltis_visitante.setValue(penaltis_visitante if penaltis_visitante is not None else 0)
    
    def cargar_jugadores_disponibles(self, local: list[dict], visitante: list[dict]):
        """Carga los jugadores disponibles de ambos equipos (nueva estructura con checkboxes)."""
        print(f"[VIEW] cargar_jugadores_disponibles: {len(local)} local, {len(visitante)} visitante")
        
        # Activar flag para evitar señales durante carga
        self._convocatoria_loading = True
        
        # Verificar que los widgets existan
        if not hasattr(self, 'jugadores_lista_local') or not hasattr(self, 'jugadores_lista_visitante'):
            print("[WARNING] Listas de jugadores no inicializadas, omitiendo carga")
            self._convocatoria_loading = False
            return
        
        # Actualizar nombre del equipo local
        if hasattr(self, 'equipo_local_label') and hasattr(self, 'partido_actual'):
            local_nombre = self.partido_actual.get('local_nombre', '-') if self.partido_actual else '-'
            self.equipo_local_label.setText(f"Equipo: {local_nombre}")
        
        # Cargar jugadores del equipo local con checkboxes
        self.jugadores_lista_local.clear()
        for jugador in local:
            nombre = f"{jugador.get('nombre', '')} {jugador.get('apellidos', '')}".strip()
            item = QListWidgetItem(nombre)
            item.setData(Qt.ItemDataRole.UserRole, jugador.get('id'))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.jugadores_lista_local.addItem(item)
        
        # Actualizar nombre del equipo visitante
        if hasattr(self, 'equipo_visitante_label') and hasattr(self, 'partido_actual'):
            visitante_nombre = self.partido_actual.get('visitante_nombre', '-') if self.partido_actual else '-'
            self.equipo_visitante_label.setText(f"Equipo: {visitante_nombre}")
        
        # Cargar jugadores del equipo visitante con checkboxes
        self.jugadores_lista_visitante.clear()
        for jugador in visitante:
            nombre = f"{jugador.get('nombre', '')} {jugador.get('apellidos', '')}".strip()
            item = QListWidgetItem(nombre)
            item.setData(Qt.ItemDataRole.UserRole, jugador.get('id'))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.jugadores_lista_visitante.addItem(item)
        
        # Actualizar contadores
        if hasattr(self, '_actualizar_contador_convocados'):
            self._actualizar_contador_convocados(es_local=True)
            self._actualizar_contador_convocados(es_local=False)
        
        # Desactivar flag
        self._convocatoria_loading = False
        
        print(f"[VIEW] Jugadores cargados correctamente")
    
    def cargar_convocados(self, local: list[dict], visitante: list[dict]):
        """Carga los jugadores convocados (marca los checkboxes correspondientes)."""
        print(f"[VIEW] cargar_convocados: {len(local)} local, {len(visitante)} visitante")
        
        # Activar flag para evitar señales durante carga
        self._convocatoria_loading = True
        
        # Verificar que los widgets existan
        if not hasattr(self, 'jugadores_lista_local') or not hasattr(self, 'jugadores_lista_visitante'):
            print("[WARNING] Listas de jugadores no inicializadas, omitiendo carga de convocados")
            self._convocatoria_loading = False
            return
        
        # Crear sets con IDs de convocados para búsqueda rápida
        convocados_local_ids = {j.get('participante_id') for j in local}
        convocados_visitante_ids = {j.get('participante_id') for j in visitante}
        
        # Marcar checkboxes de convocados en lista local
        for i in range(self.jugadores_lista_local.count()):
            item = self.jugadores_lista_local.item(i)
            jugador_id = item.data(Qt.ItemDataRole.UserRole)
            if jugador_id in convocados_local_ids:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
        
        # Marcar checkboxes de convocados en lista visitante
        for i in range(self.jugadores_lista_visitante.count()):
            item = self.jugadores_lista_visitante.item(i)
            jugador_id = item.data(Qt.ItemDataRole.UserRole)
            if jugador_id in convocados_visitante_ids:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
        
        # Actualizar contadores
        if hasattr(self, '_actualizar_contador_convocados'):
            self._actualizar_contador_convocados(es_local=True)
            self._actualizar_contador_convocados(es_local=False)
        
        # Desactivar flag
        self._convocatoria_loading = False
        
        print(f"[VIEW] Convocados cargados y marcados correctamente")
    
    def cargar_stats(self, stats: list[dict]):
        """Carga las estadísticas del partido."""
        self.tabla_stats_partido.setRowCount(0)
        for stat in stats:
            fila = self.tabla_stats_partido.rowCount()
            self.tabla_stats_partido.insertRow(fila)
            
            nombre = f"{stat.get('nombre', '')} {stat.get('apellidos', '')}".strip()
            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_nombre.setData(Qt.ItemDataRole.UserRole, stat.get('participante_id'))
            self.tabla_stats_partido.setItem(fila, 0, item_nombre)
            
            equipo = stat.get('equipo_nombre', '')
            item_equipo = QTableWidgetItem(equipo)
            item_equipo.setFlags(item_equipo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_stats_partido.setItem(fila, 1, item_equipo)
            
            self.tabla_stats_partido.setItem(fila, 2, QTableWidgetItem(str(stat.get('goles', 0))))
            self.tabla_stats_partido.setItem(fila, 3, QTableWidgetItem(str(stat.get('amarillas', 0))))
            self.tabla_stats_partido.setItem(fila, 4, QTableWidgetItem(str(stat.get('rojas', 0))))
    
    def obtener_datos_formulario(self) -> dict:
        """Obtiene los datos del formulario."""
        stats = []
        for fila in range(self.tabla_stats_partido.rowCount()):
            participante_id = self.tabla_stats_partido.item(fila, 0).data(Qt.ItemDataRole.UserRole)
            stats.append({
                'participante_id': participante_id,
                'goles': int(self.tabla_stats_partido.item(fila, 2).text() or 0),
                'amarillas': int(self.tabla_stats_partido.item(fila, 3).text() or 0),
                'rojas': int(self.tabla_stats_partido.item(fila, 4).text() or 0)
            })
        
        return {
            'arbitro_nombre': self.comboArbitro.currentText(),
            'fecha_hora': self.fecha_hora.dateTime().toString("yyyy-MM-dd HH:mm"),
            'goles_local': self.goles_local.value(),
            'goles_visitante': self.goles_visitante.value(),
            'penaltis_local': self.penaltis_local.value() if self.grupo_penaltis.isEnabled() else None,
            'penaltis_visitante': self.penaltis_visitante.value() if self.grupo_penaltis.isEnabled() else None,
            'stats': stats
        }
    
    def deshabilitar_guardar_resultado(self):
        """Deshabilita el botón de guardar resultado."""
        self.guardar_resultado.setEnabled(False)
    
    def habilitar_guardar_resultado(self):
        """Habilita el botón de guardar resultado."""
        if self.modo_actual == "editar_resultado":
            self.validar_guardar_resultado()
    
    def mostrar_aviso_sin_jugadores(self, mensaje: str):
        """Muestra un aviso de que no hay jugadores."""
        pass
    
    def ocultar_aviso_sin_jugadores(self):
        """Oculta el aviso de jugadores."""
        pass
    
    def cargar_equipos_en_combos(self, equipos: list[dict]):
        """Carga los equipos en los combos Local y Visitante."""
        self.comboLocal.clear()
        self.comboLocal.addItem("-- Seleccionar equipo --", None)
        
        self.comboVisitante.clear()
        self.comboVisitante.addItem("-- Seleccionar equipo --", None)
        
        for equipo in equipos:
            self.comboLocal.addItem(equipo['nombre'], equipo['id'])
            self.comboVisitante.addItem(equipo['nombre'], equipo['id'])
        
        # Configurar QCompleter para búsqueda en combos editables
        completer_local = QCompleter([equipo['nombre'] for equipo in equipos], self.comboLocal)
        completer_local.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer_local.setFilterMode(Qt.MatchFlag.MatchContains)
        completer_local.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.comboLocal.setCompleter(completer_local)
        
        completer_visitante = QCompleter([equipo['nombre'] for equipo in equipos], self.comboVisitante)
        completer_visitante.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer_visitante.setFilterMode(Qt.MatchFlag.MatchContains)
        completer_visitante.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.comboVisitante.setCompleter(completer_visitante)
    
    def cargar_arbitros_en_combo(self, arbitros: list[str]):
        """Carga los árbitros en el combo."""
        self.comboArbitro.clear()
        self.comboArbitro.addItem("Sin árbitro", None)
        arbitros_validos = []
        for arb in arbitros:
            if arb != "Sin asignar" and arb != "Sin árbitro":
                self.comboArbitro.addItem(arb)
                arbitros_validos.append(arb)
        
        # Configurar QCompleter para búsqueda en combo editable
        if arbitros_validos:
            completer_arbitro = QCompleter(arbitros_validos, self.comboArbitro)
            completer_arbitro.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer_arbitro.setFilterMode(Qt.MatchFlag.MatchContains)
            completer_arbitro.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.comboArbitro.setCompleter(completer_arbitro)
    
    def actualizar_estado_botones(self):
        """
        Actualiza el estado de los botones Guardar/Eliminar/Cancelar según el contexto.
        
        Reglas:
        - Nuevo partido: Guardar ✅, Cancelar ✅, Eliminar ❌
        - Partido existente: Guardar ✅, Cancelar ✅, Eliminar ✅
        - Nada seleccionado: Guardar ❌, Cancelar ❌, Eliminar ❌
        """
        if self.partido_actual_id is not None:
            # Partido existente cargado
            self.btnGuardar.setEnabled(True)
            self.btnEliminar.setEnabled(True)
            self.btnCancelar.setEnabled(True)
        elif self.modo_actual in ["crear", "editar"]:
            # Nuevo partido en creación (sin ID)
            self.btnGuardar.setEnabled(True)
            self.btnEliminar.setEnabled(False)
            self.btnCancelar.setEnabled(True)
        else:
            # Modo ver o sin selección
            self.btnGuardar.setEnabled(False)
            self.btnEliminar.setEnabled(False)
            self.btnCancelar.setEnabled(False)
        
        # Actualizar convocatoria (solo habilitada si hay partido guardado)
        conv_enabled = self.partido_actual_id is not None
        if hasattr(self, 'jugadores_lista_local'):
            self.jugadores_lista_local.setEnabled(conv_enabled)
        if hasattr(self, 'jugadores_lista_visitante'):
            self.jugadores_lista_visitante.setEnabled(conv_enabled)
    
    def validar_convocatoria_minima(self) -> tuple[bool, str]:
        """
        Valida que ambos equipos tengan al menos 7 jugadores convocados (Fútbol 7).
        
        Returns:
            (bool, str): (es_valido, mensaje_error)
        """
        MIN_JUGADORES = 7
        
        # Contar convocados local
        convocados_local = 0
        if hasattr(self, 'jugadores_lista_local'):
            for i in range(self.jugadores_lista_local.count()):
                item = self.jugadores_lista_local.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    convocados_local += 1
        
        # Contar convocados visitante
        convocados_visitante = 0
        if hasattr(self, 'jugadores_lista_visitante'):
            for i in range(self.jugadores_lista_visitante.count()):
                item = self.jugadores_lista_visitante.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    convocados_visitante += 1
        
        # Validar ambos equipos
        if convocados_local < MIN_JUGADORES:
            return False, f"El equipo local debe tener al menos {MIN_JUGADORES} jugadores convocados.\nActualmente tiene: {convocados_local}"
        
        if convocados_visitante < MIN_JUGADORES:
            return False, f"El equipo visitante debe tener al menos {MIN_JUGADORES} jugadores convocados.\nActualmente tiene: {convocados_visitante}"
        
        return True, ""
    
    def set_modo(self, modo: str):
        """
        Establece el modo de operación (ver, crear, editar, editar_resultado).
        
        IMPORTANTE: Las pestañas NUNCA se bloquean. Solo se controla el estado
        de los botones de guardar según validaciones.
        """
        self.modo_actual = modo
        
        # Las pestañas siempre están habilitadas
        # El usuario puede navegar libremente
        # La validación ocurre al guardar
        
        if modo == "ver":
            # Modo solo lectura: campos deshabilitados
            self.comboFase.setEnabled(False)
            self.comboLocal.setEnabled(False)
            self.comboVisitante.setEnabled(False)
            self.fecha_hora.setEnabled(False)
            self.comboEstado.setEnabled(False)
            self.comboArbitro.setEnabled(False)
            
            # Resultado deshabilitado
            self.goles_local.setEnabled(False)
            self.goles_visitante.setEnabled(False)
            self.penaltis_local.setEnabled(False)
            self.penaltis_visitante.setEnabled(False)
            self.guardar_resultado.setEnabled(False)
            self.guardar_resultado.setVisible(False)
            self.cancelar_cambios.setEnabled(False)
            self.cancelar_cambios.setVisible(False)
            
            # Botón editar resultado visible si hay partido
            self.editar_resultado_btn.setVisible(True)
            self.editar_resultado_btn.setEnabled(bool(self.partido_actual_id))
            
            # Footer buttons
            self.btnGuardar.setEnabled(False)
            self.btnEliminar.setEnabled(bool(self.partido_actual_id))
            self.btnCancelar.setEnabled(False)
            
        elif modo in ["crear", "editar"]:
            # Modo edición de datos: tab Datos habilitado
            self.comboFase.setEnabled(True)
            self.comboLocal.setEnabled(True)
            self.comboVisitante.setEnabled(True)
            self.fecha_hora.setEnabled(True)
            self.comboEstado.setEnabled(True)
            self.comboArbitro.setEnabled(True)
            
            # Resultado deshabilitado (editar datos, no resultado)
            self.goles_local.setEnabled(False)
            self.goles_visitante.setEnabled(False)
            self.penaltis_local.setEnabled(False)
            self.penaltis_visitante.setEnabled(False)
            self.guardar_resultado.setEnabled(False)
            self.guardar_resultado.setVisible(False)
            self.cancelar_cambios.setEnabled(False)
            self.cancelar_cambios.setVisible(False)
            
            # Botón editar resultado oculto
            self.editar_resultado_btn.setVisible(False)
            
            # Footer buttons
            self.btnGuardar.setEnabled(True)  # Siempre habilitado en modo edición
            self.btnEliminar.setEnabled(modo == "editar")  # Solo en editar, no en crear
            self.btnCancelar.setEnabled(True)
            
        elif modo == "editar_resultado":
            # Modo edición de resultado: Datos deshabilitado, Resultado habilitado
            self.comboFase.setEnabled(False)
            self.comboLocal.setEnabled(False)
            self.comboVisitante.setEnabled(False)
            self.fecha_hora.setEnabled(False)
            self.comboEstado.setEnabled(False)
            self.comboArbitro.setEnabled(True)  # Árbitro sí se puede cambiar
            
            # Resultado habilitado
            self.goles_local.setEnabled(True)
            self.goles_visitante.setEnabled(True)
            
            # Penaltis solo si hay empate
            empate = (self.goles_local.value() == self.goles_visitante.value())
            self.penaltis_local.setEnabled(empate)
            self.penaltis_visitante.setEnabled(empate)
            self.grupo_penaltis.setEnabled(empate)
            
            self.guardar_resultado.setEnabled(False)  # Se habilita con puede_guardar_resultado()
            self.guardar_resultado.setVisible(True)
            self.cancelar_cambios.setEnabled(True)
            self.cancelar_cambios.setVisible(True)
            
            # Botón editar resultado oculto
            self.editar_resultado_btn.setVisible(False)
            
            # Footer buttons deshabilitados (no aplican en modo resultado)
            self.btnGuardar.setEnabled(False)
            self.btnEliminar.setEnabled(False)
            self.btnCancelar.setEnabled(False)
            
            # Validar si se puede guardar resultado
            puede_guardar, mensaje = self.puede_guardar_resultado()
            self.guardar_resultado.setEnabled(puede_guardar)
            
            if not puede_guardar and mensaje:
                # Mostrar tooltip con el motivo
                self.guardar_resultado.setToolTip(mensaje)
            else:
                self.guardar_resultado.setToolTip("Guardar el resultado del partido")
        
        # Actualizar dirty state buttons
        self.update_guardar_button_state()
    
    def limpiar_formulario_partido(self):
        """Limpia el formulario del partido."""
        self.partido_actual_id = None
        self.partido_titulo.setText("Nuevo partido")
        self.comboFase.setCurrentIndex(0)
        self.comboLocal.setCurrentIndex(0)
        self.comboVisitante.setCurrentIndex(0)
        self.fecha_hora.setDateTime(QDateTime.currentDateTime())
        self.comboEstado.setCurrentIndex(0)
        self.comboArbitro.setCurrentIndex(0)
        
        # Mostrar label informativo
        self.label_info_convocatoria.setVisible(True)
        
        # Limpiar convocatoria (nueva estructura con listas)
        self.equipo_local_label.setText("Equipo: -")
        self.equipo_visitante_label.setText("Equipo: -")
        if hasattr(self, 'jugadores_lista_local'):
            self.jugadores_lista_local.clear()
            self.contador_local_label.setText("Convocados: 0 / 0")
        if hasattr(self, 'jugadores_lista_visitante'):
            self.jugadores_lista_visitante.clear()
            self.contador_visitante_label.setText("Convocados: 0 / 0")
        
        # Limpiar resultado
        self.goles_local.setValue(0)
        self.goles_visitante.setValue(0)
        self.penaltis_local.setValue(0)
        self.penaltis_visitante.setValue(0)
        self.tabla_stats_partido.setRowCount(0)
        
        # Actualizar estado de botones
        self.actualizar_estado_botones()
    
    def obtener_datos_partido(self) -> dict:
        """Obtiene los datos del partido desde el formulario."""
        # Para el árbitro, necesitamos obtener tanto el texto como el userData
        arbitro_text = self.comboArbitro.currentText()
        arbitro_id = self.comboArbitro.currentData()
        
        # Si el combo no tiene userData configurado, intentar buscar por texto
        if arbitro_id is None and arbitro_text != "Sin árbitro":
            # El árbitro fue cargado sin userData, necesitamos buscarlo
            # En este caso, lo dejamos None y el controlador lo resolverá
            arbitro_id = None
        
        return {
            'ronda': self.comboFase.currentData(),  # Devuelve fase_id (octavos, cuartos, etc.)
            'local_id': self.comboLocal.currentData(),
            'visitante_id': self.comboVisitante.currentData(),
            'fecha_hora': self.fecha_hora.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            'estado': self.comboEstado.currentText(),
            'arbitro_id': arbitro_id,
            'arbitro_nombre': arbitro_text
        }


# Alias para mantener compatibilidad con código existente
PageMatches = PageCalendarioPartidos
