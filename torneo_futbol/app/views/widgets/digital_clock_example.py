"""
Ejemplo de uso del componente DigitalClock.
Demuestra todas las características: reloj, cronómetro, alarmas.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTimeEdit, 
    QLineEdit, QCheckBox, QRadioButton, QSpinBox, QGroupBox
)
from PySide6.QtCore import QTime, Qt
from digital_clock import DigitalClock, ClockMode


class DigitalClockDemo(QMainWindow):
    """Ventana de demostración del componente DigitalClock."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DigitalClock - Demostración Completa")
        self.resize(600, 500)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # ==================== Reloj Digital ====================
        self.clock = DigitalClock()
        self.clock.setMinimumHeight(80)
        layout.addWidget(self.clock)
        
        # Conectar señales
        self.clock.alarmTriggered.connect(self.on_alarm_triggered)
        self.clock.timerFinished.connect(self.on_timer_finished)
        
        # ==================== Controles de Modo ====================
        mode_group = QGroupBox("Modo")
        mode_layout = QHBoxLayout(mode_group)
        
        self.radio_clock = QRadioButton("Reloj")
        self.radio_clock.setChecked(True)
        self.radio_clock.toggled.connect(self.on_mode_changed)
        
        self.radio_timer = QRadioButton("Cronómetro")
        self.radio_timer.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.radio_clock)
        mode_layout.addWidget(self.radio_timer)
        layout.addWidget(mode_group)
        
        # ==================== Controles de Reloj ====================
        self.clock_group = QGroupBox("Configuración de Reloj")
        clock_layout = QVBoxLayout(self.clock_group)
        
        # Formato 24h
        self.check_24h = QCheckBox("Formato 24 horas")
        self.check_24h.setChecked(True)
        self.check_24h.toggled.connect(self.on_24h_changed)
        clock_layout.addWidget(self.check_24h)
        
        # Alarma
        alarm_layout = QHBoxLayout()
        self.check_alarm = QCheckBox("Alarma")
        self.check_alarm.toggled.connect(self.on_alarm_enabled_changed)
        alarm_layout.addWidget(self.check_alarm)
        
        alarm_layout.addWidget(QLabel("Hora:"))
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime().addSecs(10))
        self.time_edit.timeChanged.connect(self.on_alarm_time_changed)
        alarm_layout.addWidget(self.time_edit)
        
        alarm_layout.addWidget(QLabel("Mensaje:"))
        self.alarm_msg = QLineEdit("¡Es hora!")
        self.alarm_msg.textChanged.connect(self.on_alarm_message_changed)
        alarm_layout.addWidget(self.alarm_msg)
        
        clock_layout.addLayout(alarm_layout)
        layout.addWidget(self.clock_group)
        
        # ==================== Controles de Cronómetro ====================
        self.timer_group = QGroupBox("Configuración de Cronómetro")
        self.timer_group.hide()
        timer_layout = QVBoxLayout(self.timer_group)
        
        # Tipo de cronómetro
        type_layout = QHBoxLayout()
        self.radio_stopwatch = QRadioButton("Ascendente (Stopwatch)")
        self.radio_stopwatch.setChecked(True)
        self.radio_stopwatch.toggled.connect(self.on_timer_type_changed)
        
        self.radio_countdown = QRadioButton("Descendente (Countdown)")
        
        type_layout.addWidget(self.radio_stopwatch)
        type_layout.addWidget(self.radio_countdown)
        timer_layout.addLayout(type_layout)
        
        # Configuración countdown
        countdown_layout = QHBoxLayout()
        countdown_layout.addWidget(QLabel("Countdown:"))
        
        countdown_layout.addWidget(QLabel("H:"))
        self.spin_hours = QSpinBox()
        self.spin_hours.setMaximum(23)
        self.spin_hours.valueChanged.connect(self.on_countdown_changed)
        countdown_layout.addWidget(self.spin_hours)
        
        countdown_layout.addWidget(QLabel("M:"))
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setMaximum(59)
        self.spin_minutes.setValue(1)
        self.spin_minutes.valueChanged.connect(self.on_countdown_changed)
        countdown_layout.addWidget(self.spin_minutes)
        
        countdown_layout.addWidget(QLabel("S:"))
        self.spin_seconds = QSpinBox()
        self.spin_seconds.setMaximum(59)
        self.spin_seconds.valueChanged.connect(self.on_countdown_changed)
        countdown_layout.addWidget(self.spin_seconds)
        
        countdown_layout.addStretch()
        timer_layout.addLayout(countdown_layout)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶ Iniciar")
        self.btn_start.clicked.connect(self.on_start)
        
        self.btn_pause = QPushButton("⏸ Pausar")
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_pause.setEnabled(False)
        
        self.btn_reset = QPushButton("⏹ Resetear")
        self.btn_reset.clicked.connect(self.on_reset)
        
        buttons_layout.addWidget(self.btn_start)
        buttons_layout.addWidget(self.btn_pause)
        buttons_layout.addWidget(self.btn_reset)
        timer_layout.addLayout(buttons_layout)
        
        layout.addWidget(self.timer_group)
        
        # ==================== Estado ====================
        self.status_label = QLabel("Listo")
        self.status_label.setStyleSheet("padding: 10px; background-color: #e0e0e0;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def on_mode_changed(self):
        """Cambia entre modo reloj y cronómetro."""
        if self.radio_clock.isChecked():
            self.clock.mode = ClockMode.CLOCK
            self.clock_group.show()
            self.timer_group.hide()
            self.status_label.setText("Modo: Reloj")
        else:
            self.clock.mode = ClockMode.TIMER
            self.clock_group.hide()
            self.timer_group.show()
            self.status_label.setText("Modo: Cronómetro")
            self.on_timer_type_changed()
    
    def on_24h_changed(self, checked):
        """Cambia el formato de hora."""
        self.clock.is24Hour = checked
    
    def on_alarm_enabled_changed(self, checked):
        """Habilita/deshabilita la alarma."""
        self.clock.alarmEnabled = checked
        self.status_label.setText(
            f"Alarma {'activada' if checked else 'desactivada'}"
        )
    
    def on_alarm_time_changed(self, time):
        """Actualiza la hora de la alarma."""
        self.clock.alarmTime = time
    
    def on_alarm_message_changed(self, text):
        """Actualiza el mensaje de alarma."""
        self.clock.alarmMessage = text
    
    def on_timer_type_changed(self):
        """Cambia entre stopwatch y countdown."""
        if self.radio_stopwatch.isChecked():
            self.clock.setStopwatchMode()
            self.spin_hours.setEnabled(False)
            self.spin_minutes.setEnabled(False)
            self.spin_seconds.setEnabled(False)
            self.status_label.setText("Cronómetro ascendente configurado")
        else:
            self.on_countdown_changed()
            self.spin_hours.setEnabled(True)
            self.spin_minutes.setEnabled(True)
            self.spin_seconds.setEnabled(True)
    
    def on_countdown_changed(self):
        """Actualiza el tiempo del countdown."""
        if self.radio_countdown.isChecked():
            self.clock.setCountdownTime(
                self.spin_hours.value(),
                self.spin_minutes.value(),
                self.spin_seconds.value()
            )
            self.status_label.setText("Countdown configurado")
    
    def on_start(self):
        """Inicia el cronómetro."""
        self.clock.start()
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.status_label.setText("▶ Ejecutando...")
    
    def on_pause(self):
        """Pausa el cronómetro."""
        self.clock.pause()
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.status_label.setText("⏸ Pausado")
    
    def on_reset(self):
        """Resetea el cronómetro."""
        self.clock.reset()
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.status_label.setText("⏹ Reseteado")
    
    def on_alarm_triggered(self, message):
        """Maneja el evento de alarma."""
        self.status_label.setText(f"🔔 ALARMA: {message}")
        self.status_label.setStyleSheet(
            "padding: 10px; background-color: #ffeb3b; font-weight: bold;"
        )
    
    def on_timer_finished(self):
        """Maneja el evento de fin de countdown."""
        self.status_label.setText("⏰ ¡Tiempo terminado!")
        self.status_label.setStyleSheet(
            "padding: 10px; background-color: #ff9800; font-weight: bold;"
        )
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)


def main():
    """Punto de entrada de la aplicación de ejemplo."""
    app = QApplication(sys.argv)
    
    # Aplicar estilo
    app.setStyle("Fusion")
    
    demo = DigitalClockDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
