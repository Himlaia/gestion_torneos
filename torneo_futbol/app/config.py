"""Configuración de la aplicación."""
import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESOURCES_DIR = BASE_DIR / "app" / "resources"
STYLES_DIR = RESOURCES_DIR / "styles"

# Base de datos
DB_NAME = "torneo.db"
DB_PATH = DATA_DIR / DB_NAME

# Tema por defecto
DEFAULT_THEME = "light"

# Asegurar que el directorio de datos existe
DATA_DIR.mkdir(exist_ok=True)
