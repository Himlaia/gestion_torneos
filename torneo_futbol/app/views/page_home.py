"""Página de inicio con selector visual de secciones."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QIcon
from app.views.widgets import CardWidget


class PageInicio(QWidget):
    """Página de inicio con acceso visual a todas las secciones."""
    
    # Señales personalizadas
    ir_a_equipos_signal = Signal()
    ir_a_participantes_signal = Signal()
    ir_a_partidos_signal = Signal()
    ir_a_cuadro_signal = Signal()
    ir_a_ayuda_signal = Signal()
    ir_a_creditos_signal = Signal()
    
    def __init__(self):
        """Inicializa la página de inicio."""
        super().__init__()
        self.imagenes_fondo = {}
        self.current_columns = 2  # Columnas actuales del grid
        self.grid_layout = None
        self.cards = []
        self._resizing = False  # Guard para evitar recursión en resize
        self.setup_ui()
        self.conectar_senales()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Layout principal (contenedor del scroll)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Crear QScrollArea con transparencia para ver el fondo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_area.viewport().setStyleSheet("background: transparent;")
        
        # Widget contenedor interno del scroll con transparencia
        scroll_content = QWidget()
        scroll_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        scroll_content.setStyleSheet("background: transparent;")
        
        # Layout del contenido scrolleable
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(40, 20, 40, 40)
        content_layout.setSpacing(10)
        
        # Título principal
        self.crear_titulo(content_layout)
        
        # Contenedor central para el grid (con tamaño controlado)
        self.panel_central = QWidget()
        self.panel_central.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.panel_central.setStyleSheet("background: transparent;")
        panel_layout = QVBoxLayout(self.panel_central)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # Grid de botones tipo card
        self.crear_grid_botones(panel_layout)
        
        content_layout.addWidget(self.panel_central)
        
        # Pequeño espaciador inferior (reducido)
        content_layout.addSpacing(20)
        
        # Asignar el contenido al scroll
        scroll_area.setWidget(scroll_content)
        
        # Añadir scroll al layout principal
        main_layout.addWidget(scroll_area)
    
    def crear_titulo(self, layout_padre: QVBoxLayout):
        """Crea el título principal de la página."""
        self.titulo = QLabel(self.tr("Gestión de torneos"))
        self.titulo.setObjectName("homeTitleLabel")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_padre.addWidget(self.titulo)
    
    def crear_grid_botones(self, layout_padre: QVBoxLayout):
        """Crea el grid de botones tipo card usando CardWidget."""
        # Grid 2x3 para las tarjetas
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(18)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        
        # Información de botones: (titulo, descripcion, icono_unicode)
        self.botones_info = [
            (self.tr("Equipos"), self.tr("Gestiona los equipos del torneo"), "⚽"),
            (self.tr("Participantes"), self.tr("Administra jugadores y árbitros"), "👥"),
            (self.tr("Calendario / Partidos"), self.tr("Programa y gestiona los partidos"), "📅"),
            (self.tr("Cuadro de eliminatorias"), self.tr("Visualiza el cuadro del torneo"), "🏆"),
            (self.tr("Ayuda"), self.tr("Consulta la documentación"), "❓"),
            (self.tr("Créditos"), self.tr("Información del proyecto"), "ℹ️")
        ]
        
        # Crear tarjetas
        self.cards = []
        for idx, (titulo, descripcion, icono) in enumerate(self.botones_info):
            card = CardWidget(titulo, descripcion, icono, theme="light")
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            card.setMinimumHeight(140)
            self.cards.append(card)
        
        # Añadir tarjetas al grid inicialmente en 2 columnas
        self.relayout_cards(2)
        
        # Referencias para mantener compatibilidad
        self.boton_equipos = self.cards[0]
        self.boton_participantes = self.cards[1]
        self.boton_partidos = self.cards[2]
        self.boton_cuadro = self.cards[3]
        self.boton_ayuda = self.cards[4]
        self.boton_creditos = self.cards[5]
        
        layout_padre.addLayout(self.grid_layout)
    
    def actualizar_tema_cards(self, theme: str):
        """
        Actualiza el tema de todas las tarjetas.
        
        Args:
            theme: 'light' o 'dark'
        """
        if hasattr(self, 'cards'):
            for card in self.cards:
                card.set_theme(theme)
    
    def relayout_cards(self, columns: int):
        """
        Reorganiza las tarjetas en el grid según el número de columnas.
        
        Args:
            columns: Número de columnas (1 o 2)
        """
        # Limpiar el grid actual
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Reinsertar tarjetas con nueva distribución
        for idx, card in enumerate(self.cards):
            if columns == 1:
                # 1 columna x 6 filas
                row = idx
                col = 0
            else:
                # 2 columnas x 3 filas
                row = idx // 2
                col = idx % 2
            
            self.grid_layout.addWidget(card, row, col)
        
        # Actualizar stretches de columnas
        if columns == 1:
            self.grid_layout.setColumnStretch(0, 1)
            self.grid_layout.setColumnStretch(1, 0)
        else:
            self.grid_layout.setColumnStretch(0, 1)
            self.grid_layout.setColumnStretch(1, 1)
        
        self.current_columns = columns
    
    def resizeEvent(self, event):
        """Maneja el redimensionamiento para hacer el layout responsive."""
        super().resizeEvent(event)
        
        # Evitar recursión durante el resize
        if self._resizing:
            return
        
        self._resizing = True
        try:
            # Breakpoint: cambiar a 1 columna si el ancho es menor a 900px
            ancho_disponible = self.width()
            
            if ancho_disponible < 900 and self.current_columns != 1:
                self.relayout_cards(1)
            elif ancho_disponible >= 900 and self.current_columns != 2:
                self.relayout_cards(2)
        finally:
            self._resizing = False
    
    def conectar_senales(self):
        """Conecta las señales de las tarjetas."""
        self.boton_equipos.clicked.connect(self.ir_a_equipos_signal.emit)
        self.boton_participantes.clicked.connect(self.ir_a_participantes_signal.emit)
        self.boton_partidos.clicked.connect(self.ir_a_partidos_signal.emit)
        self.boton_cuadro.clicked.connect(self.ir_a_cuadro_signal.emit)
        self.boton_ayuda.clicked.connect(self.ir_a_ayuda_signal.emit)
        self.boton_creditos.clicked.connect(self.ir_a_creditos_signal.emit)
    
    def set_imagenes(self, imagenes: dict[str, str]):
        """
        Establece imágenes de fondo para los botones.
        
        Args:
            imagenes: Diccionario con claves "equipos", "participantes", "partidos",
                     "cuadro", "ayuda", "creditos" y valores con rutas a imágenes.
        """
        self.imagenes_fondo = imagenes
        
        # Mapeo de claves a botones
        mapeo_botones = {
            "equipos": self.boton_equipos,
            "participantes": self.boton_participantes,
            "partidos": self.boton_partidos,
            "cuadro": self.boton_cuadro,
            "ayuda": self.boton_ayuda,
            "creditos": self.boton_creditos
        }
        
        # Aplicar imagen de fondo a cada botón
        for clave, boton in mapeo_botones.items():
            ruta_imagen = imagenes.get(clave)
            if ruta_imagen:
                self._aplicar_imagen_fondo(boton, ruta_imagen)
    
    def _aplicar_imagen_fondo(self, boton: QPushButton, ruta_imagen: str):
        """
        Aplica una imagen de fondo a un botón manteniendo el estilo base.
        
        Args:
            boton: Botón al que aplicar la imagen
            ruta_imagen: Ruta a la imagen de fondo
        """
        # Obtener el texto actual para preservarlo
        texto = boton.text()
        
        # Estilo con imagen de fondo y overlay oscuro para legibilidad
        estilo_con_imagen = f"""
            QPushButton#cardButton {{
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: rgba(52, 73, 94, 0.85);
                background-image: 
                    linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
                    url({ruta_imagen});
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
                border: 2px solid #2c3e50;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            }}
            QPushButton#cardButton:hover {{
                background-color: rgba(41, 128, 185, 0.95);
                background-image: 
                    linear-gradient(rgba(41, 128, 185, 0.6), rgba(41, 128, 185, 0.6)),
                    url({ruta_imagen});
                border: 2px solid #1f618d;
            }}
            QPushButton#cardButton:pressed {{
                background-color: rgba(31, 97, 141, 0.95);
                background-image: 
                    linear-gradient(rgba(31, 97, 141, 0.7), rgba(31, 97, 141, 0.7)),
                    url({ruta_imagen});
                border: 2px solid #154360;
            }}
        """
        boton.setStyleSheet(estilo_con_imagen)
    
    def set_imagen_boton(self, nombre_boton: str, ruta_imagen: str):
        """
        Establece la imagen de fondo para un botón específico.
        
        Args:
            nombre_boton: Nombre del botón ("equipos", "participantes", etc.)
            ruta_imagen: Ruta a la imagen de fondo
        """
        mapeo_botones = {
            "equipos": self.boton_equipos,
            "participantes": self.boton_participantes,
            "partidos": self.boton_partidos,
            "cuadro": self.boton_cuadro,
            "ayuda": self.boton_ayuda,
            "creditos": self.boton_creditos
        }
        
        boton = mapeo_botones.get(nombre_boton)
        if boton:
            self._aplicar_imagen_fondo(boton, ruta_imagen)
            self.imagenes_fondo[nombre_boton] = ruta_imagen
    
    def changeEvent(self, event):
        """Maneja eventos de cambio, incluyendo cambio de idioma."""
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
    
    def retranslate_ui(self):
        """Actualiza todos los textos traducibles de la interfaz."""
        self.titulo.setText(self.tr("Gestión de torneos"))
        
        # Actualizar textos de las tarjetas
        traducciones = [
            (self.tr("Equipos"), self.tr("Gestiona los equipos del torneo")),
            (self.tr("Participantes"), self.tr("Administra jugadores y árbitros")),
            (self.tr("Calendario / Partidos"), self.tr("Programa y gestiona los partidos")),
            (self.tr("Cuadro de eliminatorias"), self.tr("Visualiza el cuadro del torneo")),
            (self.tr("Ayuda"), self.tr("Consulta la documentación")),
            (self.tr("Créditos"), self.tr("Información del proyecto"))
        ]
        
        for i, (titulo, descripcion) in enumerate(traducciones):
            if i < len(self.cards):
                self.cards[i].set_texts(titulo, descripcion)
