"""Constantes de la aplicación."""

# Títulos de la aplicación
APP_TITLE = "Gestión de Torneo de Fútbol"
APP_VERSION = "1.0.0"

# Dimensiones de la ventana
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Páginas del QStackedWidget
PAGE_HOME = 0
PAGE_TEAMS = 1
PAGE_PARTICIPANTS = 2
PAGE_MATCHES = 3
PAGE_BRACKET = 4
PAGE_TOOLS = 5
PAGE_HELP = 6
PAGE_CREDITS = 7

# Nombres de páginas
PAGE_NAMES = {
    PAGE_HOME: "Inicio",
    PAGE_TEAMS: "Gestión de Equipos",
    PAGE_PARTICIPANTS: "Gestión de Participantes",
    PAGE_MATCHES: "Calendario / Partidos",
    PAGE_BRACKET: "Cuadro de Eliminatorias",
    PAGE_TOOLS: "Herramientas",
    PAGE_HELP: "Ayuda",
    PAGE_CREDITS: "Créditos"
}

# Fases del torneo (para calendario y bracket)
FASE_OCTAVOS = "octavos"
FASE_CUARTOS = "cuartos"
FASE_SEMIFINAL = "semifinal"
FASE_FINAL = "final"

# Configuración de fases
FASES_CONFIG = {
    FASE_OCTAVOS: {"label": "Octavos", "required": 8, "prev": None},
    FASE_CUARTOS: {"label": "Cuartos", "required": 4, "prev": FASE_OCTAVOS},
    FASE_SEMIFINAL: {"label": "Semifinal", "required": 2, "prev": FASE_CUARTOS},
    FASE_FINAL: {"label": "Final", "required": 1, "prev": FASE_SEMIFINAL}
}

# Orden de fases para combo
FASES_ORDEN = [FASE_OCTAVOS, FASE_CUARTOS, FASE_SEMIFINAL, FASE_FINAL]

# Temas disponibles
THEME_LIGHT = "light"
THEME_DARK = "dark"
