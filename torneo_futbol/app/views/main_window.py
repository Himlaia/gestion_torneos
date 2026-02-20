"""Ventana principal de la aplicación."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
    QMenuBar, QMenu, QApplication
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QTranslator, QEvent
from pathlib import Path

from app.constants import (
    APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    PAGE_HOME, PAGE_TEAMS, PAGE_PARTICIPANTS, PAGE_MATCHES,
    PAGE_BRACKET, PAGE_REPORTS, PAGE_TOOLS, PAGE_HELP, PAGE_CREDITS, THEME_LIGHT
)
from app.config import AVAILABLE_LANGUAGES, TRANSLATIONS_DIR
from app.controllers.navigation_controller import NavigationController
from app.controllers.teams_controller import ControladorGestionEquipos
from app.controllers.participants_controller import ControladorGestionParticipantes
from app.controllers.matches_controller import ControladorCalendarioPartidos
from app.controllers.bracket_controller import ControladorCuadroEliminatorias
from app.controllers.reports_controller import ControladorReportes
from app.services.qss_service import qss_service
from app.views.widgets.background_widget import BackgroundWidget
from app.views.page_home import PageInicio
from app.views.page_teams import PageGestionEquipos
from app.views.page_participants import PageParticipants
from app.views.page_matches import PageMatches
from app.views.page_bracket import PageBracket
from app.views.page_reports import PageReports
from app.views.page_tools import PageTools
from app.views.page_help import PageHelp
from app.views.page_credits import PageCredits


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()
        self.translator = None
        self.current_language = "es"
        self.setup_ui()
        self.create_menu_bar()
        self.setup_navigation()
    
    def setup_ui(self):
        """Configura la interfaz de usuario básica."""
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Widget central con fondo de césped
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal con background widget
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Widget de fondo de césped (detrás de todo)
        self.background_widget = BackgroundWidget(central_widget)
        self.background_widget.set_theme(THEME_LIGHT)
        self.background_widget.setGeometry(central_widget.rect())
        self.background_widget.lower()  # Enviar al fondo
        
        # Stacked Widget para las páginas (con fondo transparente)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        main_layout.addWidget(self.stacked_widget)
        
        # Crear páginas (guardar referencias)
        self.page_inicio = PageInicio()
        self.page_equipos = PageGestionEquipos()
        self.page_participantes = PageParticipants()
        self.page_matches = PageMatches()  # ✅ GUARDADA COMO ATRIBUTO
        self.page_bracket = PageBracket()  # ✅ GUARDADA COMO ATRIBUTO
        self.page_reports = PageReports()
        self.page_tools = PageTools()
        self.page_help = PageHelp()
        self.page_credits = PageCredits()
        
        # Agregar páginas al stacked widget
        self.stacked_widget.addWidget(self.page_inicio)         # 0 - HOME
        self.stacked_widget.addWidget(self.page_equipos)        # 1 - TEAMS
        self.stacked_widget.addWidget(self.page_participantes)  # 2 - PARTICIPANTS
        self.stacked_widget.addWidget(self.page_matches)        # 3 - MATCHES
        self.stacked_widget.addWidget(self.page_bracket)        # 4 - BRACKET
        self.stacked_widget.addWidget(self.page_reports)        # 5 - REPORTS
        self.stacked_widget.addWidget(self.page_tools)          # 6 - TOOLS
        self.stacked_widget.addWidget(self.page_help)           # 7 - HELP
        self.stacked_widget.addWidget(self.page_credits)        # 8 - CREDITS
        
        # ✅ Inicializar controladores
        print("[MAIN WINDOW] Inicializando controladores...")
        self.controlador_equipos = ControladorGestionEquipos(self.page_equipos)
        self.controlador_participantes = ControladorGestionParticipantes(self.page_participantes)
        
        # 🔴 CRITICAL: Inicializar controlador de partidos
        print("[MAIN WINDOW] Inicializando ControladorCalendarioPartidos...")
        self.controlador_matches = ControladorCalendarioPartidos(self.page_matches)
        print("[MAIN WINDOW] ControladorCalendarioPartidos inicializado correctamente")
        
        # 🔴 CRITICAL: Inicializar controlador de bracket (temporalmente comentado por incompatibilidades)
        print("[MAIN WINDOW] Inicializando ControladorCuadroEliminatorias...")
        try:
            self.controlador_bracket = ControladorCuadroEliminatorias(self.page_bracket)
            print("[MAIN WINDOW] ControladorCuadroEliminatorias inicializado correctamente")
            
            # Conectar ambos controladores entre sí
            self.controlador_matches.set_bracket_controller(self.controlador_bracket)
            self.controlador_bracket.set_matches_controller(self.controlador_matches)
        except Exception as e:
            print(f"[MAIN WINDOW WARNING] No se pudo inicializar controlador bracket: {e}")
            self.controlador_bracket = None
        
        # Inicializar controlador de reportes
        print("[MAIN WINDOW] Inicializando ControladorReportes...")
        self.controlador_reportes = ControladorReportes(self.page_reports)
        print("[MAIN WINDOW] ControladorReportes inicializado correctamente")

        # Conectar señales de navegación de PageInicio
        self.page_inicio.ir_a_equipos_signal.connect(lambda: self.navigate_to_page(PAGE_TEAMS))
        self.page_inicio.ir_a_participantes_signal.connect(lambda: self.navigate_to_page(PAGE_PARTICIPANTS))
        self.page_inicio.ir_a_partidos_signal.connect(lambda: self.navigate_to_page(PAGE_MATCHES))
        self.page_inicio.ir_a_cuadro_signal.connect(lambda: self.navigate_to_page(PAGE_BRACKET))
        self.page_inicio.ir_a_reportes_signal.connect(lambda: self.navigate_to_page(PAGE_REPORTS))
        self.page_inicio.ir_a_ayuda_signal.connect(lambda: self.navigate_to_page(PAGE_HELP))
        
        # Mostrar página de inicio al cargar
        self.stacked_widget.setCurrentIndex(PAGE_HOME)
    
    def setup_navigation(self):
        """Configura el controlador de navegación."""
        self.nav_controller = NavigationController(self.stacked_widget)
        
        # Conectar señal de cambio de página para recargar datos
        self.stacked_widget.currentChanged.connect(self._on_page_changed)
    
    def create_menu_bar(self):
        """Crea la barra de menú."""
        menubar = self.menuBar()
        
        # Menú Torneo
        torneo_menu = menubar.addMenu(self.tr("Torneo"))
        
        action_home = QAction(self.tr("Inicio"), self)
        action_home.triggered.connect(lambda: self.navigate_to_page(PAGE_HOME))
        torneo_menu.addAction(action_home)
        
        torneo_menu.addSeparator()
        
        action_teams = QAction(self.tr("Gestión de equipos"), self)
        action_teams.triggered.connect(lambda: self.navigate_to_page(PAGE_TEAMS))
        torneo_menu.addAction(action_teams)
        
        action_participants = QAction(self.tr("Gestión de participantes"), self)
        action_participants.triggered.connect(lambda: self.navigate_to_page(PAGE_PARTICIPANTS))
        torneo_menu.addAction(action_participants)
        
        action_matches = QAction(self.tr("Calendario / Partidos"), self)
        action_matches.triggered.connect(lambda: self.navigate_to_page(PAGE_MATCHES))
        torneo_menu.addAction(action_matches)
        
        action_bracket = QAction(self.tr("Cuadro de eliminatorias"), self)
        action_bracket.triggered.connect(lambda: self.navigate_to_page(PAGE_BRACKET))
        torneo_menu.addAction(action_bracket)

        # Menú Herramientas (independiente)
        tools_menu = menubar.addMenu(self.tr("Herramientas"))

        action_reports = QAction(self.tr("Informes"), self)
        action_reports.triggered.connect(lambda: self.navigate_to_page(PAGE_REPORTS))
        tools_menu.addAction(action_reports)

        action_tools = QAction(self.tr("Reloj digital"), self)
        action_tools.triggered.connect(lambda: self.navigate_to_page(PAGE_TOOLS))
        tools_menu.addAction(action_tools)
        
        # Menú Ver
        view_menu = menubar.addMenu(self.tr("Ver"))
        
        action_theme = QAction(self.tr("Cambiar tema"), self)
        action_theme.triggered.connect(self.toggle_theme)
        view_menu.addAction(action_theme)
        
        view_menu.addSeparator()
        
        # Submenú Idioma
        language_menu = view_menu.addMenu(self.tr("Idioma"))
        
        action_spanish = QAction(self.tr("Español"), self)
        action_spanish.triggered.connect(lambda: self.change_language("es"))
        language_menu.addAction(action_spanish)
        
        action_english = QAction(self.tr("English"), self)
        action_english.triggered.connect(lambda: self.change_language("en"))
        language_menu.addAction(action_english)
        
        # Menú Ayuda
        help_menu = menubar.addMenu(self.tr("Ayuda"))
        
        action_help = QAction(self.tr("Ayuda"), self)
        action_help.triggered.connect(lambda: self.navigate_to_page(PAGE_HELP))
        help_menu.addAction(action_help)
        
        action_credits = QAction(self.tr("Créditos"), self)
        action_credits.triggered.connect(lambda: self.navigate_to_page(PAGE_CREDITS))
        help_menu.addAction(action_credits)
    
    def navigate_to_page(self, page_index: int):
        """
        Navega a una página específica.
        
        Args:
            page_index: Índice de la página
        """
        self.nav_controller.navigate_to(page_index)
    
    def change_language(self, language_code: str):
        """Cambia el idioma de la aplicación."""
        if language_code == self.current_language:
            return
        
        app = QApplication.instance()
        
        # Remover traductor anterior si existe
        if self.translator:
            app.removeTranslator(self.translator)
        
        # Crear nuevo traductor
        self.translator = QTranslator(app)
        translations_path = Path(TRANSLATIONS_DIR)
        
        # Intentar cargar archivo .qm primero
        qm_file = translations_path / f"torneo_{language_code}.qm"
        
        if qm_file.exists() and self.translator.load(str(qm_file)):
            app.installTranslator(self.translator)
            print(f"✓ Idioma cambiado a: {language_code} (.qm)")
        else:
            # Fallback a archivo .ts
            ts_file = translations_path / f"torneo_{language_code}"
            if self.translator.load(str(ts_file), str(translations_path)):
                app.installTranslator(self.translator)
                print(f"✓ Idioma cambiado a: {language_code} (.ts)")
            else:
                print(f"⚠ No se pudo cargar idioma: {language_code}")
                return
        
        self.current_language = language_code
        
        # Emitir evento de cambio de idioma a todos los widgets
        event = QEvent(QEvent.Type.LanguageChange)
        app.sendEvent(app, event)
        
        # Recargar la interfaz para reflejar el cambio
        self.retranslate_ui()
        
        print(f"Idioma actualizado a: {AVAILABLE_LANGUAGES.get(language_code, language_code)}")
    
    def retranslate_ui(self):
        """Recarga los textos de la interfaz después de cambiar el idioma."""
        # Recrear barra de menú
        self.menuBar().clear()
        self.create_menu_bar()
        
        # Emitir evento LanguageChange a todas las páginas
        event = QEvent(QEvent.Type.LanguageChange)
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if widget:
                QApplication.sendEvent(widget, event)
                # Forzar actualización visual
                widget.update()
    
    def toggle_theme(self):
        """Alterna entre tema claro y oscuro."""
        # Alternar tema y aplicar globalmente a toda la aplicación
        new_theme = qss_service.toggle_theme()
        
        # Actualizar el overlay del fondo según el tema
        self.background_widget.set_theme(new_theme)
        
        # Actualizar las tarjetas de la página de inicio
        if hasattr(self, 'page_inicio'):
            self.page_inicio.actualizar_tema_cards(new_theme)
        
        print(f"Tema cambiado a: {new_theme}")
    
    def resizeEvent(self, event):
        """Maneja el redimensionamiento de la ventana para ajustar el fondo."""
        super().resizeEvent(event)
        if hasattr(self, 'background_widget'):
            self.background_widget.setGeometry(self.centralWidget().rect())
    
    def _on_page_changed(self, index: int):
        """Maneja el evento de cambio de página para recargar datos."""
        # Recargar datos cuando se navega a la página de equipos
        if index == PAGE_TEAMS:
            self.controlador_equipos.cargar_tabla()
        elif index == PAGE_REPORTS:
            self.controlador_reportes.cargar_filtros()
