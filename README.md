# ⚽ Gestión de Torneo de Fútbol

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.0%2B-green)
![SQLite](https://img.shields.io/badge/SQLite-3-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Aplicación de escritorio profesional desarrollada con **PySide6** y **SQLite** para la gestión completa de torneos de fútbol de eliminatorias. Diseñada con arquitectura MVC (Modelo-Vista-Controlador) y servicios independientes.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Ejecución](#-ejecución)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Base de Datos](#-base-de-datos)
- [Componente Reutilizable](#-componente-reutilizable-digitalclock)
- [Distribución y Entregables](#-distribución-y-entregables)
- [Documentación Técnica](#-documentación-técnica)

---

## ✨ Características

### Funcionalidades Principales

- **Gestión de Equipos**
  - CRUD completo de equipos
  - Carga de escudos/logos (PNG, JPG, SVG)
  - Asignación de colores y cursos
  - Visualización de jugadores por equipo

- **Gestión de Participantes**
  - Registro de jugadores y árbitros
  - Soporte para roles duales (jugador/árbitro)
  - Estadísticas automáticas (goles, tarjetas, partidos jugados)
  - Filtrado por tipo (jugadores/árbitros)
  - Posiciones de juego (Portero, Defensa, Centrocampista, Delantero)

- **Calendario y Partidos**
  - Vista de calendario con marcadores de días con partidos
  - Generación automática de torneo de 16 equipos
  - Programación manual de partidos
  - Gestión de convocatorias por partido
  - Registro detallado de resultados (goles, tarjetas, minutos)
  - Desempate por penaltis

- **Cuadro de Eliminatorias**
  - Visualización gráfica del bracket completo
  - Actualización automática al guardar resultados
  - Avance automático de ganadores a siguientes rondas
  - Creación automática de partidos de rondas posteriores
  - Soporte para Octavos, Cuartos, Semifinales y Final

### Características Técnicas

- ✅ **Arquitectura MVC** con separación clara de responsabilidades
- ✅ **Event Bus** para comunicación desacoplada entre módulos
- ✅ **Servicios independientes** (TournamentService, MatchService)
- ✅ **Temas claro y oscuro** con QSS personalizado
- ✅ **Persistencia automática** con SQLite
- ✅ **Validaciones robustas** en todos los formularios
- ✅ **Manejo de errores** con mensajes informativos
- ✅ **Tooltips** y ayuda contextual
- ✅ **Interfaz responsive** y moderna

---

## 🔧 Requisitos

### Requisitos del Sistema

- **Sistema Operativo**: Windows 10+, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.8 o superior (recomendado 3.11+)
- **Espacio en disco**: 50 MB mínimo
- **RAM**: 512 MB mínimo (1 GB recomendado)

### Dependencias de Python

```txt
PySide6>=6.0.0
```

---

## 📥 Instalación

### Opción 1: Instalación desde el código fuente

1. **Clonar el repositorio**:
```bash
git clone https://github.com/Himlaia/gestion_torneos.git
cd gestion_torneos/torneo_futbol
```

2. **Crear un entorno virtual** (recomendado):
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

### Opción 2: Ejecutable (próximamente)

Descarga el archivo `.exe` (Windows) o `.deb` (Linux) desde la sección de [Releases](https://github.com/Himlaia/gestion_torneos/releases).

---

## 🚀 Ejecución

### Modo Desarrollo

```bash
python main.py
```

### Modo Producción (ejecutable)

- **Windows**: Doble clic en `torneo_futbol.exe`
- **Linux**: `./torneo_futbol`

---

## 🏗️ Arquitectura del Proyecto

### Estructura de Directorios

```
torneo_futbol/
├── main.py                          # Punto de entrada de la aplicación
├── requirements.txt                 # Dependencias de Python
├── README.md                        # Documentación técnica
│
├── data/                            # Datos persistentes
│   ├── torneo.db                    # Base de datos SQLite
│   └── escudos/                     # Imágenes de escudos de equipos
│
├── app/
│   ├── __init__.py
│   ├── config.py                    # Configuración global (rutas, constantes)
│   ├── constants.py                 # Constantes de la aplicación (fases, estados)
│   │
│   ├── models/                      # Capa de datos (ORM/Data Access)
│   │   ├── __init__.py
│   │   ├── db.py                    # Gestión de conexión a SQLite
│   │   ├── schema.py                # Definición de esquema y tablas
│   │   ├── team_model.py            # CRUD de equipos
│   │   ├── participant_model.py     # CRUD de participantes
│   │   ├── match_model.py           # CRUD de partidos
│   │   ├── callup_model.py          # CRUD de convocatorias
│   │   ├── goal_model.py            # CRUD de goles
│   │   └── match_stats_model.py     # CRUD de estadísticas
│   │
│   ├── services/                    # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── event_bus.py             # Sistema de eventos desacoplado
│   │   ├── tournament_service.py    # Lógica del torneo (avance de rondas)
│   │   ├── match_service.py         # Lógica de partidos (validaciones)
│   │   └── qss_service.py           # Gestión de temas (light/dark)
│   │
│   ├── controllers/                 # Controladores (lógica de presentación)
│   │   ├── __init__.py
│   │   ├── navigation_controller.py # Navegación entre páginas
│   │   ├── teams_controller.py      # Controlador de equipos
│   │   ├── participants_controller.py # Controlador de participantes
│   │   ├── matches_controller.py    # Controlador de partidos
│   │   └── bracket_controller.py    # Controlador del cuadro
│   │
│   ├── views/                       # Vistas (interfaz de usuario)
│   │   ├── __init__.py
│   │   ├── main_window.py           # Ventana principal con menús
│   │   ├── page_home.py             # Página de inicio (dashboard)
│   │   ├── page_teams.py            # Gestión de equipos
│   │   ├── page_participants.py     # Gestión de participantes
│   │   ├── page_matches.py          # Calendario/Partidos
│   │   ├── page_bracket.py          # Cuadro de eliminatorias
│   │   ├── page_help.py             # Ayuda
│   │   ├── page_credits.py          # Créditos
│   │   │
│   │   ├── dialogs/                 # Diálogos modales
│   │   │   ├── dialog_goles_detalle.py # Asignar goles a jugadores
│   │   │   └── dialog_partidos_dia.py  # Ver partidos de un día
│   │   │
│   │   └── widgets/                 # Widgets personalizados
│   │       ├── calendario_widget.py # Widget de calendario
│   │       └── team_selector.py     # Selector de equipos
│   │
│   ├── utils/                       # Utilidades
│   │   └── __init__.py
│   │
│   └── resources/                   # Recursos estáticos
│       ├── styles/
│       │   ├── light.qss            # Tema claro
│       │   └── dark.qss             # Tema oscuro
│       ├── fonts/                   # Fuentes personalizadas
│       └── img/                     # Imágenes de la aplicación
```

### Patrón de Arquitectura

La aplicación sigue el patrón **MVC (Model-View-Controller)** con una capa adicional de **Services**:

1. **Models** (`app/models/`): Acceso a datos y persistencia
   - Interacción directa con SQLite
   - Operaciones CRUD
   - Sin lógica de negocio

2. **Services** (`app/services/`): Lógica de negocio
   - Validaciones complejas
   - Automatizaciones (avance de rondas, cálculo de ganadores)
   - Comunicación entre módulos vía EventBus

3. **Controllers** (`app/controllers/`): Coordinación
   - Conecta vistas con modelos y servicios
   - Manejo de eventos de UI
   - Validación de formularios

4. **Views** (`app/views/`): Interfaz de usuario
   - Solo código de presentación
   - No contiene lógica de negocio
   - Emite señales que capturan los controladores

---

## 🗄️ Base de Datos

### Esquema de la Base de Datos

La aplicación utiliza **SQLite** como base de datos embebida. El esquema se crea automáticamente al iniciar la aplicación.

#### Tabla: `equipos`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Identificador único |
| nombre | TEXT NOT NULL | Nombre del equipo |
| curso | TEXT | Curso asociado |
| color | TEXT | Color de camiseta (formato hex) |
| escudo | TEXT | Ruta al archivo de escudo |

#### Tabla: `participantes`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Identificador único |
| nombre | TEXT NOT NULL | Nombre del participante |
| apellidos | TEXT | Apellidos |
| fecha_nacimiento | TEXT | Fecha de nacimiento (ISO) |
| curso | TEXT | Curso del participante |
| es_jugador | INTEGER | 1 si es jugador, 0 si no |
| es_arbitro | INTEGER | 1 si es árbitro, 0 si no |
| posicion | TEXT | Posición en el campo (si es jugador) |
| equipo_id | INTEGER | FK a equipos |
| goles_totales | INTEGER DEFAULT 0 | Goles marcados (calculado) |
| amarillas_totales | INTEGER DEFAULT 0 | Tarjetas amarillas (calculado) |
| rojas_totales | INTEGER DEFAULT 0 | Tarjetas rojas (calculado) |
| partidos_jugados | INTEGER DEFAULT 0 | Partidos jugados (calculado) |

#### Tabla: `partidos`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Identificador único |
| eliminatoria | TEXT NOT NULL | octavos, cuartos, semifinal, final |
| slot | INTEGER | Número de partido en la ronda (1-8) |
| fecha_hora | TEXT | Fecha y hora del partido (ISO) |
| equipo_local_id | INTEGER | FK a equipos (local) |
| equipo_visitante_id | INTEGER | FK a equipos (visitante) |
| arbitro_id | INTEGER | FK a participantes (árbitro) |
| goles_local | INTEGER DEFAULT 0 | Goles del equipo local |
| goles_visitante | INTEGER DEFAULT 0 | Goles del equipo visitante |
| penaltis_local | INTEGER | Goles en penaltis (si aplica) |
| penaltis_visitante | INTEGER | Goles en penaltis (si aplica) |
| ganador_equipo_id | INTEGER | FK a equipos (ganador) |
| estado | TEXT DEFAULT 'Pendiente' | Pendiente, Programado, Jugado |

#### Tabla: `convocados`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Identificador único |
| partido_id | INTEGER NOT NULL | FK a partidos |
| equipo_id | INTEGER NOT NULL | FK a equipos |
| participante_id | INTEGER NOT NULL | FK a participantes |

**Constraint**: UNIQUE(partido_id, participante_id)

#### Tabla: `goles`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Identificador único |
| partido_id | INTEGER NOT NULL | FK a partidos |
| participante_id | INTEGER NOT NULL | FK a participantes (goleador) |
| equipo_id | INTEGER NOT NULL | FK a equipos |
| minuto | INTEGER | Minuto del gol (opcional) |

#### Tabla: `estadisticas_partidos`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Identificador único |
| partido_id | INTEGER NOT NULL | FK a partidos |
| participante_id | INTEGER NOT NULL | FK a participantes |
| goles | INTEGER DEFAULT 0 | Goles en este partido |
| amarillas | INTEGER DEFAULT 0 | Tarjetas amarillas |
| rojas | INTEGER DEFAULT 0 | Tarjetas rojas |

**Constraint**: UNIQUE(partido_id, participante_id)

### Relaciones

- `participantes.equipo_id` → `equipos.id` (Many-to-One)
- `partidos.equipo_local_id` → `equipos.id` (Many-to-One)
- `partidos.equipo_visitante_id` → `equipos.id` (Many-to-One)
- `partidos.arbitro_id` → `participantes.id` (Many-to-One)
- `partidos.ganador_equipo_id` → `equipos.id` (Many-to-One)
- `convocados.partido_id` → `partidos.id` (Many-to-One)
- `convocados.equipo_id` → `equipos.id` (Many-to-One)
- `convocados.participante_id` → `participantes.id` (Many-to-One)
- `goles.partido_id` → `partidos.id` (Many-to-One)
- `goles.participante_id` → `participantes.id` (Many-to-One)
- `goles.equipo_id` → `equipos.id` (Many-to-One)
- `estadisticas_partidos.partido_id` → `partidos.id` (Many-to-One)
- `estadisticas_partidos.participante_id` → `participantes.id` (Many-to-One)

---

## 📚 Documentación Técnica

### EventBus - Sistema de Eventos

El sistema de eventos desacoplado permite la comunicación entre módulos sin dependencias directas:

```python
# Emitir un evento
from app.services.event_bus import get_event_bus
event_bus = get_event_bus()
event_bus.emit_result_saved(partido_id)

# Escuchar un evento
event_bus.result_saved.connect(self._on_result_saved)
```

**Eventos disponibles**:
- `team_created`, `team_updated`, `team_deleted`
- `participant_created`, `participant_updated`, `participant_deleted`
- `match_created`, `match_updated`, `match_deleted`
- `result_saved` - Cuando se guarda un resultado
- `phase_advanced` - Cuando avanza a siguiente ronda
- `bracket_updated` - Cuando se actualiza el cuadro

### TournamentService - Lógica del Torneo

Gestiona la lógica de avance de rondas y creación automática de partidos:

```python
from app.services.tournament_service import TournamentService

# Generar octavos automáticamente
emparejamientos = TournamentService.randomizar_octavos(equipos_ids)
TournamentService.generar_octavos_desde_emparejamientos(emparejamientos)

# Propagar ganador automáticamente
TournamentService.propagate_winner(partido_id)
```

**Funciones clave**:
- `randomizar_octavos()` - Genera emparejamientos aleatorios
- `generar_octavos_desde_emparejamientos()` - Crea partidos en BD
- `avanzar_ronda()` - Avanza ganador a siguiente ronda
- `propagate_winner()` - Propaga ganador y crea partido siguiente

### MatchService - Lógica de Partidos

Valida y guarda resultados con todas las reglas de negocio:

```python
from app.services.match_service import MatchService

# Guardar resultado con goles y estadísticas
resultado = MatchService.save_result_with_goals(
    partido_id=1,
    goles_local=2,
    goles_visitante=1,
    penaltis_local=None,
    penaltis_visitante=None,
    goles_detalle=[...],  # Lista de goles con autor
    stats=[...]  # Estadísticas de jugadores
)
```

### Temas - QSS Service

Gestión de temas claro y oscuro:

```python
from app.services.qss_service import QSSService

# Aplicar tema
QSSService.aplicar_tema(main_window, "dark")  # o "light"

# Cambiar tema
QSSService.toggle_theme(main_window)
```

---

## 🧩 Componente Reutilizable: DigitalClock

Este proyecto incluye un **componente reutilizable completamente independiente** desarrollado como parte de la aplicación.

### Descripción del Componente

**DigitalClock** es un widget de PySide6 que hereda de `QLCDNumber` y proporciona:

- ⏰ **Modo Reloj**: Muestra la hora actual con formato 12h/24h
- ⏱️ **Modo Cronómetro Ascendente**: Stopwatch
- ⏲️ **Modo Cronómetro Descendente**: Countdown con notificaciones
- 🔔 **Sistema de Alarmas**: Configurables con popups
- 🎨 **Completamente Personalizable**: Usa Qt Properties
- 📦 **Sin Dependencias Externas**: Solo requiere PySide6

### Ubicación del Código

```
torneo_futbol/app/views/widgets/
├── digital_clock.py          # Código fuente del componente
└── README.md                 # Documentación completa del componente
```

### Uso Básico

```python
from app.views.widgets.digital_clock import DigitalClock, ClockMode

# Crear reloj
clock = DigitalClock()
clock.mode = ClockMode.CLOCK
clock.is24Hour = True

# Configurar alarma
clock.alarmEnabled = True
clock.alarmTime = QTime(14, 30, 0)
clock.alarmTriggered.connect(lambda msg: print(f"Alarma: {msg}"))

# Usar como cronómetro
clock.mode = ClockMode.TIMER
clock.setCountdownTime(hours=0, minutes=5, seconds=0)
clock.start()
```

### Demo Standalone

El proyecto incluye una **aplicación demo independiente** (`demo_digital_clock.py`) que muestra todas las capacidades del componente de forma interactiva.

Para más detalles, consulta la documentación completa en:
📄 `torneo_futbol/app/views/widgets/README.md`

---

## 📦 Distribución y Entregables

### Entregables del Proyecto

Este proyecto genera **DOS ejecutables** que deben entregarse:

1. **TorneoFutbol.exe** - Aplicación completa de gestión de torneos
2. **DigitalClock_Demo.exe** - Demo standalone del componente reutilizable

### 🚀 Generación Automática de Ejecutables

#### Opción 1: Generar Ambos Ejecutables (Recomendado)

Desde PowerShell en el directorio raíz del proyecto:

```powershell
cd torneo_futbol
.\scripts\build_all.ps1
```

Este script:
- ✅ Compila `TorneoFutbol.exe` (aplicación completa)
- ✅ Compila `DigitalClock_Demo.exe` (demo del componente)
- ✅ Crea carpeta `entrega_final/` con todo listo para entregar
- ✅ Incluye código fuente del componente y README

**Resultado:**
```
entrega_final/
├── TorneoFutbol.exe              # Ejecutable aplicación completa
├── DigitalClock_Demo.exe         # Ejecutable demo componente
├── README.md                     # Instrucciones
└── componente_codigo_fuente/
    ├── digital_clock.py          # Código fuente del componente
    └── README.md                 # Documentación del componente
```

#### Opción 2: Compilar Solo la Aplicación Completa

```powershell
.\scripts\build.ps1
```

Genera: `dist/TorneoFutbol.exe`

#### Opción 3: Compilar Solo el Demo del Componente

```powershell
.\scripts\build_demo.ps1
```

Genera: `dist/DigitalClock_Demo.exe`

### 📋 Requisitos para Compilar

```bash
# Instalar PyInstaller (si no está instalado)
pip install pyinstaller

# Verificar instalación
pyinstaller --version
```

### 🎯 Estructura de Entrega para Evaluación

Para cumplir con los requisitos de entrega:

1. Ejecuta `.\scripts\build_all.ps1`
2. Comprime la carpeta `entrega_final/` en un archivo ZIP
3. El ZIP contendrá:
   - ✅ Proyecto completo como `.exe`
   - ✅ Componente reutilizable como `.exe` demo
   - ✅ Código fuente del componente (`.py`)
   - ✅ Documentación completa (README)
   - ✅ Todo el código fuente del proyecto MVC

### ⚙️ Archivos de Configuración de PyInstaller

El proyecto incluye archivos `.spec` preconfigurados:

- `torneo_futbol.spec` - Configuración para aplicación completa
- `demo_digital_clock.spec` - Configuración para demo del componente

### 🖥️ Ejecutar los Archivos .exe

Ambos ejecutables son **completamente independientes** y funcionan con doble clic:

- **TorneoFutbol.exe**: Abre la aplicación completa de gestión de torneos
- **DigitalClock_Demo.exe**: Abre la demo interactiva del componente

**Características:**
- ✅ Sin instalación necesaria
- ✅ Sin configuración previa
- ✅ Sin necesidad de tener Python instalado
- ✅ Portables (se pueden copiar a cualquier PC Windows)

### 🔧 Compilación Manual (Avanzada)

Si prefieres compilar manualmente:

```bash
# Aplicación completa
pyinstaller --clean torneo_futbol.spec

# Demo del componente
pyinstaller --clean demo_digital_clock.spec
```

### 📐 Tamaños Aproximados

- **TorneoFutbol.exe**: ~50-70 MB
- **DigitalClock_Demo.exe**: ~40-60 MB

*Los tamaños varían según la versión de PySide6 y el sistema operativo.*

### ⚠️ Notas Importantes

1. **Primera ejecución**: Puede tardar unos segundos en iniciar mientras se descomprimen las librerías
2. **Antivirus**: Algunos antivirus pueden marcar los ejecutables como sospechosos (falso positivo). Esto es normal con PyInstaller
3. **Base de datos**: La aplicación crea automáticamente la base de datos `data/torneo.db` en la primera ejecución
4. **Escudos**: La carpeta `data/escudos/` se crea automáticamente para almacenar logos de equipos

---

## 🧪 Testing (próximamente)

```bash
# Instalar dependencias de testing
pip install pytest pytest-qt

# Ejecutar tests
pytest tests/
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👥 Autor

- **Himlaia** - [GitHub](https://github.com/Himlaia)

---

## 📞 Soporte

Para reportar bugs o solicitar features, por favor abre un [issue](https://github.com/Himlaia/gestion_torneos/issues).