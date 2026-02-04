"""Punto de entrada de la aplicación."""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from app.models.db import init_db, DbError
from app.services.qss_service import qss_service
from app.config import DEFAULT_THEME
from app.views.main_window import MainWindow


def main():
    """Función principal de la aplicación."""
    # Crear aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("Torneo de Fútbol")
    app.setOrganizationName("DAM")
    
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
