"""Página de créditos."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QEvent
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
        self.title = QLabel(self.tr("Créditos"))
        self.title.setObjectName("titleLabel")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtítulo
        self.subtitle = QLabel(self.tr("Aplicación de Gestión de Torneo de Fútbol v{version}").format(version=VERSION))
        self.subtitle.setObjectName("subtitleLabel")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Autor
        self.author = QLabel(self.tr("Creado por Martina Valdivia Figueroa"))
        self.author.setObjectName("subtitleLabel")
        self.author.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addWidget(self.author)

        self.setLayout(layout)

    def changeEvent(self, event):
        """Maneja eventos de cambio, incluyendo cambio de idioma."""
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def retranslate_ui(self):
        """Actualiza todos los textos traducibles de la interfaz."""
        self.title.setText(self.tr("Créditos"))
        self.subtitle.setText(self.tr("Aplicación de Gestión de Torneo de Fútbol v{version}").format(version=VERSION))
        self.author.setText(self.tr("Creado por Martina Valdivia Figueroa"))
