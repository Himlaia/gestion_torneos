"""
Tests básicos para el componente DigitalClock.
Valida funcionalidad principal sin dependencias externas.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTime, QTimer
from digital_clock import DigitalClock, ClockMode


def test_initialization():
    """Test: Inicialización del componente."""
    clock = DigitalClock()
    assert clock._mode == ClockMode.CLOCK
    assert clock._is24Hour == True
    assert clock._alarmEnabled == False
    print("✓ Test inicialización: PASSED")


def test_properties():
    """Test: Propiedades @Property."""
    clock = DigitalClock()
    
    # Mode
    clock.mode = ClockMode.TIMER
    assert clock._mode == ClockMode.TIMER
    assert clock.mode == "timer"
    
    clock.mode = "clock"
    assert clock._mode == ClockMode.CLOCK
    
    # is24Hour
    clock.is24Hour = False
    assert clock._is24Hour == False
    
    # Alarm
    clock.alarmEnabled = True
    assert clock._alarmEnabled == True
    
    test_time = QTime(10, 30, 0)
    clock.alarmTime = test_time
    assert clock._alarmTime == test_time
    
    clock.alarmMessage = "Test Message"
    assert clock._alarmMessage == "Test Message"
    
    print("✓ Test propiedades: PASSED")


def test_timer_controls():
    """Test: Controles del cronómetro."""
    clock = DigitalClock()
    clock.mode = ClockMode.TIMER
    
    # Stopwatch mode
    clock.setStopwatchMode()
    assert clock._isCountdown == False
    assert clock._elapsedSeconds == 0
    
    # Start/Pause/Reset
    clock.start()
    assert clock._timerRunning == True
    assert clock._timerPaused == False
    
    clock.pause()
    assert clock._timerPaused == True
    
    clock.reset()
    assert clock._timerRunning == False
    assert clock._elapsedSeconds == 0
    
    # Countdown mode
    clock.setCountdownTime(hours=1, minutes=30, seconds=45)
    expected_seconds = 1*3600 + 30*60 + 45
    assert clock._countdownSeconds == expected_seconds
    assert clock._isCountdown == True
    
    print("✓ Test controles cronómetro: PASSED")


def test_state_queries():
    """Test: Consultas de estado."""
    clock = DigitalClock()
    clock.mode = ClockMode.TIMER
    
    # Initial state
    assert clock.isRunning() == False
    assert clock.isPaused() == False
    
    # Running state
    clock.start()
    assert clock.isRunning() == True
    assert clock.isPaused() == False
    
    # Paused state
    clock.pause()
    assert clock.isRunning() == False
    assert clock.isPaused() == True
    
    print("✓ Test estado: PASSED")


def test_signals():
    """Test: Señales personalizadas."""
    clock = DigitalClock()
    
    # Verificar que las señales existen
    assert hasattr(clock, 'alarmTriggered')
    assert hasattr(clock, 'timerFinished')
    
    # Variable para capturar señal
    signal_received = {'alarm': False, 'timer': False}
    
    def on_alarm(msg):
        signal_received['alarm'] = True
    
    def on_timer_finished():
        signal_received['timer'] = True
    
    # Conectar señales
    clock.alarmTriggered.connect(on_alarm)
    clock.timerFinished.connect(on_timer_finished)
    
    # Simular alarma
    clock._alarmEnabled = True
    clock._alarmMessage = "Test"
    clock.alarmTriggered.emit("Test")
    assert signal_received['alarm'] == True
    
    # Simular timer finished
    clock.timerFinished.emit()
    assert signal_received['timer'] == True
    
    print("✓ Test señales: PASSED")


def test_mode_switching():
    """Test: Cambio entre modos."""
    clock = DigitalClock()
    
    # CLOCK -> TIMER
    assert clock._mode == ClockMode.CLOCK
    clock.mode = ClockMode.TIMER
    assert clock._mode == ClockMode.TIMER
    
    # TIMER -> CLOCK
    clock.mode = ClockMode.CLOCK
    assert clock._mode == ClockMode.CLOCK
    
    # String mode
    clock.mode = "timer"
    assert clock._mode == ClockMode.TIMER
    
    clock.mode = "clock"
    assert clock._mode == ClockMode.CLOCK
    
    print("✓ Test cambio de modos: PASSED")


def test_elapsed_time():
    """Test: Obtener tiempo transcurrido."""
    clock = DigitalClock()
    clock.mode = ClockMode.TIMER
    
    # Stopwatch
    clock.setStopwatchMode()
    clock._elapsedSeconds = 125
    assert clock.getElapsedTime() == 125
    
    # Countdown
    clock.setCountdownTime(minutes=5)
    assert clock.getElapsedTime() == 300
    
    clock._countdownSeconds = 180
    assert clock.getElapsedTime() == 180
    
    print("✓ Test tiempo transcurrido: PASSED")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "="*50)
    print("🧪 Ejecutando Tests de DigitalClock")
    print("="*50 + "\n")
    
    try:
        test_initialization()
        test_properties()
        test_timer_controls()
        test_state_queries()
        test_signals()
        test_mode_switching()
        test_elapsed_time()
        
        print("\n" + "="*50)
        print("✅ TODOS LOS TESTS PASARON")
        print("="*50 + "\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}\n")
        return False
    except Exception as e:
        print(f"\n⚠️ ERROR: {e}\n")
        return False


if __name__ == "__main__":
    # Necesitamos QApplication para componentes Qt
    app = QApplication(sys.argv)
    
    success = run_all_tests()
    
    sys.exit(0 if success else 1)
