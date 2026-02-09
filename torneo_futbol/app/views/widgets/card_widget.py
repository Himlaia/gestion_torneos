"""Widget de tarjeta con bordes redondeados reales y clipping correcto."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QFontMetrics


class CardWidget(QWidget):
    """Tarjeta clicable con bordes redondeados reales mediante paintEvent."""
    
    clicked = Signal()
    
    def __init__(
        self,
        titulo: str,
        descripcion: str,
        icono: str,
        theme: str = "light",
        parent=None
    ):
        """
        Inicializa la tarjeta.
        
        Args:
            titulo: Texto del título
            descripcion: Texto de la descripción
            icono: Emoji/carácter unicode del icono
            theme: Tema actual ('light' o 'dark')
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.titulo_text = titulo
        self.descripcion_text = descripcion
        self.icono_text = icono
        self.theme = theme
        self.is_hovered = False
        self.is_pressed = False
        self.border_radius = 10
        
        # Configurar widget para transparencia y clipping
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Configurar tamaños y size policy
        self.setMinimumSize(280, 140)
        self.setMinimumHeight(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Layout principal con márgenes para el contenido
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Label del icono (tamaño fijo)
        self.icon_label = QLabel(self.icono_text)
        self.icon_label.setFixedSize(56, 56)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.icon_label.setStyleSheet(
            f"font-size: 36pt; "
            f"color: #16a085; "
            f"background-color: transparent; "
            f"padding: 0px; "
            f"margin: 0px;"
        )
        
        main_layout.addWidget(self.icon_label)
        
        # Bloque de texto (título + descripción)
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        # Stretch superior para centrado vertical
        text_layout.addStretch(1)
        
        # Título
        self.title_label = QLabel(self.titulo_text)
        self.title_label.setWordWrap(False)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._update_title_style()
        text_layout.addWidget(self.title_label)
        
        # Descripción
        self.desc_label = QLabel(self.descripcion_text)
        self.desc_label.setWordWrap(True)
        self.desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._update_desc_style()
        text_layout.addWidget(self.desc_label)
        
        # Stretch inferior para centrado vertical
        text_layout.addStretch(1)
        
        main_layout.addLayout(text_layout, 1)
    
    def _update_title_style(self):
        """Actualiza el estilo del título según el tema."""
        color = "#1f2a2e" if self.theme == "light" else "#f2f2f2"
        self.title_label.setStyleSheet(
            f"font-family: 'Poppins', 'Segoe UI', Arial, sans-serif; "
            f"font-size: 16pt; "
            f"font-weight: 600; "
            f"color: {color}; "
            f"background-color: transparent; "
            f"padding: 0px; "
            f"margin: 0px; "
            f"line-height: 1.2;"
        )
    
    def _update_desc_style(self):
        """Actualiza el estilo de la descripción según el tema."""
        color = "#5a6c7d" if self.theme == "light" else "#b0b0b0"
        self.desc_label.setStyleSheet(
            f"font-size: 11pt; "
            f"font-weight: 400; "
            f"color: {color}; "
            f"background-color: transparent; "
            f"padding: 0px; "
            f"margin: 0px; "
            f"line-height: 1.4;"
        )
    
    def set_theme(self, theme: str):
        """
        Actualiza el tema de la tarjeta.
        
        Args:
            theme: 'light' o 'dark'
        """
        self.theme = theme
        self._update_title_style()
        self._update_desc_style()
        self.update()
    
    def set_texts(self, titulo: str, descripcion: str):
        """
        Actualiza los textos de la tarjeta.
        
        Args:
            titulo: Nuevo texto del título
            descripcion: Nuevo texto de la descripción
        """
        self.titulo_text = titulo
        self.descripcion_text = descripcion
        self.title_label.setText(titulo)
        self.desc_label.setText(descripcion)
    
    def paintEvent(self, event):
        """Dibuja la tarjeta con bordes redondeados y clipping real."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Crear path con bordes redondeados
        path = QPainterPath()
        rect = QRect(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, self.border_radius, self.border_radius)
        
        # Aplicar clipping
        painter.setClipPath(path)
        
        # Determinar colores según estado y tema
        if self.theme == "light":
            if self.is_pressed:
                bg_color = QColor(250, 248, 235, int(0.88 * 255))
                border_color = QColor(19, 141, 117, int(0.7 * 255))
            elif self.is_hovered:
                bg_color = QColor(255, 253, 240, int(0.95 * 255))
                border_color = QColor(22, 160, 133, int(0.6 * 255))
            else:
                bg_color = QColor(255, 253, 240, int(0.88 * 255))
                border_color = QColor(180, 160, 90, int(0.45 * 255))
        else:  # dark theme
            if self.is_pressed:
                bg_color = QColor(30, 45, 35, int(0.88 * 255))
                border_color = QColor(19, 141, 117, int(0.8 * 255))
            elif self.is_hovered:
                bg_color = QColor(40, 55, 45, int(0.92 * 255))
                border_color = QColor(22, 160, 133, int(0.7 * 255))
            else:
                bg_color = QColor(35, 50, 40, int(0.88 * 255))
                border_color = QColor(80, 120, 90, int(0.5 * 255))
        
        # Dibujar fondo
        painter.fillPath(path, bg_color)
        
        # Dibujar borde
        pen = QPen(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)
    
    def mousePressEvent(self, event):
        """Maneja el evento de click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = True
            self.update()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Maneja el evento de release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = False
            if self.rect().contains(event.pos()):
                self.clicked.emit()
            self.update()
        super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        """Maneja el evento de hover."""
        self.is_hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Maneja el evento de salida del hover."""
        self.is_hovered = False
        self.is_pressed = False
        self.update()
        super().leaveEvent(event)
