# DigitalClock - Componente Reutilizable PySide6

Componente de reloj digital profesional y completamente portable para aplicaciones PySide6.

## 🎯 Características

- **✅ Sin dependencias externas** - Solo requiere PySide6
- **🎨 Basado en QLCDNumber** - Interfaz LCD realista
- **⚙️ Propiedades con @Property** - Configuración tipo Qt
- **📡 Señales personalizadas** - Eventos de alarma y cronómetro
- **🔄 Dual-mode** - Reloj y cronómetro en un solo componente
- **⏰ Sistema de alarmas** - Configurable con mensajes personalizados
- **⏱️ Cronómetro versátil** - Ascendante y descendente

## 📦 Instalación

Simplemente copia el archivo `digital_clock.py` a tu proyecto. No requiere instalación adicional.

```python
from digital_clock import DigitalClock, ClockMode
```

## 🚀 Uso Básico

### Modo Reloj (CLOCK)

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from digital_clock import DigitalClock, ClockMode

app = QApplication([])
window = QMainWindow()

# Crear reloj
clock = DigitalClock()
clock.mode = ClockMode.CLOCK  # Modo reloj (default)
clock.is24Hour = True          # Formato 24 horas

window.setCentralWidget(clock)
window.show()
app.exec()
```

### Modo Cronómetro (TIMER)

```python
# Cronómetro ascendente (stopwatch)
clock = DigitalClock()
clock.mode = ClockMode.TIMER
clock.setStopwatchMode()
clock.start()  # Inicia conteo

# Cronómetro descendente (countdown)
clock = DigitalClock()
clock.mode = ClockMode.TIMER
clock.setCountdownTime(hours=0, minutes=5, seconds=30)
clock.start()  # Inicia countdown desde 5:30
```

## 🔧 Propiedades

Todas las propiedades usan el decorador `@Property` de PySide6:

| Propiedad | Tipo | Descripción | Default |
|-----------|------|-------------|---------|
| `mode` | `str/ClockMode` | Modo del reloj: "clock" o "timer" | `CLOCK` |
| `is24Hour` | `bool` | Formato 24h (True) o 12h (False) | `True` |
| `alarmEnabled` | `bool` | Activa/desactiva alarma | `False` |
| `alarmTime` | `QTime` | Hora de la alarma | `00:00:00` |
| `alarmMessage` | `str` | Mensaje al disparar alarma | `"¡Alarma!"` |

### Ejemplo de Propiedades

```python
from PySide6.QtCore import QTime

clock = DigitalClock()

# Configurar modo
clock.mode = ClockMode.CLOCK
# O con string
clock.mode = "timer"

# Configurar formato
clock.is24Hour = False  # Formato 12h con AM/PM

# Configurar alarma
clock.alarmTime = QTime(14, 30, 0)  # 2:30 PM
clock.alarmMessage = "¡Hora de la reunión!"
clock.alarmEnabled = True
```

## 📡 Señales

El componente emite las siguientes señales:

### `alarmTriggered(str)`
Se emite cuando la alarma se dispara.

```python
def on_alarm(message):
    print(f"Alarma: {message}")

clock.alarmTriggered.connect(on_alarm)
```

### `timerFinished()`
Se emite cuando el countdown llega a cero.

```python
def on_timer_done():
    print("¡Tiempo terminado!")

clock.timerFinished.connect(on_timer_done)
```

## 🎮 Métodos Públicos

### Control del Cronómetro

| Método | Descripción |
|--------|-------------|
| `start()` | Inicia o reanuda el cronómetro |
| `pause()` | Pausa el cronómetro |
| `reset()` | Resetea el cronómetro a 0 |

### Configuración del Cronómetro

| Método | Parámetros | Descripción |
|--------|------------|-------------|
| `setCountdownTime()` | `hours, minutes, seconds` | Configura tiempo para countdown |
| `setStopwatchMode()` | - | Configura modo ascendente |
| `isRunning()` | - | Retorna True si está corriendo |
| `isPaused()` | - | Retorna True si está pausado |
| `getElapsedTime()` | - | Retorna segundos transcurridos |

### Ejemplo Completo de Control

```python
clock = DigitalClock()
clock.mode = ClockMode.TIMER

# Configurar countdown de 2 minutos
clock.setCountdownTime(minutes=2)

# Controlar ejecución
clock.start()   # Inicia
clock.pause()   # Pausa
clock.start()   # Reanuda
clock.reset()   # Vuelve a 2:00

# Consultar estado
if clock.isRunning():
    print(f"Tiempo restante: {clock.getElapsedTime()}s")
