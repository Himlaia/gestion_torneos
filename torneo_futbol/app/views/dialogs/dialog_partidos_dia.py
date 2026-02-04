from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QWidget, QGroupBox, QDateTimeEdit,
    QComboBox, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime, QLocale
from PySide6.QtGui import QColor


class DialogPartidosDia(QDialog):
    
    abrir_detalle_signal = Signal(int)
    partido_programado_signal = Signal()  # Nueva señal para refrescar calendario
    
    def __init__(self, fecha: QDate, partidos: list[dict], partidos_pendientes: list[dict], arbitros: list[dict], parent=None):
        super().__init__(parent)
        self.fecha = fecha
        self.partidos = partidos  # Partidos programados ese día
        self.partidos_pendientes = partidos_pendientes  # Partidos sin fecha
        self.arbitros = arbitros
        self.partido_seleccionado_id = None
        self.setup_ui()
        self.cargar_partidos()
        
    def setup_ui(self):
        self.setWindowTitle("Partidos del día")
        self.setObjectName("dayMatchesDialog")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Formatear fecha en español
        locale = QLocale(QLocale.Spanish, QLocale.Spain)
        fecha_texto = locale.toString(self.fecha, "dddd, dd/MM/yyyy")
        # Capitalizar primera letra
        fecha_texto = fecha_texto[0].upper() + fecha_texto[1:] if fecha_texto else ""
        
        titulo = QLabel(fecha_texto)
        titulo.setObjectName("subtitleLabel")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Siempre mostrar lista (programados + pendientes)
        label_info = QLabel("Partidos programados y pendientes:")
        layout.addWidget(label_info)
        
        self.lista_partidos = QListWidget()
        self.lista_partidos.itemClicked.connect(self._on_partido_clicked)
        layout.addWidget(self.lista_partidos)
        
        # Panel de edición
        self.grupo_edicion = QGroupBox("Programar partido")
        self.grupo_edicion.setVisible(False)
        layout_edicion = QVBoxLayout()
        
        # Título del partido
        self.label_titulo = QLabel()
        self.label_titulo.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout_edicion.addWidget(self.label_titulo)
        
        # Fecha y hora
        layout_fecha = QHBoxLayout()
        layout_fecha.addWidget(QLabel("Fecha/Hora:"))
        self.fecha_hora_edit = QDateTimeEdit()
        self.fecha_hora_edit.setCalendarPopup(True)
        self.fecha_hora_edit.setDisplayFormat("dd/MM/yyyy HH:mm")
        # Fecha por defecto: la seleccionada a las 10:00
        default_datetime = QDateTime(self.fecha, self.fecha.startOfDay().time().addSecs(36000))  # 10:00 AM
        self.fecha_hora_edit.setDateTime(default_datetime)
        layout_fecha.addWidget(self.fecha_hora_edit)
        layout_edicion.addLayout(layout_fecha)
        
        # Árbitro
        layout_arbitro = QHBoxLayout()
        layout_arbitro.addWidget(QLabel("Árbitro:"))
        self.combo_arbitro = QComboBox()
        self.combo_arbitro.addItem("Sin asignar", None)
        for arb in self.arbitros:
            nombre = f"{arb['nombre']} {arb.get('apellidos', '')}".strip()
            self.combo_arbitro.addItem(nombre, arb['id'])
        layout_arbitro.addWidget(self.combo_arbitro)
        layout_edicion.addLayout(layout_arbitro)
        
        self.grupo_edicion.setLayout(layout_edicion)
        layout.addWidget(self.grupo_edicion)
        
        # Botones
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        self.btn_programar = QPushButton("Programar/Guardar")
        self.btn_programar.setObjectName("successButton")
        self.btn_programar.setEnabled(False)
        self.btn_programar.clicked.connect(self._on_programar)
        layout_botones.addWidget(self.btn_programar)
        
        self.btn_abrir = QPushButton("Abrir en detalle")
        self.btn_abrir.setEnabled(False)
        self.btn_abrir.clicked.connect(self._on_abrir_detalle)
        layout_botones.addWidget(self.btn_abrir)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(btn_cerrar)
        
        layout.addLayout(layout_botones)
        self.setLayout(layout)
    
    def cargar_partidos(self):
        # Cargar partidos programados
        for partido in sorted(self.partidos, key=lambda p: p.get('fecha_hora', '')):
            self._agregar_partido_a_lista(partido, programado=True)
        
        # Cargar partidos pendientes
        if self.partidos_pendientes:
            # Separador visual
            if self.partidos:
                item_sep = QListWidgetItem("─── Partidos pendientes de programar ───")
                item_sep.setFlags(Qt.ItemFlag.NoItemFlags)
                item_sep.setForeground(QColor(128, 128, 128))
                self.lista_partidos.addItem(item_sep)
            
            for partido in self.partidos_pendientes:
                self._agregar_partido_a_lista(partido, programado=False)
    
    def _agregar_partido_a_lista(self, partido: dict, programado: bool):
        item = QListWidgetItem()
        
        hora = ""
        if programado:
            fecha_completa = partido.get('fecha_hora', '')
            if ' ' in fecha_completa:
                hora = fecha_completa.split(' ')[1][:5] + " • "
        
        local = partido.get('local_nombre', 'TBD')
        visitante = partido.get('visitante_nombre', 'TBD')
        ronda = partido.get('eliminatoria', '')
        estado = partido.get('estado', 'Pendiente')
        
        texto = f"{hora}{local} vs {visitante} ({ronda})"
        
        if not programado:
            texto += " - SIN PROGRAMAR"
            item.setBackground(QColor(255, 152, 0, 30))  # Naranja
        elif estado == 'Jugado':
            goles_local = partido.get('goles_local', 0)
            goles_visitante = partido.get('goles_visitante', 0)
            texto += f" - {goles_local}:{goles_visitante}"
            item.setBackground(QColor(46, 204, 113, 30))  # Verde
        else:
            texto += " - Pendiente"
            item.setBackground(QColor(52, 152, 219, 30))  # Azul
        
        item.setText(texto)
        item.setData(Qt.ItemDataRole.UserRole, partido.get('id'))
        item.setData(Qt.ItemDataRole.UserRole + 1, programado)  # Flag de programado
        
        self.lista_partidos.addItem(item)
    
    def _on_partido_clicked(self, item: QListWidgetItem):
        # Verificar si es el separador
        if item.flags() == Qt.ItemFlag.NoItemFlags:
            return
        
        self.partido_seleccionado_id = item.data(Qt.ItemDataRole.UserRole)
        programado = item.data(Qt.ItemDataRole.UserRole + 1)
        
        # Buscar partido en ambas listas
        partido = None
        if programado:
            partido = next((p for p in self.partidos if p.get('id') == self.partido_seleccionado_id), None)
        else:
            partido = next((p for p in self.partidos_pendientes if p.get('id') == self.partido_seleccionado_id), None)
        
        if partido:
            self.grupo_edicion.setVisible(True)
            self.btn_programar.setEnabled(True)
            self.btn_abrir.setEnabled(True)
            
            local = partido.get('local_nombre', 'TBD')
            visitante = partido.get('visitante_nombre', 'TBD')
            ronda = partido.get('eliminatoria', '')
            self.label_titulo.setText(f"{local} vs {visitante} ({ronda})")
            
            # Si ya está programado, cargar su fecha/hora
            if programado and partido.get('fecha_hora'):
                qdatetime = QDateTime.fromString(partido.get('fecha_hora'), "yyyy-MM-dd HH:mm")
                if qdatetime.isValid():
                    self.fecha_hora_edit.setDateTime(qdatetime)
            
            # Cargar árbitro si existe
            arbitro_id = partido.get('arbitro_id')
            if arbitro_id:
                index = self.combo_arbitro.findData(arbitro_id)
                if index >= 0:
                    self.combo_arbitro.setCurrentIndex(index)
            else:
                self.combo_arbitro.setCurrentIndex(0)
    
    def _on_programar(self):
        """Programa o actualiza la fecha/hora del partido seleccionado."""
        if not self.partido_seleccionado_id:
            return
        
        from app.models.match_model import MatchModel
        
        try:
            # Obtener valores
            nueva_fecha = self.fecha_hora_edit.dateTime().toString("yyyy-MM-dd HH:mm")
            arbitro_id = self.combo_arbitro.currentData()
            
            # Actualizar partido
            MatchModel.actualizar_fecha_hora(self.partido_seleccionado_id, nueva_fecha)
            
            if arbitro_id:
                MatchModel.asignar_arbitro(self.partido_seleccionado_id, arbitro_id)
            
            msg = QMessageBox(self)
            msg.setObjectName("appMessageBox")
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Éxito")
            msg.setText("Partido programado correctamente")
            msg.setStyleSheet(self.styleSheet() or QApplication.instance().styleSheet())
            msg.exec()
            
            # Emitir señal para refrescar calendario
            self.partido_programado_signal.emit()
            
            # Cerrar diálogo
            self.accept()
            
        except Exception as e:
            msg = QMessageBox(self)
            msg.setObjectName("appMessageBox")
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Error al programar partido: {str(e)}")
            msg.setStyleSheet(self.styleSheet() or QApplication.instance().styleSheet())
            msg.exec()
    
    def _on_abrir_detalle(self):
        """Open selected match in detail panel."""
        if self.partido_seleccionado_id:
            self.abrir_detalle_signal.emit(self.partido_seleccionado_id)
            self.accept()

