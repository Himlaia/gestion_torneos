"""Página de Informes PDF."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QPushButton, QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QEvent


class PageReports(QWidget):
    """Página de generación de informes PDF."""

    # Señales
    generar_signal = Signal()
    guardar_como_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("pageRoot")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 4, 20, 12)
        layout_principal.setSpacing(8)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        self.titulo = QLabel(self.tr("Informes"))
        self.titulo.setObjectName("titleLabel")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_principal.addWidget(self.titulo)

        # Card de contenido
        content_card = QFrame()
        content_card.setObjectName("contentCard")
        content_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # Subtítulo
        self.subtitulo = QLabel(self.tr("Generador de Informes PDF"))
        self.subtitulo.setObjectName("subtitleLabel")
        self.subtitulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(self.subtitulo)

        # ── Selector de tipo de informe ──
        tipo_layout = QHBoxLayout()
        self.label_tipo = QLabel(self.tr("Tipo de informe:"))
        self.label_tipo.setFixedWidth(130)
        tipo_layout.addWidget(self.label_tipo)

        self.combo_tipo = QComboBox()
        self.combo_tipo.setObjectName("ComboAccent")
        self.combo_tipo.addItem(self.tr("Equipos y Jugadores"), "equipos_jugadores")
        self.combo_tipo.addItem(self.tr("Partidos y Resultados"), "partidos_resultados")
        self.combo_tipo.addItem(
            self.tr("Clasificacion y Eliminatorias"), "clasificacion"
        )
        self.combo_tipo.currentIndexChanged.connect(self._on_tipo_changed)
        self.combo_tipo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        tipo_layout.addWidget(self.combo_tipo)
        card_layout.addLayout(tipo_layout)

        # ── Filtro por equipo (solo informe 1) ──
        self.filtro_equipo_layout = QHBoxLayout()
        self.label_equipo = QLabel(self.tr("Filtrar por equipo:"))
        self.label_equipo.setFixedWidth(130)
        self.filtro_equipo_layout.addWidget(self.label_equipo)

        self.combo_equipo = QComboBox()
        self.combo_equipo.setObjectName("ComboAccent")
        self.combo_equipo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.filtro_equipo_layout.addWidget(self.combo_equipo)

        self.widget_filtro_equipo = QWidget()
        self.widget_filtro_equipo.setLayout(self.filtro_equipo_layout)
        card_layout.addWidget(self.widget_filtro_equipo)

        # ── Filtro por eliminatoria (informes 2 y 3) ──
        self.filtro_elim_layout = QHBoxLayout()
        self.label_eliminatoria = QLabel(self.tr("Filtrar por fase:"))
        self.label_eliminatoria.setFixedWidth(130)
        self.filtro_elim_layout.addWidget(self.label_eliminatoria)

        self.combo_eliminatoria = QComboBox()
        self.combo_eliminatoria.setObjectName("ComboAccent")
        self.combo_eliminatoria.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.filtro_elim_layout.addWidget(self.combo_eliminatoria)

        self.widget_filtro_elim = QWidget()
        self.widget_filtro_elim.setLayout(self.filtro_elim_layout)
        self.widget_filtro_elim.hide()
        card_layout.addWidget(self.widget_filtro_elim)

        # ── Botones ──
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)

        self.btn_generar = QPushButton(self.tr("Generar PDF"))
        self.btn_generar.setObjectName("successButton")
        self.btn_generar.setMinimumWidth(140)
        self.btn_generar.clicked.connect(self.generar_signal.emit)
        botones_layout.addWidget(self.btn_generar)

        self.btn_guardar_como = QPushButton(self.tr("Guardar como..."))
        self.btn_guardar_como.setMinimumWidth(140)
        self.btn_guardar_como.clicked.connect(self.guardar_como_signal.emit)
        botones_layout.addWidget(self.btn_guardar_como)

        botones_layout.addStretch()
        card_layout.addLayout(botones_layout)

        # ── Estado ──
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(30)
        card_layout.addWidget(self.status_label)

        # ── Último PDF generado ──
        self.label_ultimo = QLabel("")
        self.label_ultimo.setWordWrap(True)
        self.label_ultimo.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        card_layout.addWidget(self.label_ultimo)

        card_layout.addStretch()
        layout_principal.addWidget(content_card)

        # Estado inicial de filtros
        self._on_tipo_changed(0)

    # ── Visibilidad de filtros ───────────────
    def _on_tipo_changed(self, index: int):
        tipo = self.combo_tipo.currentData()
        if tipo == "equipos_jugadores":
            self.widget_filtro_equipo.show()
            self.widget_filtro_elim.hide()
        else:
            self.widget_filtro_equipo.hide()
            self.widget_filtro_elim.show()

    # ── Getters ──────────────────────────────
    def get_tipo_informe(self) -> str:
        return self.combo_tipo.currentData()

    def get_equipo_id(self):
        return self.combo_equipo.currentData()

    def get_eliminatoria(self):
        return self.combo_eliminatoria.currentData()

    # ── Setters para combos de filtro ────────
    def set_equipos(self, equipos: list[dict]):
        self.combo_equipo.clear()
        self.combo_equipo.addItem(self.tr("Todos los equipos"), None)
        for eq in equipos:
            self.combo_equipo.addItem(eq["nombre"], eq["id"])

    def set_eliminatorias(self, fases: list[str]):
        self.combo_eliminatoria.clear()
        self.combo_eliminatoria.addItem(self.tr("Todas las fases"), None)
        labels = {
            "octavos": self.tr("Octavos de Final"),
            "cuartos": self.tr("Cuartos de Final"),
            "semifinal": self.tr("Semifinales"),
            "final": self.tr("Final"),
        }
        for fase in fases:
            self.combo_eliminatoria.addItem(
                labels.get(fase, fase.capitalize()), fase
            )

    # ── Estado ───────────────────────────────
    def set_status(self, message: str, is_success: bool = True):
        self.status_label.setText(message)
        if is_success:
            self.status_label.setStyleSheet("""
                QLabel#statusLabel {
                    background-color: #d5f4e6;
                    color: #0e6655;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                }
            """)
        else:
            self.status_label.setStyleSheet("""
                QLabel#statusLabel {
                    background-color: #fadbd8;
                    color: #922b21;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                }
            """)

    def set_ultimo_pdf(self, path: str):
        self.label_ultimo.setText(self.tr("Ultimo PDF: ") + path)

    def clear_status(self):
        self.status_label.setText("")
        self.status_label.setStyleSheet("")
        self.label_ultimo.setText("")

    # ── i18n ─────────────────────────────────
    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def retranslate_ui(self):
        self.titulo.setText(self.tr("Informes"))
        self.subtitulo.setText(self.tr("Generador de Informes PDF"))
        self.label_tipo.setText(self.tr("Tipo de informe:"))
        self.label_equipo.setText(self.tr("Filtrar por equipo:"))
        self.label_eliminatoria.setText(self.tr("Filtrar por fase:"))
        self.btn_generar.setText(self.tr("Generar PDF"))
        self.btn_guardar_como.setText(self.tr("Guardar como..."))

        # Actualizar items de combo tipo
        self.combo_tipo.setItemText(0, self.tr("Equipos y Jugadores"))
        self.combo_tipo.setItemText(1, self.tr("Partidos y Resultados"))
        self.combo_tipo.setItemText(2, self.tr("Clasificacion y Eliminatorias"))
