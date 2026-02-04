"""Controlador de navegación entre páginas."""
from PySide6.QtWidgets import QStackedWidget
from typing import Optional


class NavigationController:
    """Controlador para gestionar la navegación entre páginas."""
    
    def __init__(self, stacked_widget: QStackedWidget):
        """
        Inicializa el controlador de navegación.
        
        Args:
            stacked_widget: Widget apilado que contiene las páginas
        """
        self.stacked_widget: QStackedWidget = stacked_widget
        self.current_page: int = 0
    
    def navigate_to(self, page_index: int) -> None:
        """
        Navega a una página específica.
        
        Args:
            page_index: Índice de la página a mostrar
        """
        if 0 <= page_index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(page_index)
            self.current_page = page_index
            print(f"Navegando a página {page_index}")
        else:
            print(f"⚠ Índice de página inválido: {page_index}")
    
    def get_current_page(self) -> int:
        """
        Obtiene el índice de la página actual.
        
        Returns:
            Índice de la página actual
        """
        return self.current_page
    
    def get_page_count(self) -> int:
        """
        Obtiene el número total de páginas.
        
        Returns:
            Número de páginas en el stacked widget
        """
        return self.stacked_widget.count()
