"""
Ejemplo mínimo de uso del componente DigitalClock.
Ejemplo rápido para probar el componente.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTime
from digital_clock import DigitalClock, ClockMode


def ejemplo_reloj():
    """Ejemplo básico: Reloj digital simple."""
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("DigitalClock - Reloj Simple")
    
    # Crear reloj
    clock = DigitalClock()
    clock.mode = ClockMode.CLOCK
    clock.is24Hour = True
    
    window.setCentralWidget(clock)
    window.resize(400, 150)
    window.show()
    
    sys.exit(app.exec())


def ejemplo_cronometro():
    """Ejemplo básico: Cronómetro ascendente."""
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("DigitalClock - Cronómetro")
    
    # Crear cronómetro
    clock = DigitalClock()
    clock.mode = ClockMode.TIMER
    clock.setStopwatchMode()
    clock.start()  # Inicia automáticamente
    
    window.setCentralWidget(clock)
    window.resize(400, 150)
    window.show()
    
    sys.exit(app.exec())


def ejemplo_alarma():
    """Ejemplo básico: Reloj con alarma."""
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("DigitalClock - Con Alarma")
    
    # Crear reloj con alarma
    clock = DigitalClock()
    clock.mode = ClockMode.CLOCK
    
    # Configurar alarma en 10 segundos
    alarm_time = QTime.currentTime().addSecs(10)
    clock.alarmTime = alarm_time
    clock.alarmMessage = "¡Alarma de prueba!"
    clock.alarmEnabled = True
    
    # Conectar señal
    def on_alarm(msg):
        print(f"🔔 {msg}")
        window.setWindowTitle(f"DigitalClock - {msg}")
    
    clock.alarmTriggered.connect(on_alarm)
    
    window.setCentralWidget(clock)
    window.resize(400, 150)
    window.show()
    
    print(f"Alarma configurada para: {alarm_time.toString('HH:mm:ss')}")
    
    sys.exit(app.exec())


def ejemplo_countdown():
    """Ejemplo básico: Countdown timer."""
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("DigitalClock - Countdown 1 minuto")
    
    # Crear countdown
    clock = DigitalClock()
    clock.mode = ClockMode.TIMER
    clock.setCountdownTime(minutes=1)
    clock.start()
    
    # Conectar señal de finalización
    def on_finished():
        print("⏰ ¡Countdown terminado!")
        window.setWindowTitle("DigitalClock - ¡Terminado!")
    
    clock.timerFinished.connect(on_finished)
    
    window.setCentralWidget(clock)
    window.resize(400, 150)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Ejemplos Rápidos de DigitalClock")
    print("="*50)
    print("1. Reloj simple")
    print("2. Cronómetro ascendente")
    print("3. Reloj con alarma (10 seg)")
    print("4. Countdown 1 minuto")
    print("="*50)
    
    opcion = input("\nSelecciona un ejemplo (1-4): ").strip()
    
    if opcion == "1":
        ejemplo_reloj()
    elif opcion == "2":
        ejemplo_cronometro()
    elif opcion == "3":
        ejemplo_alarma()
    elif opcion == "4":
        ejemplo_countdown()
    else:
        print("Opción inválida. Ejecutando ejemplo de reloj...")
        ejemplo_reloj()
