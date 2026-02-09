"""Página de Herramientas."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QCheckBox, QTimeEdit, QRadioButton, QGroupBox, 
    QPushButton, QSpinBox, QLineEdit, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QTime, QEvent
from app.views.widgets.digital_clock import DigitalClock, ClockMode


class PageTools(QWidget):
    """Página de herramientas con reloj digital configurable."""
    
    def __init__(self):
        """Inicializa la página de herramientas."""
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Establecer objectName para el widget raíz
        self.setObjectName("pageRoot")
        
        # Layout principal con márgenes
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 4, 20, 12)
        layout_principal.setSpacing(8)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Título de la página (guardar referencia)
        self.titulo = QLabel(self.tr("Herramientas"))
        self.titulo.setObjectName("titleLabel")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_principal.addWidget(self.titulo)
        
        # Contenedor de contenido (card)
        content_card = QFrame()
        content_card.setObjectName("contentCard")
        content_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(15)
        
        # Subtítulo dentro del card (guardar referencia)
        self.subtitulo = QLabel(self.tr("Reloj Digital Configurable"))
        self.subtitulo.setObjectName("subtitleLabel")
        self.subtitulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(self.subtitulo)
        
        # ==================== COMPONENTE DIGITAL CLOCK ====================
        self.digital_clock = DigitalClock()
        self.digital_clock.setMinimumHeight(80)
        self.digital_clock.setMaximumHeight(120)
        self.digital_clock.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Conectar señales del reloj
        self.digital_clock.alarmTriggered.connect(self._on_alarm_triggered)
        self.digital_clock.timerFinished.connect(self._on_timer_finished)
        
        card_layout.addWidget(self.digital_clock)
        
        # Label para mostrar notificaciones
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(30)
        card_layout.addWidget(self.status_label)
        
        # ==================== CONTROLES DE CONFIGURACIÓN ====================
        
        # Grupo: Modo del Reloj (guardar referencia)
        self.modo_group = QGroupBox(self.tr("Modo"))
        modo_layout = QHBoxLayout(self.modo_group)
        
        self.radio_clock = QRadioButton(self.tr("Reloj"))
        self.radio_clock.setChecked(True)
        self.radio_clock.toggled.connect(self._on_mode_changed)
        
        self.radio_timer = QRadioButton(self.tr("Cronómetro"))
        self.radio_timer.toggled.connect(self._on_mode_changed)
        
        modo_layout.addWidget(self.radio_clock)
        modo_layout.addWidget(self.radio_timer)
        modo_layout.addStretch()
        
        card_layout.addWidget(self.modo_group)
        
        # ==================== CONTROLES DE RELOJ ====================
        self.clock_group = QGroupBox(self.tr("Configuración de Reloj"))
        clock_layout = QVBoxLayout(self.clock_group)
        
        # Formato 24 horas
        self.check_24h = QCheckBox(self.tr("Formato 24 horas"))
        self.check_24h.setChecked(True)
        self.check_24h.toggled.connect(self._on_24h_changed)
        clock_layout.addWidget(self.check_24h)
        
        # Activar alarma (alineado con el checkbox anterior)
        self.check_alarm = QCheckBox(self.tr("Activar alarma"))
        self.check_alarm.toggled.connect(self._on_alarm_enabled_changed)
        clock_layout.addWidget(self.check_alarm)
        
        # Configuración de alarma
        alarm_frame = QFrame()
        alarm_frame.setObjectName("alarmFrame")
        alarm_layout = QVBoxLayout(alarm_frame)
        alarm_layout.setContentsMargins(10, 10, 10, 10)
        alarm_layout.setSpacing(8)
        
        # Hora de alarma (guardar referencia al label)
        time_layout = QHBoxLayout()
        self.label_hora = QLabel(self.tr("Hora:"))
        time_layout.addWidget(self.label_hora)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime().addSecs(60))
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setEnabled(False)
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        alarm_layout.addLayout(time_layout)
        
        # Mensaje de alarma (guardar referencia al label)
        msg_layout = QHBoxLayout()
        self.label_mensaje = QLabel(self.tr("Mensaje:"))
        msg_layout.addWidget(self.label_mensaje)
        self.alarm_msg = QLineEdit(self.tr("¡Alarma!"))
        self.alarm_msg.setEnabled(False)
        msg_layout.addWidget(self.alarm_msg)
        alarm_layout.addLayout(msg_layout)
        
        # Botón para aplicar alarma
        apply_alarm_layout = QHBoxLayout()
        apply_alarm_layout.addStretch()
        self.btn_apply_alarm = QPushButton(self.tr("✓ Aplicar Alarma"))
        self.btn_apply_alarm.clicked.connect(self._on_apply_alarm)
        self.btn_apply_alarm.setEnabled(False)
        apply_alarm_layout.addWidget(self.btn_apply_alarm)
        alarm_layout.addLayout(apply_alarm_layout)
        
        clock_layout.addWidget(alarm_frame)
        card_layout.addWidget(self.clock_group)
        
        # ==================== CONTROLES DE CRONÓMETRO ====================
        self.timer_group = QGroupBox(self.tr("Configuración de Cronómetro"))
        self.timer_group.hide()
        timer_layout = QVBoxLayout(self.timer_group)
        
        # Tipo de cronómetro
        type_layout = QHBoxLayout()
        self.radio_stopwatch = QRadioButton(self.tr("Ascendente (Stopwatch)"))
        self.radio_stopwatch.setChecked(True)
        self.radio_stopwatch.toggled.connect(self._on_timer_type_changed)
        
        self.radio_countdown = QRadioButton(self.tr("Descendente (Countdown)"))
        
        type_layout.addWidget(self.radio_stopwatch)
        type_layout.addWidget(self.radio_countdown)
        type_layout.addStretch()
        timer_layout.addLayout(type_layout)
        
        # Configuración de countdown
        countdown_frame = QFrame()
        countdown_frame.setObjectName("countdownFrame")
        countdown_layout = QVBoxLayout(countdown_frame)
        countdown_layout.setContentsMargins(10, 10, 10, 10)
        countdown_layout.setSpacing(8)
        
        self.countdown_label = QLabel(self.tr("Tiempo de Countdown:"))
        countdown_layout.addWidget(self.countdown_label)
        
        countdown_inputs = QHBoxLayout()
        
        self.label_horas = QLabel(self.tr("Horas:"))
        countdown_inputs.addWidget(self.label_horas)
        self.spin_hours = QSpinBox()
        self.spin_hours.setMaximum(23)
        self.spin_hours.valueChanged.connect(self._on_countdown_changed)
        self.spin_hours.setEnabled(False)
        countdown_inputs.addWidget(self.spin_hours)
        
        self.label_minutos = QLabel(self.tr("Minutos:"))
        countdown_inputs.addWidget(self.label_minutos)
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setMaximum(59)
        self.spin_minutes.setValue(1)
        self.spin_minutes.valueChanged.connect(self._on_countdown_changed)
        self.spin_minutes.setEnabled(False)
        countdown_inputs.addWidget(self.spin_minutes)
        
        self.label_segundos = QLabel(self.tr("Segundos:"))
        countdown_inputs.addWidget(self.label_segundos)
        self.spin_seconds = QSpinBox()
        self.spin_seconds.setMaximum(59)
        self.spin_seconds.valueChanged.connect(self._on_countdown_changed)
        self.spin_seconds.setEnabled(False)
        countdown_inputs.addWidget(self.spin_seconds)
        
        countdown_inputs.addStretch()
        countdown_layout.addLayout(countdown_inputs)
        
        timer_layout.addWidget(countdown_frame)
        
        # Botones de control del cronómetro
        buttons_layout = QHBoxLayout()
        
        self.btn_start = QPushButton(self.tr("▶ Iniciar"))
        self.btn_start.clicked.connect(self._on_start)
        
        self.btn_pause = QPushButton(self.tr("⏸ Pausar"))
        self.btn_pause.clicked.connect(self._on_pause)
        self.btn_pause.setEnabled(False)
        
        self.btn_reset = QPushButton(self.tr("⏹ Resetear"))
        self.btn_reset.clicked.connect(self._on_reset)
        
        buttons_layout.addWidget(self.btn_start)
        buttons_layout.addWidget(self.btn_pause)
        buttons_layout.addWidget(self.btn_reset)
        buttons_layout.addStretch()
        
        timer_layout.addLayout(buttons_layout)
        card_layout.addWidget(self.timer_group)
        
        # Espaciador al final
        card_layout.addStretch()
        
        layout_principal.addWidget(content_card)
    
    # ==================== MÉTODOS DE MANEJO DE EVENTOS ====================
    
    def _on_mode_changed(self):
        """Cambia entre modo reloj y cronómetro."""
        if self.radio_clock.isChecked():
            self.digital_clock.mode = ClockMode.CLOCK
            self.clock_group.show()
            self.timer_group.hide()
            self._update_status(self.tr("Modo: Reloj"))
        else:
            self.digital_clock.mode = ClockMode.TIMER
            self.clock_group.hide()
            self.timer_group.show()
            self._update_status(self.tr("Modo: Cronómetro"))
            self._on_timer_type_changed()
    
    def _on_24h_changed(self, checked):
        """Cambia el formato de hora."""
        # Ajustar el número de dígitos ANTES de cambiar el formato para evitar parpadeo
        if checked:
            self.digital_clock.setDigitCount(8)  # HH:MM:SS
        else:
            self.digital_clock.setDigitCount(11)  # HH:MM:SS AM
        
        # Ahora cambiar el formato
        self.digital_clock.is24Hour = checked
        formato = self.tr("24 horas") if checked else self.tr("12 horas (AM/PM)")
        self._update_status(self.tr("Formato cambiado a {}").format(formato))
    
    def _on_alarm_enabled_changed(self, checked):
        """Habilita o deshabilita la alarma."""
        self.time_edit.setEnabled(checked)
        self.alarm_msg.setEnabled(checked)
        self.btn_apply_alarm.setEnabled(checked)
        
        if not checked:
            self.digital_clock.alarmEnabled = False
            self._update_status(self.tr("Alarma desactivada"))
        else:
            self._update_status(self.tr("Configure la alarma y presione 'Aplicar'"))
    
    def _on_apply_alarm(self):
        """Aplica la configuración de alarma."""
        alarm_time = self.time_edit.time()
        alarm_message = self.alarm_msg.text()
        
        self.digital_clock.alarmTime = alarm_time
        self.digital_clock.alarmMessage = alarm_message
        self.digital_clock.alarmEnabled = True
        
        self._update_status(
            self.tr("⏰ Alarma activada para: {}").format(alarm_time.toString('HH:mm:ss')),
            is_warning=True
        )
    
    def _on_timer_type_changed(self):
        """Cambia entre stopwatch y countdown."""
        if self.radio_stopwatch.isChecked():
            self.digital_clock.setStopwatchMode()
            self.spin_hours.setEnabled(False)
            self.spin_minutes.setEnabled(False)
            self.spin_seconds.setEnabled(False)
            self._update_status(self.tr("Cronómetro ascendente configurado"))
        else:
            self._on_countdown_changed()
            self.spin_hours.setEnabled(True)
            self.spin_minutes.setEnabled(True)
            self.spin_seconds.setEnabled(True)
    
    def _on_countdown_changed(self):
        """Actualiza el tiempo del countdown."""
        if self.radio_countdown.isChecked():
            hours = self.spin_hours.value()
            minutes = self.spin_minutes.value()
            seconds = self.spin_seconds.value()
            
            self.digital_clock.setCountdownTime(hours, minutes, seconds)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            self._update_status(self.tr("Countdown configurado: {}s").format(total_seconds))
    
    def _on_start(self):
        """Inicia el cronómetro."""
        self.digital_clock.start()
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self._update_status(self.tr("▶ Cronómetro en ejecución..."), is_running=True)
    
    def _on_pause(self):
        """Pausa el cronómetro."""
        self.digital_clock.pause()
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self._update_status(self.tr("⏸ Cronómetro pausado"))
    
    def _on_reset(self):
        """Resetea el cronómetro."""
        self.digital_clock.reset()
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self._update_status(self.tr("⏹ Cronómetro reseteado"))
    
    def _on_alarm_triggered(self, message):
        """Maneja el evento de alarma."""
        self._update_status(self.tr("🔔 ALARMA: {}").format(message), is_alarm=True)
        
        # Mostrar popup de alarma
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(self.tr("⏰ Alarma"))
        msg_box.setText(self.tr("¡ALARMA!"))
        msg_box.setInformativeText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fff;
            }
            QLabel {
                color: #000;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #009688;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #00796b;
            }
        """)
        msg_box.exec()
    
    def _on_timer_finished(self):
        """Maneja el evento de fin de countdown."""
        self._update_status(self.tr("⏰ ¡Tiempo terminado!"), is_alarm=True)
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        
        # Mostrar popup de fin de cronómetro
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(self.tr("⏱️ Cronómetro"))
        msg_box.setText(self.tr("¡Tiempo Terminado!"))
        msg_box.setInformativeText(self.tr("El cronómetro descendente ha llegado a cero."))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fff;
            }
            QLabel {
                color: #000;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #009688;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #00796b;
            }
        """)
        msg_box.exec()
    
    def _update_status(self, message, is_alarm=False, is_warning=False, is_running=False):
        """
        Actualiza el mensaje de estado.
        
        Args:
            message: Mensaje a mostrar
            is_alarm: Si es True, usa estilo de alarma
            is_warning: Si es True, usa estilo de advertencia
            is_running: Si es True, usa estilo de ejecución
        """
        self.status_label.setText(message)
        
        # Cambiar estilo según el tipo de mensaje
        if is_alarm:
            self.status_label.setStyleSheet("""
                QLabel#statusLabel {
                    background-color: #ff9800;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                }
            """)
        elif is_warning:
            self.status_label.setStyleSheet("""
                QLabel#statusLabel {
                    background-color: #ffeb3b;
                    color: #333;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                }
            """)
        elif is_running:
            self.status_label.setStyleSheet("""
                QLabel#statusLabel {
                    background-color: #4caf50;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                }
            """)
        else:
            self.status_label.setStyleSheet("""
                QLabel#statusLabel {
                    background-color: #e0e0e0;
                    color: #333;
                    padding: 8px;
                    border-radius: 4px;
                }
            """)    
    def changeEvent(self, event):
        """Maneja eventos de cambio, incluyendo cambio de idioma."""
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
    
    def retranslate_ui(self):
        """Actualiza todos los textos traducibles de la interfaz."""
        # Actualizar título y subtítulo
        self.titulo.setText(self.tr("Herramientas"))
        self.subtitulo.setText(self.tr("Reloj Digital Configurable"))
        
        # Actualizar grupo de modo
        self.modo_group.setTitle(self.tr("Modo"))
        self.radio_clock.setText(self.tr("Reloj"))
        self.radio_timer.setText(self.tr("Cronómetro"))
        
        # Actualizar controles de reloj
        self.clock_group.setTitle(self.tr("Configuración de Reloj"))
        self.check_24h.setText(self.tr("Formato 24 horas"))
        self.check_alarm.setText(self.tr("Activar alarma"))
        self.label_hora.setText(self.tr("Hora:"))
        self.label_mensaje.setText(self.tr("Mensaje:"))
        
        # Actualizar controles de cronómetro
        self.timer_group.setTitle(self.tr("Configuración de Cronómetro"))
        self.radio_stopwatch.setText(self.tr("Ascendente (Stopwatch)"))
        self.radio_countdown.setText(self.tr("Descendente (Countdown)"))
        self.countdown_label.setText(self.tr("Tiempo de Countdown:"))
        self.label_horas.setText(self.tr("Horas:"))
        self.label_minutos.setText(self.tr("Minutos:"))
        self.label_segundos.setText(self.tr("Segundos:"))
        
        # Actualizar botones
        self.btn_apply_alarm.setText(self.tr("✓ Aplicar Alarma"))
        self.btn_start.setText(self.tr("▶ Iniciar"))
        self.btn_pause.setText(self.tr("⏸ Pausar"))
        self.btn_reset.setText(self.tr("⏹ Resetear"))
        
        # Actualizar mensaje de alarma predeterminado si no ha sido modificado
        if self.alarm_msg.text() in ["¡Alarma!", "Alarm!"]:
            self.alarm_msg.setText(self.tr("¡Alarma!"))