"""Página de gestión de equipos."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QSplitter,
    QGroupBox, QHeaderView, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize, QEvent
from PySide6.QtGui import QPixmap, QIcon, QPainter
from PySide6.QtSvg import QSvgRenderer
from pathlib import Path
from typing import Optional

from app.config import DATA_DIR


class PageGestionEquipos(QWidget):
    """Página para la gestión de equipos."""
    
    # Señales personalizadas
    nuevo_equipo_signal = Signal()
    editar_equipo_signal = Signal()
    eliminar_equipo_signal = Signal()
    seleccionar_escudo_signal = Signal()
    guardar_equipo_signal = Signal()
    cancelar_edicion_signal = Signal()
    buscar_equipo_changed_signal = Signal(str)
    equipo_seleccionado_signal = Signal(dict)
    ver_jugadores_equipo_signal = Signal(int, str)  # id_equipo, nombre_equipo
    
    def __init__(self):
        """Inicializa la página de equipos."""
        super().__init__()
        self.modo_actual = "ver"
        self.pixmap_original = None  # Guarda el pixmap original para reescalar
        self.setup_ui()
        self.conectar_senales()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Establecer objectName para el widget raíz
        self.setObjectName("pageRoot")
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 4, 20, 12)
        layout_principal.setSpacing(8)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Título
        self.crear_titulo(layout_principal)
        
        # Contenedor de contenido (card)
        content_card = QFrame()
        content_card.setObjectName("contentCard")
        content_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        # Barra de acciones
        self.crear_barra_acciones(card_layout)
        
        # Zona central con splitter
        self.crear_zona_central(card_layout)
        
        layout_principal.addWidget(content_card)
        
        self.setLayout(layout_principal)
    
    def crear_titulo(self, layout_padre: QVBoxLayout):
        """Crea el título de la página."""
        self.titulo = QLabel(self.tr("Gestión de equipos"))
        self.titulo.setObjectName("titleLabel")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_padre.addWidget(self.titulo)
    
    def crear_barra_acciones(self, layout_padre: QVBoxLayout):
        """Crea la barra de acciones con búsqueda y botones."""
        layout_acciones = QHBoxLayout()
        layout_acciones.setSpacing(10)
        
        # Campo de búsqueda
        self.buscar_equipo = QLineEdit()
        self.buscar_equipo.setPlaceholderText("Buscar equipo…")
        self.buscar_equipo.setMinimumWidth(250)
        layout_acciones.addWidget(self.buscar_equipo)
        
        layout_acciones.addStretch()
        
        # Botones de acción
        self.nuevo_equipo = QPushButton("Nuevo equipo")
        self.editar_equipo = QPushButton("Editar equipo")
        self.eliminar_equipo = QPushButton("Eliminar equipo")
        self.eliminar_equipo.setObjectName("dangerButton")
        
        layout_acciones.addWidget(self.nuevo_equipo)
        layout_acciones.addWidget(self.editar_equipo)
        layout_acciones.addWidget(self.eliminar_equipo)
        
        layout_padre.addLayout(layout_acciones)
    
    def crear_zona_central(self, layout_padre: QVBoxLayout):
        """Crea la zona central con splitter (tabla + detalle)."""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Ocultar el handle del splitter para eliminar barra visible
        splitter.setHandleWidth(0)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: transparent;
                width: 0px;
            }
        """)
        
        # Panel izquierdo: tabla de equipos
        self.crear_panel_tabla(splitter)
        
        # Panel derecho: detalle del equipo
        self.crear_panel_detalle(splitter)
        
        # Configurar proporciones del splitter
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout_padre.addWidget(splitter, 1)  # stretch factor 1 para ocupar espacio restante
    
    def crear_panel_tabla(self, splitter: QSplitter):
        """Crea el panel con la tabla de equipos."""
        widget_tabla = QWidget()
        layout_tabla = QVBoxLayout()
        layout_tabla.setContentsMargins(0, 0, 10, 0)
        
        # Tabla de equipos
        self.tabla_equipos = QTableWidget()
        self.tabla_equipos.setColumnCount(4)
        self.tabla_equipos.setHorizontalHeaderLabels([
            "Nombre", "Colores", "Escudo", "Nº jugadores"
        ])
        
        # Configurar tabla
        self.tabla_equipos.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_equipos.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.tabla_equipos.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        
        # Estirar columnas
        header = self.tabla_equipos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Configurar tamaño de iconos y altura de filas para escudos
        self.tabla_equipos.setIconSize(QSize(32, 32))
        self.tabla_equipos.verticalHeader().setDefaultSectionSize(40)
        
        layout_tabla.addWidget(self.tabla_equipos)
        widget_tabla.setLayout(layout_tabla)
        splitter.addWidget(widget_tabla)
    
    def crear_panel_detalle(self, splitter: QSplitter):
        """Crea el panel de detalle del equipo."""
        self.grupo_detalle = QGroupBox("Detalle del equipo")
        layout_detalle = QVBoxLayout()
        layout_detalle.setSpacing(10)
        
        # Nombre del equipo
        layout_nombre = QVBoxLayout()
        layout_nombre.setSpacing(5)
        self.label_nombre = QLabel("Nombre:")
        self.nombre_equipo = QLineEdit()
        self.nombre_equipo.setPlaceholderText("Nombre del equipo")
        layout_nombre.addWidget(self.label_nombre)
        layout_nombre.addWidget(self.nombre_equipo)
        layout_detalle.addLayout(layout_nombre)
        
        # Colores del equipo
        layout_colores = QVBoxLayout()
        layout_colores.setSpacing(5)
        self.label_colores = QLabel("Colores:")
        self.colores_equipo = QLineEdit()
        self.colores_equipo.setPlaceholderText("Ej: Rojo y blanco")
        layout_colores.addWidget(self.label_colores)
        layout_colores.addWidget(self.colores_equipo)
        layout_detalle.addLayout(layout_colores)
        
        # Escudo del equipo
        layout_escudo = QVBoxLayout()
        layout_escudo.setSpacing(5)
        self.label_escudo = QLabel("Escudo:")
        
        # Preview del escudo
        self.preview_escudo = QLabel("Sin escudo")
        self.preview_escudo.setObjectName("previewEscudo")
        self.preview_escudo.setFixedSize(144, 144)
        self.preview_escudo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_escudo.setStyleSheet(
            "border: 2px solid #bdc3c7; "
            "background-color: #ecf0f1; "
            "border-radius: 4px;"
        )
        self.preview_escudo.setScaledContents(False)
        self.preview_escudo.setProperty("empty", True)
        
        # Botón de escudo
        self.seleccionar_escudo = QPushButton("Seleccionar escudo")
        
        layout_escudo.addWidget(self.label_escudo)
        layout_escudo.addWidget(self.preview_escudo)
        layout_escudo.addWidget(self.seleccionar_escudo)
        layout_detalle.addLayout(layout_escudo)
        
        # Botones inferiores
        layout_botones = QHBoxLayout()
        self.guardar_equipo = QPushButton("Guardar equipo")
        self.guardar_equipo.setObjectName("successButton")
        self.cancelar_edicion = QPushButton("Cancelar")
        
        layout_botones.addWidget(self.guardar_equipo)
        layout_botones.addWidget(self.cancelar_edicion)
        layout_detalle.addLayout(layout_botones)
        
        layout_detalle.addStretch()
        
        self.grupo_detalle.setLayout(layout_detalle)
        splitter.addWidget(self.grupo_detalle)
    
    def conectar_senales(self):
        """Conecta las señales de los widgets."""
        # Botones de acción
        self.nuevo_equipo.clicked.connect(self.nuevo_equipo_signal.emit)
        self.editar_equipo.clicked.connect(self.editar_equipo_signal.emit)
        self.eliminar_equipo.clicked.connect(self.eliminar_equipo_signal.emit)
        
        # Botón de escudo
        self.seleccionar_escudo.clicked.connect(self.seleccionar_escudo_signal.emit)
        
        # Botones de formulario
        self.guardar_equipo.clicked.connect(self.guardar_equipo_signal.emit)
        self.cancelar_edicion.clicked.connect(self.cancelar_edicion_signal.emit)
        
        # Búsqueda
        self.buscar_equipo.textChanged.connect(
            self.buscar_equipo_changed_signal.emit
        )
        
        # Selección en tabla
        self.tabla_equipos.itemSelectionChanged.connect(
            self.on_seleccion_tabla_changed
        )
        
        # Doble clic en tabla para ver jugadores
        self.tabla_equipos.cellDoubleClicked.connect(
            self.on_doble_clic_tabla
        )
    
    def on_seleccion_tabla_changed(self):
        """Maneja el cambio de selección en la tabla."""
        fila_seleccionada = self.tabla_equipos.currentRow()
        if fila_seleccionada >= 0:
            datos = self.obtener_datos_fila(fila_seleccionada)
            self.equipo_seleccionado_signal.emit(datos)
    
    def on_doble_clic_tabla(self, fila: int, columna: int):
        """
        Maneja el doble clic en la tabla para mostrar jugadores del equipo.
        
        Args:
            fila: Fila donde se hizo doble clic
            columna: Columna donde se hizo doble clic
        """
        datos = self.obtener_datos_fila(fila)
        id_equipo = datos.get('id')
        nombre_equipo = datos.get('nombre', 'Equipo')
        
        if id_equipo:
            self.ver_jugadores_equipo_signal.emit(id_equipo, nombre_equipo)
    
    def obtener_datos_fila(self, fila: int) -> dict:
        """
        Obtiene los datos de una fila de la tabla.
        
        Args:
            fila: Índice de la fila
            
        Returns:
            Diccionario con los datos de la fila
        """
        datos = {}
        if fila >= 0 and fila < self.tabla_equipos.rowCount():
            # Obtener el item de nombre que contiene el ID en UserRole
            item_nombre = self.tabla_equipos.item(fila, 0)
            datos['id'] = item_nombre.data(Qt.ItemDataRole.UserRole) if item_nombre else None
            datos['nombre'] = item_nombre.text() if item_nombre else ''
            datos['colores'] = self.tabla_equipos.item(fila, 1).text()
            # Leer la ruta del escudo desde UserRole
            item_escudo = self.tabla_equipos.item(fila, 2)
            datos['escudo'] = item_escudo.data(Qt.ItemDataRole.UserRole) if item_escudo else ''
            datos['num_jugadores'] = self.tabla_equipos.item(fila, 3).text()
        return datos
    
    # ========== Métodos públicos obligatorios ==========
    
    def set_filas_tabla(self, equipos: list[dict]):
        """
        Establece las filas de la tabla con los datos de equipos.
        
        Args:
            equipos: Lista de diccionarios con datos de equipos
        """
        self.tabla_equipos.setRowCount(0)
        
        for equipo in equipos:
            fila = self.tabla_equipos.rowCount()
            self.tabla_equipos.insertRow(fila)
            
            # Columna nombre - Guardar ID en UserRole
            item_nombre = QTableWidgetItem(str(equipo.get('nombre', '')))
            item_nombre.setData(Qt.ItemDataRole.UserRole, equipo.get('id'))
            self.tabla_equipos.setItem(fila, 0, item_nombre)
            
            self.tabla_equipos.setItem(
                fila, 1, QTableWidgetItem(str(equipo.get('colores', '')))
            )
            
            # Columna de escudo: mostrar icono en lugar de texto
            ruta_escudo = equipo.get('escudo', '')
            item_escudo = QTableWidgetItem()
            
            # Guardar la ruta en UserRole para recuperarla después
            item_escudo.setData(Qt.ItemDataRole.UserRole, ruta_escudo)
            
            if ruta_escudo and ruta_escudo != 'Sin escudo':
                # Construir ruta absoluta
                ruta = Path(ruta_escudo)
                if not ruta.is_absolute():
                    ruta_proyecto = Path(__file__).resolve().parent.parent.parent
                    ruta = ruta_proyecto / ruta_escudo
                
                # Cargar icono si el archivo existe
                if ruta.exists():
                    item_escudo.setIcon(QIcon(str(ruta)))
                else:
                    # Sin icono si no existe el archivo
                    item_escudo.setText("—")
            else:
                # Sin escudo
                item_escudo.setText("—")
            
            # Centrar el contenido de la celda
            item_escudo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_equipos.setItem(fila, 2, item_escudo)
            
            self.tabla_equipos.setItem(
                fila, 3, QTableWidgetItem(str(equipo.get('num_jugadores', '0')))
            )
    
    def get_datos_formulario(self) -> dict:
        """
        Obtiene los datos del formulario de detalle.
        
        Returns:
            Diccionario con los datos del formulario
        """
        # El escudo se maneja por separado en el controlador vía escudo_temporal
        return {
            'nombre': self.nombre_equipo.text().strip(),
            'colores': self.colores_equipo.text().strip(),
            'escudo': ''  # No se lee de aquí, se gestiona en el controlador
        }
    
    def set_datos_formulario(self, datos: dict):
        """
        Establece los datos en el formulario de detalle.
        
        Args:
            datos: Diccionario con los datos a mostrar
        """
        self.nombre_equipo.setText(datos.get('nombre', ''))
        self.colores_equipo.setText(datos.get('colores', ''))
        
        escudo = datos.get('escudo', '')
        self.cargar_escudo(escudo)
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.nombre_equipo.clear()
        self.colores_equipo.clear()
        self.cargar_escudo('')
        self.tabla_equipos.clearSelection()
    
    def set_modo(self, modo: str):
        """
        Establece el modo de operación del formulario.
        
        Args:
            modo: Modo de operación ('ver', 'crear', 'editar')
        """
        self.modo_actual = modo
        
        if modo == "ver":
            # Modo lectura
            self.nombre_equipo.setReadOnly(True)
            self.colores_equipo.setReadOnly(True)
            self.seleccionar_escudo.setEnabled(False)
            self.guardar_equipo.setEnabled(False)
            self.cancelar_edicion.setEnabled(False)
            
            # Habilitar botones de acción
            self.nuevo_equipo.setEnabled(True)
            self.editar_equipo.setEnabled(True)
            self.eliminar_equipo.setEnabled(True)
            
        elif modo in ["crear", "editar"]:
            # Modo edición
            self.nombre_equipo.setReadOnly(False)
            self.colores_equipo.setReadOnly(False)
            self.seleccionar_escudo.setEnabled(True)
            self.guardar_equipo.setEnabled(True)
            self.cancelar_edicion.setEnabled(True)
            
            # Deshabilitar botones de acción
            self.nuevo_equipo.setEnabled(False)
            self.editar_equipo.setEnabled(False)
            self.eliminar_equipo.setEnabled(False)
    
    def cargar_escudo(self, ruta_escudo: str):
        """
        Carga y muestra una imagen de escudo en el preview.
        
        Args:
            ruta_escudo: Ruta del archivo de imagen (relativa o absoluta)
        """
        if not ruta_escudo or ruta_escudo == 'Sin escudo':
            self.pixmap_original = None
            self.preview_escudo.clear()
            self.preview_escudo.setText("Sin\nescudo")
            self.preview_escudo.setProperty("empty", True)
            self.preview_escudo.style().unpolish(self.preview_escudo)
            self.preview_escudo.style().polish(self.preview_escudo)
            return
        
        # Construir ruta absoluta si es relativa
        ruta = Path(ruta_escudo)
        if not ruta.is_absolute():
            # Usar DATA_DIR como base para rutas relativas
            ruta = DATA_DIR.parent / ruta_escudo
        
        # Verificar si el archivo existe
        if not ruta.exists():
            self.pixmap_original = None
            self.preview_escudo.clear()
            self.preview_escudo.setText("No\nencontrado")
            self.preview_escudo.setProperty("empty", True)
            self.preview_escudo.style().unpolish(self.preview_escudo)
            self.preview_escudo.style().polish(self.preview_escudo)
            return
        
        if ruta.suffix.lower() == '.svg':
            renderer = QSvgRenderer(str(ruta))
            if not renderer.isValid():
                self.pixmap_original = None
                self.preview_escudo.clear()
                self.preview_escudo.setText("Error")
                self.preview_escudo.setProperty("empty", True)
                self.preview_escudo.style().unpolish(self.preview_escudo)
                self.preview_escudo.style().polish(self.preview_escudo)
                return
            
            self.pixmap_original = QPixmap(144, 144)
            self.pixmap_original.fill(Qt.GlobalColor.transparent)
            painter = QPainter(self.pixmap_original)
            renderer.render(painter)
            painter.end()
        else:
            self.pixmap_original = QPixmap(str(ruta))
            
            if self.pixmap_original.isNull():
                self.pixmap_original = None
                self.preview_escudo.clear()
                self.preview_escudo.setText("Error")
                self.preview_escudo.setProperty("empty", True)
                self.preview_escudo.style().unpolish(self.preview_escudo)
                self.preview_escudo.style().polish(self.preview_escudo)
                return
        
        self._actualizar_escudo_escalado()
    
    def _actualizar_escudo_escalado(self):
        """Escala el pixmap al tamaño del preview manteniendo proporción."""
        if self.pixmap_original is None or self.pixmap_original.isNull():
            return
        
        pixmap_escalado = self.pixmap_original.scaled(
            self.preview_escudo.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_escudo.clear()
        self.preview_escudo.setPixmap(pixmap_escalado)
        self.preview_escudo.setProperty("empty", False)
        self.preview_escudo.style().unpolish(self.preview_escudo)
        self.preview_escudo.style().polish(self.preview_escudo)
    
    def changeEvent(self, event):
        """Maneja eventos de cambio, incluyendo cambio de idioma."""
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
    
    def retranslate_ui(self):
        """Actualiza todos los textos traducibles de la interfaz."""
        # Título principal
        self.titulo.setText(self.tr("Gestión de equipos"))
        
        # Barra de búsqueda y botones de acción
        self.buscar_equipo.setPlaceholderText(self.tr("Buscar equipo…"))
        self.nuevo_equipo.setText(self.tr("Nuevo equipo"))
        self.editar_equipo.setText(self.tr("Editar equipo"))
        self.eliminar_equipo.setText(self.tr("Eliminar equipo"))
        
        # Headers de tabla
        self.tabla_equipos.setHorizontalHeaderLabels([
            self.tr("Nombre"), 
            self.tr("Colores"), 
            self.tr("Escudo"), 
            self.tr("Nº jugadores")
        ])
        
        # Panel de detalle
        self.grupo_detalle.setTitle(self.tr("Detalle del equipo"))
        self.label_nombre.setText(self.tr("Nombre:"))
        self.nombre_equipo.setPlaceholderText(self.tr("Nombre del equipo"))
        self.label_colores.setText(self.tr("Colores:"))
        self.colores_equipo.setPlaceholderText(self.tr("Ej: Rojo y blanco"))
        self.label_escudo.setText(self.tr("Escudo:"))
        if self.preview_escudo.property("empty"):
            self.preview_escudo.setText(self.tr("Sin escudo"))
        self.seleccionar_escudo.setText(self.tr("Seleccionar escudo"))
        self.guardar_equipo.setText(self.tr("Guardar equipo"))
        self.cancelar_edicion.setText(self.tr("Cancelar"))
    
    def resizeEvent(self, event):
        """Sobrescribe el evento de redimensionar para reescalar el escudo."""
        super().resizeEvent(event)
        if self.pixmap_original is not None:
            self._actualizar_escudo_escalado()


# Alias para mantener compatibilidad con código existente
PageTeams = PageGestionEquipos
