"""Widget de fondo con césped escalado y overlay para tema oscuro."""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QPainterPath
from pathlib import Path
from app.config import RESOURCES_DIR
from app.constants import THEME_DARK


class BackgroundWidget(QWidget):
    """Widget que pinta un fondo de césped escalado tipo 'cover' con overlay opcional."""
    
    def __init__(self, parent=None):
        """
        Inicializa el widget de fondo.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.current_theme = None
        self.pixmap = None
        
        # Cargar imagen de césped
        img_path = RESOURCES_DIR / "img" / "cesped.jpg"
        if img_path.exists():
            try:
                self.pixmap = QPixmap(str(img_path))
            except KeyboardInterrupt:
                # Bug conocido en PySide6/Windows: QPixmap puede lanzar KeyboardInterrupt espurio
                # Reintentar la carga
                self.pixmap = QPixmap(str(img_path))
        
        # Establecer como fondo (detrás de otros widgets)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
    
    def set_theme(self, theme: str):
        """
        Establece el tema actual para el overlay.
        
        Args:
            theme: 'light' o 'dark'
        """
        self.current_theme = theme
        self.update()
    
    def paintEvent(self, event):
        """
        Pinta el fondo escalado con overlay según el tema.
        
        Args:
            event: Evento de pintado
        """
        if not self.pixmap:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Obtener dimensiones
        widget_rect = self.rect()
        widget_w = widget_rect.width()
        widget_h = widget_rect.height()
        
        pixmap_w = self.pixmap.width()
        pixmap_h = self.pixmap.height()
        
        # Calcular escala tipo "cover" (cubrir toda el área manteniendo aspecto)
        scale_w = widget_w / pixmap_w
        scale_h = widget_h / pixmap_h
        scale = max(scale_w, scale_h)  # Usar el mayor para cubrir todo
        
        # Calcular dimensiones escaladas
        scaled_w = int(pixmap_w * scale)
        scaled_h = int(pixmap_h * scale)
        
        # Centrar la imagen
        x = (widget_w - scaled_w) // 2
        y = (widget_h - scaled_h) // 2
        
        # Dibujar imagen escalada
        painter.drawPixmap(x, y, scaled_w, scaled_h, self.pixmap)
        
        # Aplicar overlay oscuro en tema dark (30% de opacidad)
        if self.current_theme == THEME_DARK:
            painter.setOpacity(0.30)
            painter.fillRect(widget_rect, Qt.GlobalColor.black)
        
        painter.end()
