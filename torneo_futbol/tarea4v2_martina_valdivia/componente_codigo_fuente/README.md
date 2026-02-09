# DigitalClock - Componente Reutilizable

## Descripción

`DigitalClock` es un componente visual reutilizable que hereda de `QLCDNumber` de PySide6. Proporciona funcionalidad de reloj digital y cronómetro con múltiples modos y configuraciones.

## Características

### 🕐 Modo Reloj (CLOCK)
- Muestra la hora actual del sistema en tiempo real
- Soporte para formato 12h (AM/PM) y 24h
- Sistema de alarmas configurables
- Notificación visual y popup cuando suena la alarma

### ⏱️ Modo Cronómetro (TIMER)
- **Cronómetro Ascendente (Stopwatch)**: Cuenta tiempo hacia arriba desde 0
- **Cronómetro Descendente (Countdown)**: Cuenta regresiva desde un tiempo configurado
- Controles de inicio, pausa y reset
- Notificación visual y popup cuando el countdown llega a cero

## Instalación

El componente está completamente autocontenido y solo requiere PySide6:

```python
from PySide6.QtCore import QTime
from app.views.widgets.digital_clock import DigitalClock, ClockMode
```

## Uso Básico

### Modo Reloj Simple

```python
from PySide6.QtWidgets import QApplication
from app.views.widgets.digital_clock import DigitalClock, ClockMode

app = QApplication([])

# Crear reloj
clock = DigitalClock()
clock.mode = ClockMode.CLOCK
clock.is24Hour = True
clock.show()

app.exec()
```

### Reloj con Alarma

```python
clock = DigitalClock()
clock.mode = ClockMode.CLOCK
clock.is24Hour = False  # Formato 12h AM/PM

# Configurar alarma
clock.alarmEnabled = True
clock.alarmTime = QTime(14, 30, 0)  # 2:30 PM
clock.alarmMessage = "¡Hora de la reunión!"

# Conectar señal
clock.alarmTriggered.connect(lambda msg: print(f"Alarma: {msg}"))
clock.show()
```

### Cronómetro Ascendente (Stopwatch)

```python
clock = DigitalClock()
clock.mode = ClockMode.TIMER
clock.setStopwatchMode()  # Modo ascendente

# Controles
clock.start()   # Iniciar
clock.pause()   # Pausar
clock.reset()   # Resetear a 0

clock.show()
```

### Cronómetro Descendente (Countdown)

```python
clock = DigitalClock()
clock.mode = ClockMode.TIMER

# Configurar countdown de 1 minuto 30 segundos
clock.setCountdownTime(hours=0, minutes=1, seconds=30)

# Conectar señal de finalización
clock.timerFinished.connect(lambda: print("¡Tiempo terminado!"))

clock.start()
clock.show()
```

## API Completa

### Propiedades (@Property)

| Propiedad | Tipo | Descripción | Valores |
|-----------|------|-------------|---------|
| `mode` | `str` o `ClockMode` | Modo actual del reloj | `"clock"` o `"timer"` |
| `is24Hour` | `bool` | Formato de hora | `True` (24h) / `False` (12h AM/PM) |
| `alarmEnabled` | `bool` | Estado de la alarma | `True` / `False` |
| `alarmTime` | `QTime` | Hora de la alarma | Objeto QTime |
| `alarmMessage` | `str` | Mensaje de alarma | Cualquier texto |

### Señales (Signals)

| Señal | Parámetros | Descripción |
|-------|------------|-------------|
| `alarmTriggered` | `str` (mensaje) | Se emite cuando suena la alarma |
| `timerFinished` | - | Se emite cuando el countdown llega a 0 |

### Métodos Públicos

#### Control del Cronómetro

```python
clock.start()   # Inicia o reanuda el cronómetro
clock.pause()   # Pausa el cronómetro
clock.reset()   # Resetea el cronómetro a 0
```

#### Configuración

```python
# Modo ascendente
clock.setStopwatchMode()

# Modo descendente
clock.setCountdownTime(hours=1, minutes=30, seconds=0)
```

#### Consultas

```python
clock.isRunning()  # Returns: bool - Si el cronómetro está corriendo
clock.isPaused()   # Returns: bool - Si el cronómetro está pausado
clock.getElapsedTime()  # Returns: int - Segundos transcurridos/restantes
```

## Ejemplo Completo

```python
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTime
from app.views.widgets.digital_clock import DigitalClock, ClockMode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo DigitalClock")
        
        # Layout principal
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Crear reloj
        self.clock = DigitalClock()
        self.clock.setMinimumHeight(100)
        layout.addWidget(self.clock)
        
        # Botones de modo
        btn_clock = QPushButton("Modo Reloj")
        btn_clock.clicked.connect(lambda: setattr(self.clock, 'mode', ClockMode.CLOCK))
        layout.addWidget(btn_clock)
        
        btn_timer = QPushButton("Modo Cronómetro")
        btn_timer.clicked.connect(self.setup_timer)
        layout.addWidget(btn_timer)
        
        # Botones de control
        btn_start = QPushButton("Iniciar")
        btn_start.clicked.connect(self.clock.start)
        layout.addWidget(btn_start)
        
        btn_pause = QPushButton("Pausar")
        btn_pause.clicked.connect(self.clock.pause)
        layout.addWidget(btn_pause)
        
        btn_reset = QPushButton("Resetear")
        btn_reset.clicked.connect(self.clock.reset)
        layout.addWidget(btn_reset)
        
        # Conectar señales
        self.clock.alarmTriggered.connect(self.on_alarm)
        self.clock.timerFinished.connect(self.on_timer_finished)
        
        self.setCentralWidget(central)
    
    def setup_timer(self):
        self.clock.mode = ClockMode.TIMER
        self.clock.setCountdownTime(hours=0, minutes=0, seconds=10)
    
    def on_alarm(self, message):
        print(f"¡ALARMA!: {message}")
    
    def on_timer_finished(self):
        print("¡Countdown terminado!")

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
```

