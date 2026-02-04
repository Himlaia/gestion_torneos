# Gestión de Torneo de Fútbol

Aplicación de escritorio desarrollada con PySide6 y SQLite para gestionar torneos de fútbol.

## Requisitos

- Python 3.8+
- PySide6

## Instalación

```bash
pip install PySide6
```

## Ejecución

```bash
python main.py
```

## Estructura del Proyecto

```
torneo_futbol/
├── main.py                          # Punto de entrada
├── data/                            # Base de datos SQLite
│   └── torneo.db
├── app/
│   ├── config.py                    # Configuración
│   ├── constants.py                 # Constantes
│   ├── models/                      # Capa de datos
│   │   ├── db.py                    # Gestión de conexión
│   │   └── schema.py                # Esquema y tablas
│   ├── services/                    # Servicios
│   │   └── qss_service.py          # Gestión de temas
│   ├── controllers/                 # Controladores
│   │   └── navigation_controller.py
│   ├── views/                       # Vistas
│   │   ├── main_window.py          # Ventana principal
│   │   ├── page_teams.py           # Gestión de equipos
│   │   ├── page_participants.py    # Gestión de participantes
│   │   ├── page_matches.py         # Calendario/Partidos
│   │   ├── page_bracket.py         # Cuadro de eliminatorias
│   │   ├── page_help.py            # Ayuda
│   │   └── page_credits.py         # Créditos
│   ├── utils/                       # Utilidades
│   └── resources/                   # Recursos
│       └── styles/
│           ├── light.qss           # Tema claro
│           └── dark.qss            # Tema oscuro
```

## Características

- ✅ Arquitectura por capas (Models/Views/Controllers/Services/Utils)
- ✅ Base de datos SQLite con tablas para equipos, participantes, partidos y estadísticas
- ✅ Temas claro y oscuro
- ✅ Navegación entre múltiples páginas
- ✅ Interfaz limpia y moderna con PySide6

## Base de Datos

La base de datos se crea automáticamente al iniciar la aplicación en `data/torneo.db` con las siguientes tablas:

- **equipos**: Información de los equipos
- **participantes**: Jugadores, técnicos y árbitros
- **partidos**: Calendario y resultados
- **estadísticas**: Estadísticas individuales por partido

## Menús

### Torneo
- Gestión de equipos
- Gestión de participantes
- Calendario / Partidos
- Cuadro de eliminatorias

### Ver
- Cambiar tema (Light/Dark)

### Ayuda
- Ayuda
- Créditos
