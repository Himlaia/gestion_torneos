"""Servicio de gestión de estilos QSS (temas)."""
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QFontDatabase
from app.config import STYLES_DIR
from app.constants import THEME_LIGHT, THEME_DARK


class QSSService:
    """Servicio para cargar y aplicar estilos QSS."""
    
    def __init__(self):
        """Inicializa el servicio de estilos."""
        self.current_theme: str = THEME_LIGHT
        self._fonts_loaded: bool = False
    
    def _load_custom_fonts(self):
        """Carga las fuentes personalizadas desde la carpeta resources/fonts."""
        if self._fonts_loaded:
            return
        
        fonts_dir = STYLES_DIR.parent / "fonts"
        
        if not fonts_dir.exists():
            print(f"⚠ Directorio de fuentes no encontrado: {fonts_dir}")
            self._fonts_loaded = True
            return
        
        # Cargar fuentes Poppins
        custom_fonts = [
            "Poppins-Medium.ttf",
            "Poppins-SemiBold.ttf"
        ]
        
        for font_file in custom_fonts:
            font_path = fonts_dir / font_file
            if font_path.exists():
                font_id = QFontDatabase.addApplicationFont(str(font_path))
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    print(f"✓ Fuente cargada: {font_file} ({', '.join(families)})")
                else:
                    print(f"✗ Error al cargar fuente: {font_file}")
            else:
                print(f"⚠ Fuente no encontrada: {font_path}")
        
        self._fonts_loaded = True
    
    def load_qss(self, theme: str) -> Optional[str]:
        """
        Carga el contenido de un archivo QSS.
        
        Args:
            theme: Nombre del tema ('light' o 'dark')
            
        Returns:
            Contenido del archivo QSS o None si no existe
        """
        qss_file = STYLES_DIR / f"{theme}.qss"
        
        if not qss_file.exists():
            print(f"⚠ Archivo de estilo no encontrado: {qss_file}")
            return None
        
        try:
            with open(qss_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            img_dir = STYLES_DIR.parent / "img"
            img_cesped = img_dir / "cesped.jpg"
            if img_cesped.exists():
                img_path_normalized = str(img_cesped.resolve()).replace('\\', '/')
                content = content.replace('../img/cesped.jpg', img_path_normalized)
            
            return content
        except Exception as e:
            print(f"✗ Error al cargar el estilo: {e}")
            return None
    
    def apply_theme(self, theme: str, force_refresh: bool = True) -> bool:
        """
        Aplica un tema a la aplicación.
        
        Args:
            theme: Nombre del tema ('light' o 'dark')
            force_refresh: Si True, fuerza el refresco de estilos en todos los widgets
            
        Returns:
            True si se aplicó correctamente, False en caso contrario
        """
        # Cargar fuentes personalizadas si aún no se han cargado
        self._load_custom_fonts()
        
        qss_content = self.load_qss(theme)
        
        if qss_content is None:
            return False
        
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss_content)
            self.current_theme = theme
            
            # Forzar refresco de estilos en todos los widgets
            if force_refresh:
                self._refresh_all_widgets()
            
            print(f"✓ Tema '{theme}' aplicado correctamente")
            return True
        
        return False
    
    def _refresh_all_widgets(self):
        """
        Fuerza el refresco de estilos en todos los widgets de la aplicación.
        Esto asegura que los estilos QSS se apliquen correctamente a widgets
        ya creados, especialmente útil al iniciar o cambiar de tema.
        """
        app = QApplication.instance()
        if not app:
            return
        
        # Obtener todos los top-level widgets
        for widget in app.topLevelWidgets():
            # Forzar repolish del widget y todos sus hijos
            self._repolish_widget(widget)
    
    def _repolish_widget(self, widget):
        """
        Fuerza el repolish de un widget y todos sus hijos recursivamente.
        
        Args:
            widget: Widget a repolish
        """
        if widget is None:
            return
        
        try:
            # Forzar que el estilo se vuelva a aplicar al widget principal
            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)
            widget.update()
            
            # Aplicar recursivamente a todos los widgets hijos
            for child in widget.findChildren(QWidget):
                try:
                    child_style = child.style()
                    child_style.unpolish(child)
                    child_style.polish(child)
                    child.update()
                except:
                    # Algunos widgets pueden no soportar unpolish/polish
                    continue
        except Exception:
            # Silenciar errores de repolish
            pass
    
    def toggle_theme(self) -> str:
        """
        Alterna entre el tema claro y oscuro.
        
        Returns:
            El tema actual después del cambio
        """
        new_theme = THEME_DARK if self.current_theme == THEME_LIGHT else THEME_LIGHT
        self.apply_theme(new_theme)
        return self.current_theme
    
    def get_current_theme(self) -> str:
        """Obtiene el tema actual."""
        return self.current_theme


# Instancia global
qss_service = QSSService()