## Integración en la Aplicación

El componente se utiliza en la página de Herramientas (`page_tools.py`):

```python
from app.views.widgets.digital_clock import DigitalClock, ClockMode

class PageTools(QWidget):
    def __init__(self):
        super().__init__()
        
        # Crear componente
        self.digital_clock = DigitalClock()
        self.digital_clock.setMinimumHeight(80)
        
        # Conectar señales
        self.digital_clock.alarmTriggered.connect(self._on_alarm_triggered)
        self.digital_clock.timerFinished.connect(self._on_timer_finished)
```

## Configuración Visual

### Personalizar Apariencia

```python
# Cambiar estilo de segmentos
clock.setSegmentStyle(QLCDNumber.Flat)     # Plano (por defecto)
clock.setSegmentStyle(QLCDNumber.Outline)  # Contorno
clock.setSegmentStyle(QLCDNumber.Filled)   # Relleno

# Ajustar tamaño
clock.setMinimumHeight(100)
clock.setMaximumHeight(200)

# Número de dígitos (se ajusta automáticamente según el formato)
clock.setDigitCount(8)   # Para 24h: HH:MM:SS
clock.setDigitCount(11)  # Para 12h: HH:MM:SS AM
```

## Características Técnicas

### Arquitectura

- **Herencia**: `QLCDNumber` (PySide6)
- **Patrón**: Component/Widget reutilizable
- **Actualización**: Timer interno de 1000ms (1 segundo)
- **Thread-safe**: Todas las operaciones en el thread principal de Qt

### Dependencias

```python
from PySide6.QtCore import QTime, QTimer, Signal, Property, Qt
from PySide6.QtWidgets import QLCDNumber
```

### Sin Dependencias Externas

El componente:
- ✅ No requiere modelos de base de datos
- ✅ No depende de servicios externos
- ✅ No usa configuración global
- ✅ Completamente autocontenido
- ✅ Portable a cualquier proyecto PySide6/PyQt6

## Notas de Implementación

### Formato AM/PM

El formato AM/PM usa formateo manual para garantizar la visualización completa:

```python
hour = current_time.hour()
am_pm = "AM" if hour < 12 else "PM"
display_hour = hour % 12 if hour % 12 != 0 else 12
time_text = f"{display_hour:02d}:{minute:02d}:{second:02d} {am_pm}"
```

### Timer Interno

El componente usa un `QTimer` interno (`self._timer`) que se actualiza cada segundo:

```python
self._timer = QTimer(self)
self._timer.timeout.connect(self._update)
self._timer.start(1000)  # 1 segundo
```

### Cambio de Modo

Al cambiar entre modos, el timer se reinicia automáticamente:

```python
self._timer.stop()
if self._mode == ClockMode.CLOCK:
    self._startClock()
else:
    self._startTimerMode()
```

## Extensiones Posibles

### Ideas para Ampliar el Componente

1. **Múltiples Alarmas**: Soportar varias alarmas simultáneas
2. **Sonido**: Agregar notificación sonora
3. **Temas Visuales**: Diferentes colores y estilos de LCD
4. **Laps**: Función de vueltas en el cronómetro
5. **Persistencia**: Guardar estado del cronómetro
6. **Formato Personalizado**: Permitir formatos de hora personalizados

### Ejemplo de Extensión - Múltiples Alarmas

```python
class DigitalClockExtended(DigitalClock):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._alarms = []  # Lista de (QTime, mensaje)
    
    def addAlarm(self, time: QTime, message: str):
        self._alarms.append((time, message))
    
    def clearAlarms(self):
        self._alarms.clear()
```

## Troubleshooting

### El reloj no se actualiza

Verifica que el QApplication esté en ejecución:

```python
app = QApplication([])
clock = DigitalClock()
clock.show()
app.exec()  # ⚠️ Necesario para que el timer funcione
```

### El formato AM/PM muestra caracteres extraños

El componente usa formateo manual. Si ves "P" en lugar de "PM", verifica que estés usando la última versión del componente.

### La alarma no suena

Verifica:

```python
clock.alarmEnabled = True  # Debe estar habilitada
clock.alarmTime = QTime(...)  # Hora válida
clock.alarmTriggered.connect(handler)  # Señal conectada
```

### El countdown no se detiene en cero

El componente emite `timerFinished` y se detiene automáticamente. Conecta la señal:

```python
clock.timerFinished.connect(lambda: print("Terminado"))
```

## Licencia

Este componente es parte de la aplicación "Gestión de Torneo de Fútbol".

## Autor

Desarrollado como componente reutilizable para PySide6.

## Versión

- **Versión**: 1.0
- **Última actualización**: Febrero 2026
- **Compatibilidad**: PySide6 6.x, PyQt6 6.x
