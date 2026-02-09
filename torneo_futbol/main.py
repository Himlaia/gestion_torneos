"""Punto de entrada de la aplicación."""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTranslator, QLocale

from app.models.db import init_db, DbError
from app.services.qss_service import qss_service
from app.config import DEFAULT_THEME, DEFAULT_LANGUAGE, TRANSLATIONS_DIR
from app.views.main_window import MainWindow


def load_translations(app: QApplication, language: str = None) -> QTranslator:
    """
    Carga las traducciones de la aplicación.
    
    Args:
        app: Instancia de QApplication
        language: Código de idioma (es, en, etc). Si es None, usa DEFAULT_LANGUAGE
    
    Returns:
        QTranslator configurado
    """
    if language is None:
        language = DEFAULT_LANGUAGE
    
    translator = QTranslator(app)
    
    # Ruta al directorio de traducciones
    translations_path = Path(TRANSLATIONS_DIR)
    
    # Intentar cargar archivo .qm (compilado) primero
    qm_file = translations_path / f"torneo_{language}.qm"
    
    if qm_file.exists():
        if translator.load(str(qm_file)):
            app.installTranslator(translator)
            print(f"✓ Traducción cargada (.qm): {language} ({qm_file.name})")
            return translator
        else:
            print(f"⚠ No se pudo cargar .qm: {qm_file}")
    
    # Fallback: intentar cargar archivo .ts (fuente)
    # QTranslator puede cargar .ts directamente en desarrollo
    ts_file = translations_path / f"torneo_{language}"
    
    if translator.load(str(ts_file), str(translations_path)):
        app.installTranslator(translator)
        print(f"✓ Traducción cargada (.ts): {language}")
        print(f"  ℹ Usando archivo .ts (desarrollo). Para mejor rendimiento,")
        print(f"    compila a .qm con: pyside6-lrelease")
        return translator
    
    # Si no se encontró ninguna traducción
    print(f"⚠ Archivo de traducción no encontrado: {language}")
    print(f"  Buscado: {qm_file} y {ts_file}.ts")
    print(f"  La aplicación usará los textos por defecto (español)")
    
    return translator


def main():
    """Función principal de la aplicación."""
    # Crear aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("Torneo de Fútbol")
    app.setOrganizationName("DAM")
    
    # Cargar traducciones
    translator = load_translations(app, DEFAULT_LANGUAGE)
    
    # Inicializar base de datos
    print("Inicializando base de datos...")
    try:
        init_db()
    except DbError as e:
        QMessageBox.critical(
            None,
            "Error de base de datos",
            f"No se pudo inicializar la base de datos:\n\n{str(e)}\n\n"
            "La aplicación se cerrará."
        )
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(
            None,
            "Error crítico",
            f"Error inesperado al inicializar la base de datos:\n\n{str(e)}\n\n"
            "La aplicación se cerrará."
        )
        sys.exit(1)
    
    # Aplicar tema por defecto ANTES de crear widgets (primera pasada)
    print(f"Aplicando tema inicial: {DEFAULT_THEME}")
    qss_service.apply_theme(DEFAULT_THEME, force_refresh=False)
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    # RE-APLICAR tema con refresco DESPUÉS de crear la UI para asegurar que se aplique correctamente
    print(f"Refrescando estilos del tema: {DEFAULT_THEME}")
    qss_service.apply_theme(DEFAULT_THEME, force_refresh=True)
    
    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
