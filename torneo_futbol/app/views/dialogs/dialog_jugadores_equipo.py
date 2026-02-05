"""Diálogo para mostrar los jugadores de un equipo."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt


class DialogJugadoresEquipo(QDialog):
    """Diálogo para mostrar los jugadores de un equipo."""
    
    def __init__(self, nombre_equipo: str, jugadores: list[dict], parent=None):
        """
        Inicializa el diálogo.
        
        Args:
            nombre_equipo: Nombre del equipo
            jugadores: Lista de jugadores del equipo
            parent: Widget padre
        """
        super().__init__(parent)
        self.nombre_equipo = nombre_equipo
        self.jugadores = jugadores
        self.setup_ui()
        self.cargar_jugadores()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle(f"Jugadores de {self.nombre_equipo}")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Título
        titulo = QLabel(f"Jugadores del equipo: {self.nombre_equipo}")
        titulo.setObjectName("dialogTitle")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabla de jugadores
        self.tabla_jugadores = QTableWidget()
        self.tabla_jugadores.setColumnCount(5)
        self.tabla_jugadores.setHorizontalHeaderLabels([
            "Nombre", "Apellidos", "Posición", "Goles", "Tarjetas"
        ])
        
        # Configurar tabla
        self.tabla_jugadores.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_jugadores.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.tabla_jugadores.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        
        # Ajustar columnas
        header = self.tabla_jugadores.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.tabla_jugadores)
        
        # Etiqueta de resumen
        self.label_resumen = QLabel()
        self.label_resumen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_resumen)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
    
    def cargar_jugadores(self):
        """Carga los jugadores en la tabla."""
        self.tabla_jugadores.setRowCount(len(self.jugadores))
        
        if not self.jugadores:
            self.label_resumen.setText("Este equipo no tiene jugadores asignados")
            return
        
        for fila, jugador in enumerate(self.jugadores):
            # Nombre
            item_nombre = QTableWidgetItem(jugador.get('nombre', ''))
            self.tabla_jugadores.setItem(fila, 0, item_nombre)
            
            # Apellidos
            item_apellidos = QTableWidgetItem(jugador.get('apellidos', ''))
            self.tabla_jugadores.setItem(fila, 1, item_apellidos)
            
            # Posición
            posicion = jugador.get('posicion', 'Sin posición')
            item_posicion = QTableWidgetItem(posicion)
            self.tabla_jugadores.setItem(fila, 2, item_posicion)
            
            # Goles
            goles = jugador.get('goles', 0)
            item_goles = QTableWidgetItem(str(goles))
            item_goles.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_jugadores.setItem(fila, 3, item_goles)
            
            # Tarjetas (amarillas + rojas)
            amarillas = jugador.get('tarjetas_amarillas', 0)
            rojas = jugador.get('tarjetas_rojas', 0)
            tarjetas_texto = f"🟨 {amarillas}  🟥 {rojas}"
            item_tarjetas = QTableWidgetItem(tarjetas_texto)
            item_tarjetas.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_jugadores.setItem(fila, 4, item_tarjetas)
        
        # Actualizar resumen
        total_jugadores = len(self.jugadores)
        total_goles = sum(j.get('goles', 0) for j in self.jugadores)
        self.label_resumen.setText(
            f"Total: {total_jugadores} jugador{'es' if total_jugadores != 1 else ''} | "
            f"Goles totales: {total_goles}"
        )
