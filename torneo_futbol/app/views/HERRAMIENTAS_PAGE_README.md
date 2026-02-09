# Página de Herramientas - DigitalClock

Documentación de la nueva página **Herramientas** integrada en el sistema de Gestión de Torneos.

## 📍 Ubicación en la Aplicación

- **Menú:** Torneo → Herramientas
- **Posición:** Entre "Cuadro de eliminatorias" y el menú "Ayuda"
- **Constante:** `PAGE_TOOLS = 5`

## 🎯 Funcionalidad

La página de Herramientas proporciona un reloj digital configurable con las siguientes capacidades:

### **Modo Reloj (CLOCK)**
- Muestra la hora actual del sistema
- Formato 12h (AM/PM) o 24h
- Sistema de alarmas con mensaje personalizado

### **Modo Cronómetro (TIMER)**
- **Stopwatch (Ascendente):** Cuenta desde 0 hacia adelante
- **Countdown (Descendente):** Cuenta regresiva desde un tiempo configurado
- Controles: Iniciar, Pausar, Resetear
- Notificación cuando el countdown termina

## 🖥️ Controles de la Interfaz

### Panel de Configuración de Reloj
| Control | Tipo | Función |
|---------|------|---------|
| **Formato 24 horas** | QCheckBox | Alterna entre formato 12h/24h |
| **Activar alarma** | QCheckBox | Habilita/deshabilita el sistema de alarmas |
| **Hora** | QTimeEdit | Configura la hora de la alarma (HH:mm:ss) |
| **Mensaje** | QLineEdit | Personaliza el mensaje de la alarma |

### Panel de Configuración de Cronómetro
| Control | Tipo | Función |
|---------|------|---------|
| **Ascendente** | QRadioButton | Activa modo stopwatch |
| **Descendente** | QRadioButton | Activa modo countdown |
| **Horas/Minutos/Segundos** | QSpinBox | Configura tiempo del countdown |
| **▶ Iniciar** | QPushButton | Inicia/reanuda el cronómetro |
| **⏸ Pausar** | QPushButton | Pausa el cronómetro |
| **⏹ Resetear** | QPushButton | Resetea a 0 o al tiempo configurado |

## 🔧 Implementación Técnica

### Archivos Modificados

1. **`app/constants.py`**
   ```python
   PAGE_TOOLS = 5  # Nueva constante
   PAGE_HELP = 6   # Actualizado de 5
   PAGE_CREDITS = 7  # Actualizado de 6
   ```

2. **`app/views/main_window.py`**
   - Import de `PAGE_TOOLS` y `PageTools`
   - Instanciación de `self.page_tools = PageTools()`
   - Añadido al `stacked_widget` en índice 5
   - Nueva acción en el menú "Torneo → Herramientas"

3. **`app/views/page_tools.py`** _(Nuevo)_
   - Hereda de `QWidget`
   - Instancia `DigitalClock` del módulo widgets
   - Interfaz completa de configuración

### Uso del Componente DigitalClock

```python
# Instanciación en PageTools
self.digital_clock = DigitalClock()

# Configuración de propiedades (usando @Property)
self.digital_clock.mode = ClockMode.CLOCK
self.digital_clock.is24Hour = True
self.digital_clock.alarmEnabled = False
self.digital_clock.alarmTime = QTime(10, 30, 0)
self.digital_clock.alarmMessage = "¡Alarma!"

# Métodos públicos (solo para modo TIMER)
self.digital_clock.start()    # Iniciar
self.digital_clock.pause()    # Pausar
self.digital_clock.reset()    # Resetear

# Configuración de cronómetro
self.digital_clock.setStopwatchMode()
self.digital_clock.setCountdownTime(hours=0, minutes=5, seconds=0)

# Señales
self.digital_clock.alarmTriggered.connect(self._on_alarm_triggered)
self.digital_clock.timerFinished.connect(self._on_timer_finished)
```

## 📊 Integración con el Sistema

### Navegación

La página se integra perfectamente con el sistema de navegación existente:

```python
# Desde cualquier parte de la aplicación
self.navigate_to_page(PAGE_TOOLS)

# Desde el menú
Torneo → Herramientas
```

### Señales del Componente

**`alarmTriggered(str)`**
- Se emite cuando la alarma se dispara
- Parámetro: mensaje configurado en `alarmMessage`
- Actualiza el status label con estilo naranja

**`timerFinished()`**
- Se emite cuando el countdown llega a 0
- Habilita botón "Iniciar" y deshabilita "Pausar"
- Actualiza el status label con estilo naranja

### Indicadores Visuales

El status label cambia de color según el estado:

| Estado | Color | Descripción |
|--------|-------|-------------|
| Normal | Gris | Estado estándar |
| Advertencia | Amarillo | Alarma activada |
| Ejecutando | Verde | Cronómetro en marcha |
| Alarma | Naranja | Alarma disparada o countdown terminado |

## 🎨 Estilos CSS

La página utiliza los mismos objectNames que las demás páginas:

- `pageRoot` - Widget raíz
- `titleLabel` - Título principal "Herramientas"
- `contentCard` - Tarjeta de contenido
- `subtitleLabel` - Subtítulo "Reloj Digital Configurable"
- `statusLabel` - Label de estado con estilos dinámicos

## 🚀 Ejemplo de Uso

### Configurar una alarma para dentro de 5 minutos

1. Ir a **Torneo → Herramientas**
2. Asegurar que **Modo Reloj** esté seleccionado
3. Activar **Activar alarma**
4. En **Hora**, configurar la hora actual + 5 minutos
5. En **Mensaje**, escribir "¡Reunión en 5 minutos!"
6. Esperar a que suene la alarma

### Usar un countdown de 2 minutos

1. Ir a **Torneo → Herramientas**
2. Seleccionar **Cronómetro**
3. Seleccionar **Descendente (Countdown)**
4. Configurar: Minutos = 2
5. Clic en **▶ Iniciar**
6. El reloj contará 2:00 → 0:00
7. Se notificará cuando termine

## 📝 Notas Técnicas

### Propiedades Públicas Usadas

Todas las configuraciones usan las propiedades `@Property` del componente:

- `mode` → Cambio entre CLOCK/TIMER
- `is24Hour` → Formato de hora
- `alarmEnabled` → Activar/desactivar alarma
- `alarmTime` → Hora de la alarma
- `alarmMessage` → Mensaje personalizado

### Métodos Públicos Usados

Solo se usan los métodos públicos del componente:

- `start()` → Para iniciar cronómetro
- `pause()` → Para pausar cronómetro
- `reset()` → Para resetear cronómetro
- `setStopwatchMode()` → Configurar modo ascendente
- `setCountdownTime()` → Configurar modo descendente

**No se accede a ningún atributo privado** del componente, manteniendo la encapsulación.

## 🔍 Verificación

Para verificar que la integración funciona correctamente:

```bash
cd torneo_futbol
python main.py
```

Luego:
1. Menú **Torneo** → **Herramientas**
2. Verificar que el reloj muestra la hora actual
3. Probar cambio entre modos
4. Probar alarma con tiempo corto (10 segundos)
5. Probar cronómetro ascendente
6. Probar countdown

---

**Versión:** 1.0.0  
**Fecha:** Febrero 2026  
**Integración:** Completa y funcional