```

## 📝 Ejemplos Avanzados

### Reloj con Alarma Múltiple

```python
from PySide6.QtCore import QTime

clock = DigitalClock()
clock.mode = ClockMode.CLOCK
clock.is24Hour = True

def set_alarm(hour, minute, message):
    clock.alarmTime = QTime(hour, minute, 0)
    clock.alarmMessage = message
    clock.alarmEnabled = True

def on_alarm_triggered(msg):
    print(f"🔔 {msg}")
    # Aquí puedes mostrar notificación, reproducir sonido, etc.

clock.alarmTriggered.connect(on_alarm_triggered)

# Configurar alarma
set_alarm(hour=8, minute=30, message="¡Hora de despertar!")
```

### Cronómetro Pomodoro

```python
class PomodoroTimer:
    def __init__(self):
        self.clock = DigitalClock()
        self.clock.mode = ClockMode.TIMER
        self.clock.timerFinished.connect(self.on_pomodoro_done)
        
    def start_work_session(self):
        """25 minutos de trabajo"""
        self.clock.setCountdownTime(minutes=25)
        self.clock.start()
        
    def start_break(self):
        """5 minutos de descanso"""
        self.clock.setCountdownTime(minutes=5)
        self.clock.start()
        
    def on_pomodoro_done(self):
        print("¡Sesión terminada!")
        # Alternar entre trabajo y descanso

pomodoro = PomodoroTimer()
pomodoro.start_work_session()
```

### Timer de Ejercicio

```python
class WorkoutTimer:
    def __init__(self):
        self.clock = DigitalClock()
        self.clock.mode = ClockMode.TIMER
        self.clock.setStopwatchMode()
        
    def start_exercise(self):
        self.clock.reset()
        self.clock.start()
        
    def get_duration(self):
        total_seconds = self.clock.getElapsedTime()
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

workout = WorkoutTimer()
workout.start_exercise()
# ... después del ejercicio
print(f"Duración: {workout.get_duration()}")
```

## 🎨 Personalización Visual

### Cambiar Estilo del LCD

```python
from PySide6.QtWidgets import QLCDNumber

clock = DigitalClock()

# Estilos disponibles
clock.setSegmentStyle(QLCDNumber.Flat)      # Plano (default)
clock.setSegmentStyle(QLCDNumber.Outline)   # Contorno
clock.setSegmentStyle(QLCDNumber.Filled)    # Relleno

# Tamaño
clock.setDigitCount(8)  # HH:MM:SS
clock.setMinimumHeight(100)

# Color (con stylesheet)
clock.setStyleSheet("""
    QLCDNumber {
        background-color: #000;
        color: #0f0;  /* Verde neón */
    }
""")
```

### Integración con Temas

```python
# Tema oscuro
clock.setStyleSheet("""
    QLCDNumber {
        background-color: #1e1e1e;
        color: #00d4ff;
        border: 2px solid #333;
        border-radius: 5px;
    }
""")

# Tema claro
clock.setStyleSheet("""
    QLCDNumber {
        background-color: #f0f0f0;
        color: #333;
        border: 1px solid #ccc;
    }
""")
```

## 🔍 Casos de Uso

1. **Aplicaciones de productividad** - Pomodoro, time tracking
2. **Sistemas de timing** - Deportes, competencias
3. **Paneles de control** - Dashboards, monitoreo
4. **Aplicaciones educativas** - Temporizadores de examen
5. **Sistemas de alarma** - Recordatorios, notificaciones
6. **Fitness apps** - Intervalos de entrenamiento

## ⚡ Rendimiento

- **Bajo consumo de recursos** - Actualización cada 1 segundo
- **Eficiente** - Usa QTimer nativo de Qt
- **No bloquea la UI** - Ejecución asíncrona

## 🐛 Troubleshooting

### La alarma no suena
- Verifica que `alarmEnabled = True`
- Asegúrate de estar en modo `ClockMode.CLOCK`
- Conecta la señal `alarmTriggered`

### El cronómetro no inicia
- Verifica que estás en modo `ClockMode.TIMER`
- Para countdown, configura tiempo con `setCountdownTime()`
- Llama a `start()` después de configurar

### Formato 12h no funciona
- Asegúrate de tener `is24Hour = False`
- Solo funciona en modo `ClockMode.CLOCK`
- El formato AM/PM se añade automáticamente

## 📄 Licencia

Componente de código abierto. Libre para usar en proyectos personales y comerciales.

## 🤝 Contribución

Este componente es completamente standalone y no requiere dependencias externas más allá de PySide6.

---

**Versión:** 1.0.0  
**Última actualización:** 2026  
**Compatibilidad:** PySide6 (Qt 6.x)
