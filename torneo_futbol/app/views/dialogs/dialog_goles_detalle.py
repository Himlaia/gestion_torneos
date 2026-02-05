"""Diálogo para gestionar goles con autor y minutos."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QSpinBox, QMessageBox, QDialogButtonBox
)
from PySide6.QtCore import Qt


class DialogGolesDetalle(QDialog):
    """Diálogo para asignar autores y minutos a los goles."""
    
    def __init__(self, parent=None, partido_actual=None, goles_local=0, goles_visitante=0, goles_detalle_iniciales=None):
        super().__init__(parent)
        self.partido_actual = partido_actual
        self.goles_local = goles_local
        self.goles_visitante = goles_visitante
        
        # Usar goles iniciales si se proveen, sino cargar desde BD
        if goles_detalle_iniciales:
            self.goles_detalle = goles_detalle_iniciales.copy()
        else:
            self.goles_detalle = []
        
        self.setup_ui()
        
        # Si no se pasaron goles iniciales, intentar cargar desde BD
        if not goles_detalle_iniciales:
            self.cargar_goles_existentes()
        else:
            # Actualizar tabla con los goles iniciales
            self.actualizar_tabla()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle("Detalles de Goles")
        self.setMinimumSize(650, 450)
        
        layout = QVBoxLayout()
        
        # Información del marcador con contador
        self.info_label = QLabel()
        self.actualizar_info_marcador()
        self.info_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background-color: #fff3cd; border-radius: 5px;")
        layout.addWidget(self.info_label)
        
        # Tabla de goles
        self.tabla_goles = QTableWidget()
        self.tabla_goles.setColumnCount(4)
        self.tabla_goles.setHorizontalHeaderLabels([
            "Minuto", "Equipo", "Jugador", ""
        ])
        self.tabla_goles.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_goles.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Eliminar "casilla alargada" a la derecha
        self.tabla_goles.setCornerButtonEnabled(False)
        self.tabla_goles.setShowGrid(True)
        self.tabla_goles.verticalHeader().setVisible(False)
        
        header = self.tabla_goles.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Jugador ocupa el espacio restante
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 70)  # Ancho fijo para botón de eliminar (aumentado para evitar corte)
        header.setStretchLastSection(False)
        
        layout.addWidget(self.tabla_goles)
        
        # Botones de gestión
        layout_btns = QHBoxLayout()
        
        self.btn_anadir = QPushButton("+ Añadir Gol")
        self.btn_anadir.clicked.connect(self.on_anadir_gol)
        layout_btns.addWidget(self.btn_anadir)
        
        self.btn_randomizar = QPushButton("Randomizar")
        self.btn_randomizar.setToolTip("Distribuye los goles automáticamente entre los convocados")
        self.btn_randomizar.clicked.connect(self.on_randomizar_goles)
        layout_btns.addWidget(self.btn_randomizar)
        
        self.btn_limpiar = QPushButton("Limpiar Todo")
        self.btn_limpiar.clicked.connect(self.on_limpiar_goles)
        layout_btns.addWidget(self.btn_limpiar)
        
        layout_btns.addStretch()
        layout.addLayout(layout_btns)
        
        # Botones del diálogo
        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)
        
        self.setLayout(layout)
    
    def cargar_goles_existentes(self):
        """Carga los goles existentes desde el modelo."""
        if not self.partido_actual or not self.partido_actual.get('id'):
            return
        
        try:
            from app.models.goal_model import GoalModel
            goles = GoalModel.obtener_goles_partido(self.partido_actual['id'])
            self.goles_detalle = goles
            self.actualizar_tabla()
        except Exception as e:
            print(f"Error al cargar goles: {e}")
    
    def actualizar_info_marcador(self):
        """Actualiza el label con información del marcador y contador de goles."""
        total_marcador = self.goles_local + self.goles_visitante
        total_detalle = len(self.goles_detalle)
        
        # Contar goles por equipo en detalles
        if not self.partido_actual:
            self.info_label.setText(f"Marcador: {self.goles_local} - {self.goles_visitante}")
            return
            
        local_id = self.partido_actual.get('local_id') or self.partido_actual.get('equipo_local_id')
        visitante_id = self.partido_actual.get('visitante_id') or self.partido_actual.get('equipo_visitante_id')
        
        goles_local_detalle = sum(1 for g in self.goles_detalle if g.get('equipo_id') == local_id)
        goles_visitante_detalle = sum(1 for g in self.goles_detalle if g.get('equipo_id') == visitante_id)
        
        texto = f"Marcador: {self.goles_local} - {self.goles_visitante} | "
        texto += f"Detalles: {goles_local_detalle} - {goles_visitante_detalle} ({total_detalle}/{total_marcador})"
        
        # Validar exceso
        if goles_local_detalle > self.goles_local or goles_visitante_detalle > self.goles_visitante:
            texto += " ⚠️ EXCESO"
            self.info_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background-color: #f8d7da; border-radius: 5px; color: #721c24;")
        else:
            self.info_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background-color: #d4edda; border-radius: 5px; color: #155724;")
        
        self.info_label.setText(texto)
    
    def actualizar_tabla(self):
        """Actualiza la tabla con los goles actuales."""
        self.tabla_goles.setRowCount(len(self.goles_detalle))
        
        for i, gol in enumerate(self.goles_detalle):
            # Minuto
            minuto_text = str(gol.get('minuto')) if gol.get('minuto') else '-'
            minuto_item = QTableWidgetItem(minuto_text)
            minuto_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_goles.setItem(i, 0, minuto_item)
            
            # Equipo
            equipo_item = QTableWidgetItem(gol.get('equipo_nombre', 'Desconocido'))
            self.tabla_goles.setItem(i, 1, equipo_item)
            
            # Jugador
            jugador_item = QTableWidgetItem(gol.get('jugador_nombre', 'Desconocido'))
            self.tabla_goles.setItem(i, 2, jugador_item)
            
            # Botón eliminar con icono de basura - diseño moderno
            btn_eliminar = QPushButton("🗑")  # Icono de papelera
            btn_eliminar.setObjectName("btnEliminarGol")
            btn_eliminar.setFixedSize(40, 28)
            btn_eliminar.setToolTip("Eliminar este gol")
            btn_eliminar.setStyleSheet("""
                QPushButton#btnEliminarGol {
                    background-color: transparent;
                    color: #dc3545;
                    border: 1px solid rgba(220, 53, 69, 0.3);
                    border-radius: 6px;
                    font-size: 16px;
                    padding: 4px;
                }
                QPushButton#btnEliminarGol:hover {
                    background-color: rgba(220, 53, 69, 0.1);
                    border: 1px solid rgba(220, 53, 69, 0.5);
                }
                QPushButton#btnEliminarGol:pressed {
                    background-color: rgba(220, 53, 69, 0.2);
                }
            """)
            btn_eliminar.clicked.connect(lambda checked, row=i: self.eliminar_gol(row))
            self.tabla_goles.setCellWidget(i, 3, btn_eliminar)
        
        # Actualizar contador
        self.actualizar_info_marcador()
    
    def validar_goles_antes_de_aceptar(self) -> bool:
        """Valida que los goles no excedan el marcador."""
        if not self.partido_actual:
            return True
            
        local_id = self.partido_actual.get('local_id') or self.partido_actual.get('equipo_local_id')
        visitante_id = self.partido_actual.get('visitante_id') or self.partido_actual.get('equipo_visitante_id')
        
        goles_local_detalle = sum(1 for g in self.goles_detalle if g.get('equipo_id') == local_id)
        goles_visitante_detalle = sum(1 for g in self.goles_detalle if g.get('equipo_id') == visitante_id)
        
        if goles_local_detalle > self.goles_local:
            QMessageBox.warning(
                self,
                "Goles excedidos",
                f"El equipo local tiene {goles_local_detalle} goles en detalles pero el marcador indica {self.goles_local}.\n"
                f"Elimine {goles_local_detalle - self.goles_local} gol(es) del equipo local."
            )
            return False
        
        if goles_visitante_detalle > self.goles_visitante:
            QMessageBox.warning(
                self,
                "Goles excedidos",
                f"El equipo visitante tiene {goles_visitante_detalle} goles en detalles pero el marcador indica {self.goles_visitante}.\n"
                f"Elimine {goles_visitante_detalle - self.goles_visitante} gol(es) del equipo visitante."
            )
            return False
        
        return True
    
    def accept(self):
        """Override para validar antes de cerrar."""
        if self.validar_goles_antes_de_aceptar():
            super().accept()
    
    def on_anadir_gol(self):
        """Añade un gol manualmente."""
        if not self.partido_actual:
            QMessageBox.warning(self, "Aviso", "No hay partido cargado")
            return
        
        # Verificar si se puede añadir más goles
        total_detalle = len(self.goles_detalle)
        total_marcador = self.goles_local + self.goles_visitante
        
        if total_detalle >= total_marcador:
            QMessageBox.warning(
                self,
                "Límite alcanzado",
                f"Ya se han registrado {total_detalle} goles de {total_marcador} del marcador.\n"
                "Aumente el marcador si desea agregar más goles."
            )
            return
        
        local_id = self.partido_actual.get('local_id') or self.partido_actual.get('equipo_local_id')
        visitante_id = self.partido_actual.get('visitante_id') or self.partido_actual.get('equipo_visitante_id')
        
        if not local_id or not visitante_id:
            QMessageBox.warning(self, "Aviso", "El partido no tiene equipos asignados")
            return
        
        # Obtener convocados
        try:
            from app.models.callup_model import CallupModel
            from app.models.team_model import TeamModel
            
            convocados_local = CallupModel.obtener_convocados_equipo(self.partido_actual['id'], local_id)
            convocados_visitante = CallupModel.obtener_convocados_equipo(self.partido_actual['id'], visitante_id)
            
            if not convocados_local and not convocados_visitante:
                QMessageBox.warning(self, "Aviso", "No hay jugadores convocados para este partido")
                return
            
            # Crear diálogo para seleccionar jugador
            dialogo = QDialog(self)
            dialogo.setWindowTitle("Añadir Gol")
            layout = QVBoxLayout()
            
            # Selector de equipo
            layout.addWidget(QLabel("Equipo:"))
            combo_equipo = QComboBox()
            
            equipo_local = TeamModel.obtener_equipo_por_id(local_id)
            equipo_visitante = TeamModel.obtener_equipo_por_id(visitante_id)
            
            combo_equipo.addItem(equipo_local['nombre'] if equipo_local else "Local", local_id)
            combo_equipo.addItem(equipo_visitante['nombre'] if equipo_visitante else "Visitante", visitante_id)
            layout.addWidget(combo_equipo)
            
            # Selector de jugador
            layout.addWidget(QLabel("Jugador:"))
            combo_jugador = QComboBox()
            layout.addWidget(combo_jugador)
            
            def actualizar_jugadores():
                combo_jugador.clear()
                equipo_id = combo_equipo.currentData()
                convocados = convocados_local if equipo_id == local_id else convocados_visitante
                for conv in convocados:
                    nombre = f"{conv.get('nombre', '')} {conv.get('apellidos', '')}".strip()
                    combo_jugador.addItem(nombre, conv.get('participante_id'))
            
            combo_equipo.currentIndexChanged.connect(actualizar_jugadores)
            actualizar_jugadores()
            
            # Minuto
            layout.addWidget(QLabel("Minuto (opcional):"))
            spin_minuto = QSpinBox()
            spin_minuto.setRange(0, 120)
            spin_minuto.setValue(0)
            spin_minuto.setSpecialValueText("-")
            layout.addWidget(spin_minuto)
            
            # Botones
            botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            botones.accepted.connect(dialogo.accept)
            botones.rejected.connect(dialogo.reject)
            layout.addWidget(botones)
            
            dialogo.setLayout(layout)
            
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                participante_id = combo_jugador.currentData()
                equipo_id = combo_equipo.currentData()
                minuto = spin_minuto.value() if spin_minuto.value() > 0 else None
                
                # Añadir a la lista
                self.goles_detalle.append({
                    'participante_id': participante_id,
                    'equipo_id': equipo_id,
                    'minuto': minuto,
                    'jugador_nombre': combo_jugador.currentText(),
                    'equipo_nombre': combo_equipo.currentText()
                })
                
                self.actualizar_tabla()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al añadir gol:\n{str(e)}")
    
    def on_randomizar_goles(self):
        """Distribuye los goles aleatoriamente."""
        if not self.partido_actual:
            return
        
        try:
            from app.services.match_service import MatchService
            from app.models.team_model import TeamModel
            from app.models.participant_model import ParticipantModel
            
            goles_detalle = MatchService.randomize_goalscorers(
                self.partido_actual['id'],
                self.goles_local,
                self.goles_visitante
            )
            
            if not goles_detalle:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "No se pudieron randomizar los goles.\n"
                    "Verifique que hay jugadores convocados."
                )
                return
            
            # Enriquecer con nombres
            for gol in goles_detalle:
                equipo = TeamModel.obtener_equipo_por_id(gol['equipo_id'])
                gol['equipo_nombre'] = equipo['nombre'] if equipo else 'Desconocido'
                
                participante = ParticipantModel.obtener_participante_por_id(gol['participante_id'])
                if participante:
                    gol['jugador_nombre'] = f"{participante['nombre']} {participante.get('apellidos', '')}".strip()
                else:
                    gol['jugador_nombre'] = 'Desconocido'
            
            self.goles_detalle = goles_detalle
            self.actualizar_tabla()
            
            QMessageBox.information(
                self,
                "Goles Randomizados",
                f"Se distribuyeron {len(goles_detalle)} goles aleatoriamente."
            )
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al randomizar:\n{str(e)}")
    
    def on_limpiar_goles(self):
        """Limpia todos los goles."""
        if not self.goles_detalle:
            return
        
        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Eliminar todos los goles con autor?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.goles_detalle = []
            self.actualizar_tabla()
    
    def eliminar_gol(self, fila: int):
        """Elimina un gol específico."""
        if 0 <= fila < len(self.goles_detalle):
            del self.goles_detalle[fila]
            self.actualizar_tabla()
    
    def get_goles_detalle(self) -> list[dict]:
        """Devuelve la lista de goles configurada."""
        return self.goles_detalle
