"""Configuración de la aplicación."""
import os
import sys
from pathlib import Path

# Rutas base
if getattr(sys, 'frozen', False):
    # Estamos en un ejecutable empaquetado
    # sys._MEIPASS es el directorio temporal donde PyInstaller desempaqueta los archivos
    BASE_DIR = Path(sys._MEIPASS)
    # DATA_DIR debe estar donde está el .exe para persistencia
    DATA_DIR = Path(sys.executable).parent / "data"
else:
    # Estamos en desarrollo
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"

RESOURCES_DIR = BASE_DIR / "app" / "resources"
STYLES_DIR = RESOURCES_DIR / "styles"

# Directorio de traducciones
# Las traducciones siempre están en BASE_DIR/translations
# (en desarrollo es la carpeta del proyecto, empaquetado es sys._MEIPASS)
TRANSLATIONS_DIR = BASE_DIR / "translations"

# Base de datos
DB_NAME = "torneo.db"
DB_PATH = DATA_DIR / DB_NAME

# Tema por defecto
DEFAULT_THEME = "light"

# Idioma por defecto
DEFAULT_LANGUAGE = "es"  # Español por defecto
AVAILABLE_LANGUAGES = {
    "es": "Español",
    "en": "English"
}

# Versión de la aplicación
VERSION = "1.0.0"

# Asegurar que el directorio de datos existe
DATA_DIR.mkdir(exist_ok=True)
