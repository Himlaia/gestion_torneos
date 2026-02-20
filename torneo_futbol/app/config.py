"""Configuración de la aplicación."""
import os
import sys
import shutil
from pathlib import Path

# Rutas base
if getattr(sys, 'frozen', False):
    # Estamos en un ejecutable empaquetado
    # sys._MEIPASS es el directorio temporal donde PyInstaller desempaqueta los archivos
    BASE_DIR = Path(sys._MEIPASS)
    # DATA_DIR debe estar donde está el .exe para persistencia
    DATA_DIR = Path(sys.executable).parent / "data"
    # Copiar datos empaquetados como semilla junto al .exe
    _bundled_data = BASE_DIR / "data"
    if _bundled_data.exists():
        DATA_DIR.mkdir(exist_ok=True)
        for _f in _bundled_data.iterdir():
            _dest = DATA_DIR / _f.name
            if _f.is_file():
                # Copiar si no existe, o si el empaquetado es mayor (destino vacío/corrupto)
                if not _dest.exists() or _f.stat().st_size > _dest.stat().st_size:
                    shutil.copy2(_f, _dest)
            elif _f.is_dir() and not _dest.exists():
                shutil.copytree(_f, _dest)
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
VERSION = "1.1.0"

# Directorio de informes
# Templates están empaquetados en BASE_DIR, pero los PDFs generados van junto al .exe
REPORTS_TEMPLATES_DIR = BASE_DIR / "reports" / "templates"
if getattr(sys, 'frozen', False):
    REPORTS_DIR = Path(sys.executable).parent / "reports"
else:
    REPORTS_DIR = BASE_DIR / "reports"
REPORTS_GENERATED_DIR = REPORTS_DIR / "generated"

# Asegurar que los directorios necesarios existen
DATA_DIR.mkdir(exist_ok=True)
REPORTS_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
