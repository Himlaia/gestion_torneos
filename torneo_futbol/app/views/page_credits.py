"""Página de créditos."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from app.config import VERSION


class PageCredits(QWidget):
    """Página de créditos."""
    
    def __init__(self):
        """Inicializa la página de créditos."""
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título
        title = QLabel("Créditos")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtítulo
        subtitle = QLabel(f"Aplicación de Gestión de Torneo de Fútbol v{VERSION}")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Autor
        author = QLabel("Creado por Martina Valdivia Figueroa")
        author.setObjectName("subtitleLabel")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(author)
        
        self.setLayout(layout)
