"""
DigitalClock - Componente visual reutilizable para mostrar reloj o cronómetro.
Hereda de QLCDNumber y usa @Property de PySide6 para configuración.
Sin dependencias externas - completamente portable.
"""

from enum import Enum
from PySide6.QtCore import (
    QTime, QTimer, Signal, Property, QObject, Qt
)
from PySide6.QtWidgets import QLCDNumber


class ClockMode(Enum):
    """Enum para los modos del reloj digital."""
    CLOCK = "clock"
    TIMER = "timer"


class DigitalClock(QLCDNumber):
    """
    Componente de reloj digital reutilizable con múltiples modos.
    
    Características:
    - Modo CLOCK: Muestra la hora actual del sistema
    - Modo TIMER: Cronómetro ascendente/descendente
    - Soporte para formato 12h/24h
    - Sistema de alarmas configurables
    - Señales para eventos de alarma y fin de cronómetro
    
    Uso básico:
        clock = DigitalClock()
        clock.mode = ClockMode.CLOCK
        clock.is24Hour = True
        clock.show()
    """
    
    # Señales
    alarmTriggered = Signal(str)  # Emite el mensaje de alarma
    timerFinished = Signal()      # Emite cuando el cronómetro llega a 0
    
    def __init__(self, parent=None):
        """
        Inicializa el reloj digital.
        
        Args:
            parent: Widget padre opcional
        """
        super().__init__(parent)
        
        # Propiedades privadas
        self._mode = ClockMode.CLOCK
        self._is24Hour = True
        self._alarmEnabled = False
        self._alarmTime = QTime(0, 0, 0)
        self._alarmMessage = self.tr("¡Alarma!")
        self._alarmTriggered = False  # Para disparar alarma solo una vez
        
        # Estado del cronómetro
        self._timerRunning = False
        self._timerPaused = False
        self._elapsedSeconds = 0  # Para cronómetro ascendente
        self._countdownSeconds = 0  # Para cronómetro descendente
        self._isCountdown = False  # True para countdown, False para stopwatch
        
        # Configuración del LCD
        self.setSegmentStyle(QLCDNumber.Flat)
        self.setDigitCount(11)  # Suficiente para "HH:MM:SS AM"
        self.setMinimumHeight(50)
        
        # Timer interno para actualización
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        
        # Iniciar en modo reloj
        self._startClock()
    
    def _update(self):
        """Actualiza la visualización según el modo actual."""
        if self._mode == ClockMode.CLOCK:
            self._updateClock()
        elif self._mode == ClockMode.TIMER:
            self._updateTimer()
    
    def _updateClock(self):
        """Actualiza el reloj con la hora actual."""
        current_time = QTime.currentTime()
        
        # Verificar alarma
        if self._alarmEnabled and not self._alarmTriggered:
            if current_time.hour() == self._alarmTime.hour() and \
               current_time.minute() == self._alarmTime.minute() and \
               current_time.second() == self._alarmTime.second():
                self._alarmTriggered = True
                self.alarmTriggered.emit(self._alarmMessage)
        
        # Resetear flag de alarma si pasó el minuto
        if self._alarmTriggered and current_time.second() != self._alarmTime.second():
            self._alarmTriggered = False
        
        # Formatear y mostrar
        if self._is24Hour:
            time_text = current_time.toString("HH:mm:ss")
        else:
            # Formato manual para asegurar AM/PM completo
            hour = current_time.hour()
            am_pm = "AM" if hour < 12 else "PM"
            display_hour = hour % 12
            if display_hour == 0:
                display_hour = 12
            time_text = "{:02d}:{:02d}:{:02d} {}".format(
                display_hour,
                current_time.minute(),
                current_time.second(),
                am_pm
            )
        
        self.display(time_text)
    
    def _updateTimer(self):
        """Actualiza el cronómetro."""
        if not self._timerRunning or self._timerPaused:
            return
        
        if self._isCountdown:
            # Modo countdown
            if self._countdownSeconds > 0:
                self._countdownSeconds -= 1
                self._displayTimerValue(self._countdownSeconds)
                
                if self._countdownSeconds == 0:
                    self._timerRunning = False
                    self._timer.stop()
                    self.timerFinished.emit()
            else:
                self._timerRunning = False
                self._timer.stop()
        else:
            # Modo stopwatch (ascendente)
            self._elapsedSeconds += 1
            self._displayTimerValue(self._elapsedSeconds)
    
    def _displayTimerValue(self, total_seconds):
        """
        Muestra un valor de tiempo en formato HH:MM:SS.
        
        Args:
            total_seconds: Total de segundos a mostrar
        """
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.display(time_text)
    
    def _startClock(self):
        """Inicia el modo reloj."""
        self._timer.start(1000)  # Actualizar cada segundo
        self._timerRunning = False
        self._updateClock()
    
    def _startTimerMode(self):
        """Inicia el modo cronómetro."""
        if not self._timerRunning:
            self._displayTimerValue(
                self._countdownSeconds if self._isCountdown else self._elapsedSeconds
            )
    
    # ==================== Propiedades ====================
    
    @Property(str)
    def mode(self):
        """Obtiene el modo actual del reloj."""
        return self._mode.value
    
    @mode.setter
    def mode(self, value):
        """
        Establece el modo del reloj.
        
        Args:
            value: ClockMode.CLOCK o ClockMode.TIMER (o sus valores string)
        """
        if isinstance(value, str):
            value = ClockMode(value)
        
        if self._mode != value:
            self._mode = value
            self._timer.stop()
            
            if self._mode == ClockMode.CLOCK:
                self._startClock()
            else:
                self._startTimerMode()
    
    @Property(bool)
    def is24Hour(self):
        """Indica si usa formato de 24 horas."""
        return self._is24Hour
    
    @is24Hour.setter
    def is24Hour(self, value):
        """
        Establece el formato de hora.
        
        Args:
            value: True para 24h, False para 12h (AM/PM)
        """
        self._is24Hour = bool(value)
        if self._mode == ClockMode.CLOCK:
            self._updateClock()
    
    @Property(bool)
    def alarmEnabled(self):
        """Indica si la alarma está habilitada."""
        return self._alarmEnabled
    
    @alarmEnabled.setter
    def alarmEnabled(self, value):
        """
        Habilita o deshabilita la alarma.
        
        Args:
            value: True para habilitar, False para deshabilitar
        """
        self._alarmEnabled = bool(value)
        self._alarmTriggered = False  # Resetear estado
    
    @Property(QTime)
    def alarmTime(self):
        """Obtiene la hora de la alarma."""
        return self._alarmTime
    
    @alarmTime.setter
    def alarmTime(self, value):
        """
        Establece la hora de la alarma.
        
        Args:
            value: QTime con la hora de alarma
        """
        if isinstance(value, QTime):
            self._alarmTime = value
            self._alarmTriggered = False  # Resetear para nueva alarma
    
    @Property(str)
    def alarmMessage(self):
        """Obtiene el mensaje de alarma."""
        return self._alarmMessage
    
    @alarmMessage.setter
    def alarmMessage(self, value):
        """
        Establece el mensaje de alarma.
        
        Args:
            value: Mensaje a emitir cuando suena la alarma
        """
        self._alarmMessage = str(value)
    
    # ==================== Métodos públicos ====================
    
    def start(self):
        """
        Inicia el cronómetro.
        Solo funciona en modo TIMER.
        """
        if self._mode != ClockMode.TIMER:
            return
        
        if not self._timerRunning:
            self._timerRunning = True
            self._timerPaused = False
            self._timer.start(1000)
        elif self._timerPaused:
            self._timerPaused = False
    
    def pause(self):
        """
        Pausa el cronómetro.
        Solo funciona en modo TIMER.
        """
        if self._mode != ClockMode.TIMER or not self._timerRunning:
            return
        
        self._timerPaused = True
    
    def reset(self):
        """
        Resetea el cronómetro a cero.
        Solo funciona en modo TIMER.
        """
        if self._mode != ClockMode.TIMER:
            return
        
        self._timerRunning = False
        self._timerPaused = False
        self._elapsedSeconds = 0
        self._countdownSeconds = 0
        self._timer.stop()
        self._displayTimerValue(0)
    
    # ==================== Métodos adicionales ====================
    
    def setCountdownTime(self, hours=0, minutes=0, seconds=0):
        """
        Configura el tiempo para countdown.
        
        Args:
            hours: Horas del countdown
            minutes: Minutos del countdown
            seconds: Segundos del countdown
        """
        total_seconds = hours * 3600 + minutes * 60 + seconds
        self._countdownSeconds = total_seconds
        self._isCountdown = True
        
        if self._mode == ClockMode.TIMER:
            self._displayTimerValue(self._countdownSeconds)
    
    def setStopwatchMode(self):
        """Configura el cronómetro en modo ascendente (stopwatch)."""
        self._isCountdown = False
        self._elapsedSeconds = 0
        
        if self._mode == ClockMode.TIMER:
            self._displayTimerValue(0)
    
    def isRunning(self):
        """
        Verifica si el cronómetro está corriendo.
        
        Returns:
            bool: True si está corriendo, False en caso contrario
        """
        return self._timerRunning and not self._timerPaused
    
    def isPaused(self):
        """
        Verifica si el cronómetro está en pausa.
        
        Returns:
            bool: True si está pausado, False en caso contrario
        """
        return self._timerPaused
    
    def getElapsedTime(self):
        """
        Obtiene el tiempo transcurrido en el cronómetro.
        
        Returns:
            int: Segundos transcurridos
        """
        return self._elapsedSeconds if not self._isCountdown else \
               (self._countdownSeconds if self._countdownSeconds > 0 else 0)
