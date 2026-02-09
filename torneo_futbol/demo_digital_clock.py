"""
Demo Independiente del Componente DigitalClock
Aplicación standalone para demostrar el componente reutilizable.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QRadioButton, QCheckBox,
    QTimeEdit, QSpinBox, QLineEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QFont

# Importar el componente
from app.views.widgets.digital_clock import DigitalClock, ClockMode


class DemoWindow(QMainWindow):
    """Ventana de demostración del componente DigitalClock."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo - DigitalClock Component")
        self.setMinimumSize(700, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title = QLabel("Reloj Digital")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # ==================== COMPONENTE DIGITAL CLOCK ====================
        self.digital_clock = DigitalClock()
        self.digital_clock.setMinimumHeight(100)
        self.digital_clock.setMaximumHeight(150)
        self.digital_clock.setStyleSheet("""
            QLCDNumber {
                background-color: #2c3e50;
                color: #3498db;
                border: 2px solid #34495e;
                border-radius: 8px;
            }
        """)
        
        # Conectar señales
        self.digital_clock.alarmTriggered.connect(self._on_alarm)
        self.digital_clock.timerFinished.connect(self._on_timer_finished)
        
        main_layout.addWidget(self.digital_clock)
        
        # Label de estado
        self.status_label = QLabel("Modo: Reloj (24 horas)")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # ==================== CONTROLES ====================
        
        # Grupo: Selección de Modo
        mode_group = QGroupBox("Modo de Operación")
        mode_layout = QHBoxLayout(mode_group)
        
        self.radio_clock = QRadioButton("🕐 Reloj")
        self.radio_clock.setChecked(True)
        self.radio_clock.toggled.connect(self._on_mode_changed)
        
        self.radio_timer = QRadioButton("⏱️ Cronómetro")
        
        mode_layout.addWidget(self.radio_clock)
        mode_layout.addWidget(self.radio_timer)
        mode_layout.addStretch()
        
        main_layout.addWidget(mode_group)
        
        # Contenedor para grupos dinámicos
        self.dynamic_container = QVBoxLayout()
        main_layout.addLayout(self.dynamic_container)
        
        # ==================== CONTROLES DE RELOJ ====================
        self.clock_group = QGroupBox("⚙️ Configuración de Reloj")
        clock_layout = QVBoxLayout(self.clock_group)
        
        # Formato 24h
        self.check_24h = QCheckBox("Formato 24 horas")
        self.check_24h.setChecked(True)
        self.check_24h.toggled.connect(self._on_format_changed)
        clock_layout.addWidget(self.check_24h)
        
        # Alarma
        self.check_alarm = QCheckBox("Activar alarma")
        self.check_alarm.toggled.connect(self._on_alarm_toggled)
        clock_layout.addWidget(self.check_alarm)
        
        # Configuración de alarma
        alarm_frame = QFrame()
        alarm_layout = QVBoxLayout(alarm_frame)
        alarm_layout.setContentsMargins(20, 5, 5, 5)
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Hora:"))
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime().addSecs(60))
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setEnabled(False)
        time_layout.addWidget(self.time_edit)
        alarm_layout.addLayout(time_layout)
        
        msg_layout = QHBoxLayout()
        msg_layout.addWidget(QLabel("Mensaje:"))
        self.alarm_msg = QLineEdit("¡Es hora!")
        self.alarm_msg.setEnabled(False)
        msg_layout.addWidget(self.alarm_msg)
        alarm_layout.addLayout(msg_layout)
        
        self.btn_apply_alarm = QPushButton("✓ Aplicar Alarma")
        self.btn_apply_alarm.clicked.connect(self._apply_alarm)
        self.btn_apply_alarm.setEnabled(False)
        self.btn_apply_alarm.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        alarm_layout.addWidget(self.btn_apply_alarm)
        
        clock_layout.addWidget(alarm_frame)
        self.dynamic_container.addWidget(self.clock_group)
        
        # ==================== CONTROLES DE CRONÓMETRO ====================
        self.timer_group = QGroupBox("⚙️ Configuración de Cronómetro")
        self.timer_group.hide()
        timer_layout = QVBoxLayout(self.timer_group)
        
        # Tipo
        type_layout = QHBoxLayout()
        self.radio_stopwatch = QRadioButton("⬆️ Ascendente (Stopwatch)")
        self.radio_stopwatch.setChecked(True)
        self.radio_stopwatch.toggled.connect(self._on_timer_type_changed)
        
        self.radio_countdown = QRadioButton("⬇️ Descendente (Countdown)")
        
        type_layout.addWidget(self.radio_stopwatch)
        type_layout.addWidget(self.radio_countdown)
        timer_layout.addLayout(type_layout)
        
        # Configuración countdown
        countdown_frame = QFrame()
        countdown_layout = QVBoxLayout(countdown_frame)
        countdown_layout.setContentsMargins(20, 5, 5, 5)
        
        countdown_layout.addWidget(QLabel("Tiempo de Countdown:"))
        
        spinners_layout = QHBoxLayout()
        spinners_layout.addWidget(QLabel("Horas:"))
        self.spin_hours = QSpinBox()
        self.spin_hours.setMaximum(23)
        self.spin_hours.valueChanged.connect(self._on_countdown_changed)
        self.spin_hours.setEnabled(False)
        spinners_layout.addWidget(self.spin_hours)
        
        spinners_layout.addWidget(QLabel("Minutos:"))
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setMaximum(59)
        self.spin_minutes.setValue(1)
        self.spin_minutes.valueChanged.connect(self._on_countdown_changed)
        self.spin_minutes.setEnabled(False)
        spinners_layout.addWidget(self.spin_minutes)
        
        spinners_layout.addWidget(QLabel("Segundos:"))
        self.spin_seconds = QSpinBox()
        self.spin_seconds.setMaximum(59)
        self.spin_seconds.valueChanged.connect(self._on_countdown_changed)
        self.spin_seconds.setEnabled(False)
        spinners_layout.addWidget(self.spin_seconds)
        
        countdown_layout.addLayout(spinners_layout)
        timer_layout.addWidget(countdown_frame)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶ Iniciar")
        self.btn_start.clicked.connect(self._on_start)
        self.btn_start.setStyleSheet("QPushButton { background-color: #27ae60; color: white; padding: 8px; border-radius: 4px; font-weight: bold; }")
        
        self.btn_pause = QPushButton("⏸ Pausar")
        self.btn_pause.clicked.connect(self._on_pause)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setStyleSheet("QPushButton { background-color: #f39c12; color: white; padding: 8px; border-radius: 4px; font-weight: bold; }")
        
        self.btn_reset = QPushButton("⏹ Resetear")
        self.btn_reset.clicked.connect(self._on_reset)
        self.btn_reset.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 8px; border-radius: 4px; font-weight: bold; }")
        
        buttons_layout.addWidget(self.btn_start)
        buttons_layout.addWidget(self.btn_pause)
        buttons_layout.addWidget(self.btn_reset)
        
        timer_layout.addLayout(buttons_layout)
        self.dynamic_container.addWidget(self.timer_group)
        
        # Espaciador
        main_layout.addStretch()
        
        # Footer
        footer = QLabel("Componente reutilizable para PySide6/PyQt6 • Versión 1.0")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 10px;")
        main_layout.addWidget(footer)
        
        # Aplicar estilos globales
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QRadioButton, QCheckBox {
                font-size: 13px;
            }
            QPushButton {
                min-height: 30px;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)
    
    # ==================== EVENT HANDLERS ====================
    
    def _on_mode_changed(self):
        """Cambia entre modo reloj y cronómetro."""
        if self.radio_clock.isChecked():
            self.digital_clock.mode = ClockMode.CLOCK
            self.clock_group.show()
            self.timer_group.hide()
            fmt = "24 horas" if self.check_24h.isChecked() else "12 horas"
            self.status_label.setText(f"Modo: Reloj ({fmt})")
        else:
            self.digital_clock.mode = ClockMode.TIMER
            self.clock_group.hide()
            self.timer_group.show()
            self._on_timer_type_changed()
    
    def _on_format_changed(self, checked):
        """Cambia formato de hora."""
        if checked:
            self.digital_clock.setDigitCount(8)
        else:
            self.digital_clock.setDigitCount(11)
        self.digital_clock.is24Hour = checked
        fmt = "24 horas" if checked else "12 horas (AM/PM)"
        self.status_label.setText(f"Modo: Reloj ({fmt})")
    
    def _on_alarm_toggled(self, checked):
        """Habilita/deshabilita controles de alarma."""
        self.time_edit.setEnabled(checked)
        self.alarm_msg.setEnabled(checked)
        self.btn_apply_alarm.setEnabled(checked)
        if not checked:
            self.digital_clock.alarmEnabled = False
    
    def _apply_alarm(self):
        """Aplica configuración de alarma."""
        self.digital_clock.alarmTime = self.time_edit.time()
        self.digital_clock.alarmMessage = self.alarm_msg.text()
        self.digital_clock.alarmEnabled = True
        self.status_label.setText(f"⏰ Alarma activada: {self.time_edit.time().toString('HH:mm:ss')}")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #f39c12;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
    
    def _on_timer_type_changed(self):
        """Cambia tipo de cronómetro."""
        if self.radio_stopwatch.isChecked():
            self.digital_clock.setStopwatchMode()
            self.spin_hours.setEnabled(False)
            self.spin_minutes.setEnabled(False)
            self.spin_seconds.setEnabled(False)
            self.status_label.setText("Modo: Cronómetro Ascendente")
        else:
            self._on_countdown_changed()
            self.spin_hours.setEnabled(True)
            self.spin_minutes.setEnabled(True)
            self.spin_seconds.setEnabled(True)
        
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
    
    def _on_countdown_changed(self):
        """Actualiza tiempo de countdown."""
        if self.radio_countdown.isChecked():
            h = self.spin_hours.value()
            m = self.spin_minutes.value()
            s = self.spin_seconds.value()
            self.digital_clock.setCountdownTime(h, m, s)
            total = h * 3600 + m * 60 + s
            self.status_label.setText(f"Modo: Countdown ({total}s)")
    
    def _on_start(self):
        """Inicia cronómetro."""
        self.digital_clock.start()
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.status_label.setText("▶ Cronómetro en ejecución...")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
    
    def _on_pause(self):
        """Pausa cronómetro."""
        self.digital_clock.pause()
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.status_label.setText("⏸ Cronómetro pausado")
    
    def _on_reset(self):
        """Resetea cronómetro."""
        self.digital_clock.reset()
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.status_label.setText("⏹ Cronómetro reseteado")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
    
    def _on_alarm(self, message):
        """Maneja alarma."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("⏰ Alarma")
        msg_box.setText("¡ALARMA!")
        msg_box.setInformativeText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fff;
            }
            QLabel {
                color: #000;
                font-size: 14px;
                font-weight: bold;
                min-width: 250px;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
        """)
        msg_box.exec()
    
    def _on_timer_finished(self):
        """Maneja fin de countdown."""
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("⏱️ Cronómetro")
        msg_box.setText("¡Tiempo Terminado!")
        msg_box.setInformativeText("El cronómetro descendente ha llegado a cero.")
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fff;
            }
            QLabel {
                color: #000;
                font-size: 14px;
                font-weight: bold;
                min-width: 250px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
        """)
        msg_box.exec()


def main():
    """Función principal."""
    app = QApplication(sys.argv)
    
    # Configurar fuente global
    font = QFont()
    font.setPointSize(10)
    font.setFamily("Segoe UI")
    app.setFont(font)
    
    # Crear y mostrar ventana
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
