"""Página de ayuda."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QTextBrowser, QSizePolicy
from PySide6.QtCore import Qt, QUrl
from pathlib import Path


class PageHelp(QWidget):
    """Página de ayuda."""
    
    def __init__(self):
        """Inicializa la página de ayuda."""
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Establecer objectName para el widget raíz
        self.setObjectName("pageRoot")
        
        # Layout principal con márgenes (igual que page_teams)
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 4, 20, 12)
        layout_principal.setSpacing(8)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Título de la página
        titulo = QLabel("Ayuda")
        titulo.setObjectName("titleLabel")
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_principal.addWidget(titulo)
        
        # Contenedor de contenido (card) - MISMO PATRÓN QUE OTRAS PÁGINAS
        content_card = QFrame()
        content_card.setObjectName("contentCard")
        content_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # SIN setMaximumWidth para que ocupe todo el ancho como las otras páginas
        
        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        # Subtítulo dentro del card
        subtitulo = QLabel("Documentación de la aplicación")
        subtitulo.setObjectName("subtitleLabel")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(subtitulo)
        
        # QTextBrowser para renderizar Markdown con colores
        self.readme_browser = QTextBrowser()
        self.readme_browser.setObjectName("HelpReadme")
        self.readme_browser.setOpenExternalLinks(False)  # Links externos deshabilitados
        self.readme_browser.setOpenLinks(True)  # Links internos (anchors) habilitados
        self.readme_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.readme_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.readme_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Conectar evento de click en anchor para navegación interna
        self.readme_browser.anchorClicked.connect(self.on_anchor_clicked)
        
        # Cargar contenido del README
        self.cargar_readme()
        
        card_layout.addWidget(self.readme_browser, 1)  # stretch factor 1 para ocupar espacio
        
        layout_principal.addWidget(content_card)
    
    def cargar_readme(self):
        """Carga el contenido de la Guía de Usuario y lo renderiza con formato."""
        # Intentar cargar desde diferentes ubicaciones
        posibles_rutas = [
            Path(__file__).parent.parent.parent.parent / "GUIA_USUARIO.md",  # Raíz del workspace
            Path(__file__).parent.parent.parent / "GUIA_USUARIO.md",  # Raíz del proyecto torneo_futbol
            Path(__file__).parent.parent / "resources" / "GUIA_USUARIO.md",  # Carpeta resources
            Path(__file__).parent.parent.parent.parent / "README.md",  # Fallback al README en workspace
            Path(__file__).parent.parent.parent / "README.md",  # Fallback al README en proyecto
        ]
        
        contenido = None
        for ruta in posibles_rutas:
            if ruta.exists():
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    break
                except Exception as e:
                    print(f"Error al leer {ruta}: {e}")
        
        if contenido:
            # Usar setMarkdown para renderizar con formato
            self.readme_browser.setMarkdown(contenido)
        else:
            # Manual básico embebido si no hay README
            manual = self.crear_manual_basico()
            self.readme_browser.setMarkdown(manual)
        
        # Aplicar estilos CSS al documento para mejorar la visualización
        self.aplicar_estilos_documento()
    
    def aplicar_estilos_documento(self):
        """Aplica estilos CSS al contenido del QTextBrowser."""
        # Obtener el documento y aplicar estilos CSS
        document = self.readme_browser.document()
        
        # Detectar si estamos en modo oscuro o claro
        # (asumimos que el objectName del widget padre indica el tema)
        # Por simplicidad, usamos colores que funcionan bien en ambos modos
        
        # CSS para el contenido del documento
        css = """
        <style>
            body {
                line-height: 1.6;
            }
            h1 {
                color: #16a085;
                border-bottom: 2px solid #16a085;
                padding-bottom: 8px;
                margin-top: 20px;
                margin-bottom: 16px;
                font-size: 24pt;
                font-weight: 600;
            }
            h2 {
                color: #1abc9c;
                margin-top: 18px;
                margin-bottom: 12px;
                font-size: 18pt;
                font-weight: 600;
            }
            h3 {
                color: #27ae60;
                margin-top: 14px;
                margin-bottom: 10px;
                font-size: 14pt;
                font-weight: 600;
            }
            p {
                margin-bottom: 12px;
            }
            ul, ol {
                margin-left: 20px;
                margin-bottom: 12px;
            }
            li {
                margin-bottom: 6px;
            }
            code {
                background-color: rgba(22, 160, 133, 0.15);
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Consolas', 'Courier New', monospace;
                color: #c7254e;
                font-size: 9pt;
            }
            pre {
                background-color: rgba(44, 62, 80, 0.08);
                border: 1px solid rgba(22, 160, 133, 0.25);
                border-radius: 5px;
                padding: 12px;
                margin: 12px 0;
                overflow-x: auto;
            }
            pre code {
                background-color: transparent;
                padding: 0;
            }
            strong {
                color: #16a085;
                font-weight: 600;
            }
            hr {
                border: none;
                border-top: 1px solid rgba(22, 160, 133, 0.3);
                margin: 20px 0;
            }
            blockquote {
                border-left: 4px solid #16a085;
                padding-left: 16px;
                margin-left: 0;
                font-style: italic;
            }
            a {
                color: #1abc9c;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
        """
        
        # Insertar el CSS al inicio del documento HTML
        html_content = self.readme_browser.toHtml()
        if "<head>" in html_content:
            html_content = html_content.replace("<head>", f"<head>{css}")
        else:
            html_content = f"<html><head>{css}</head><body>{html_content}</body></html>"
        
        self.readme_browser.setHtml(html_content)
    
    def crear_manual_basico(self) -> str:
        """Crea un manual básico en formato Markdown."""
        return """# Gestión de Torneo de Fútbol

## Introducción

Bienvenido a la aplicación de **Gestión de Torneo de Fútbol**. Esta herramienta te permite organizar y gestionar torneos de fútbol de manera sencilla y profesional.

## Características principales

### 🔷 Gestión de Equipos
Administra los equipos participantes en el torneo:
- Crear nuevos equipos con nombre y escudo personalizado
- Editar información de equipos existentes
- Eliminar equipos
- Buscar equipos por nombre

### 👥 Participantes
Gestiona jugadores y árbitros:
- **Jugadores**: Añade jugadores con su información personal (nombre, apellidos, edad)
- **Árbitros**: Registra árbitros con su categoría profesional
- Asigna jugadores a equipos mediante convocatorias
- Visualiza estadísticas de cada participante

### 📅 Calendario y Partidos
Programa y gestiona los encuentros:
- Crea partidos especificando equipos, fecha y hora
- Asigna árbitros a cada partido
- Registra resultados y estadísticas
- Visualiza el calendario completo de partidos
- Filtra partidos por día

### 🏆 Cuadro de Eliminatorias
Visualiza el bracket del torneo:
- Vista gráfica del cuadro de eliminación
- Seguimiento de resultados por fase
- Identificación automática del campeón

## Navegación

Utiliza el menú lateral o las tarjetas del inicio para acceder a cada sección:

1. **Inicio**: Vista general con acceso rápido a todas las secciones
2. **Equipos**: Gestión completa de equipos
3. **Participantes**: Administración de jugadores y árbitros
4. **Partidos**: Calendario y gestión de encuentros
5. **Cuadro**: Visualización del bracket del torneo
6. **Ayuda**: Esta documentación
7. **Créditos**: Información del proyecto

## Temas

La aplicación soporta dos temas visuales:
- **Modo claro**: Para ambientes bien iluminados
- **Modo oscuro**: Para reducir la fatiga visual

Cambia entre temas usando el botón en la barra superior.

## Consejos de uso

- 💡 **Crea primero los equipos** antes de añadir partidos
- 💡 **Registra jugadores y árbitros** antes de programar encuentros
- 💡 **Usa la búsqueda** para encontrar equipos o participantes rápidamente
- 💡 **Actualiza los resultados** después de cada partido para mantener el cuadro actualizado

## Soporte

Si encuentras algún problema o tienes sugerencias, consulta la sección de **Créditos** para más información sobre el proyecto.

---

*Gestión de Torneo de Fútbol - Aplicación de escritorio con PySide6*
"""
    
    def on_anchor_clicked(self, url: QUrl):
        """Maneja clicks en anchors para navegación interna."""
        # Si es un anchor interno (comienza con #), hacer scroll a esa sección
        fragment = url.fragment()
        if fragment:
            # Scroll a la sección usando el anchor
            self.readme_browser.scrollToAnchor(fragment)
        # Si no tiene fragment, ignorar (no es un link interno válido)
