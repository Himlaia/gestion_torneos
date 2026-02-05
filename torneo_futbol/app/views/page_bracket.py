"""Página de cuadro de eliminatorias."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QComboBox, QGridLayout,
    QScrollArea, QMessageBox, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from typing import Optional
import random
import json


class BracketWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bracketRoot")
        self.setProperty("bracket", "true")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self.combos_octavos_left = []
        self.combos_octavos_right = []
        self.combos_cuartos_left = []
        self.combos_cuartos_right = []
        self.combos_semis_left = []
        self.combos_semis_right = []
        self.combo_finalista_left = None
        self.combo_finalista_right = None
        self.title_label_left = None
        self.title_label_right = None
        self.combos_final = []
        self.bracket_state = None
        self.setup_ui()
    
    def setup_ui(self):
        main_grid = QGridLayout()
        main_grid.setSpacing(12)
        main_grid.setContentsMargins(10, 10, 10, 10)
        main_grid.setHorizontalSpacing(15)
        main_grid.setVerticalSpacing(5)
        
        octavos_left_widget = self.create_round_widget("Octavos", 4, "left", "octavos")
        cuartos_left_widget = self.create_round_widget("Cuartos", 2, "left", "cuartos")
        semis_left_widget = self.create_round_widget("Semifinal", 1, "left", "semis")
        finalista_left_widget = self.create_finalista_widget("left")
        finalista_right_widget = self.create_finalista_widget("right")
        semis_right_widget = self.create_round_widget("Semifinal", 1, "right", "semis")
        cuartos_right_widget = self.create_round_widget("Cuartos", 2, "right", "cuartos")
        octavos_right_widget = self.create_round_widget("Octavos", 4, "right", "octavos")
        
        # Add stretch row at top for vertical centering
        main_grid.setRowStretch(0, 1)
        
        # Add bracket widgets in row 1 (centered row)
        main_grid.addWidget(octavos_left_widget, 1, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        main_grid.addWidget(cuartos_left_widget, 1, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        main_grid.addWidget(semis_left_widget, 1, 2, Qt.AlignmentFlag.AlignVCenter)
        main_grid.addWidget(finalista_left_widget, 1, 3, Qt.AlignmentFlag.AlignCenter)
        main_grid.addWidget(finalista_right_widget, 1, 4, Qt.AlignmentFlag.AlignCenter)
        main_grid.addWidget(semis_right_widget, 1, 5, Qt.AlignmentFlag.AlignVCenter)
        main_grid.addWidget(cuartos_right_widget, 1, 6, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        main_grid.addWidget(octavos_right_widget, 1, 7, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Add stretch row at bottom for vertical centering
        main_grid.setRowStretch(2, 1)
        
        main_grid.setColumnStretch(0, 1)
        main_grid.setColumnStretch(1, 1)
        main_grid.setColumnStretch(2, 1)
        main_grid.setColumnStretch(3, 0)
        main_grid.setColumnStretch(4, 0)
        main_grid.setColumnStretch(5, 1)
        main_grid.setColumnStretch(6, 1)
        main_grid.setColumnStretch(7, 1)
        
        self.setLayout(main_grid)
    
    def create_round_widget(self, title: str, num_matches: int, side: str, round_name: str) -> QFrame:
        round_frame = QFrame()
        round_frame.setObjectName(f"bracketRound{round_name.capitalize()}{side.capitalize()}")
        round_frame.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(3, 3, 3, 3)
        
        title_label = QLabel(title)
        title_label.setObjectName("roundTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 9pt; margin-bottom: 3px;")
        layout.addWidget(title_label)
        
        spacing_map = {"octavos": 6, "cuartos": 40, "semis": 120}
        spacing = spacing_map.get(round_name, 6)
        
        for i in range(num_matches):
            match_card = self.create_match_card(round_name, side, i)
            layout.addWidget(match_card)
            if i < num_matches - 1:
                layout.addSpacing(spacing)
        
        layout.addStretch()
        
        round_frame.setLayout(layout)
        return round_frame
    
    def create_finalista_widget(self, side: str) -> QFrame:
        finalista_frame = QFrame()
        finalista_frame.setObjectName(f"bracketFinalista{side.capitalize()}")
        finalista_frame.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(3, 3, 3, 3)
        
        title_label = QLabel("Finalista")
        title_label.setObjectName("roundTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 9pt; margin-bottom: 3px;")
        layout.addWidget(title_label)
        
        layout.addStretch(1)
        
        combo_frame = QFrame()
        combo_frame.setObjectName("finalistaCard")
        
        combo_layout = QVBoxLayout()
        combo_layout.setSpacing(0)
        combo_layout.setContentsMargins(6, 8, 6, 8)
        
        combo = QComboBox()
        combo.setObjectName("teamCombo")
        combo.setProperty("slot", "finalista")
        combo.addItem("Selecciona equipo...", None)
        combo.setMinimumWidth(160)
        combo.setMaximumHeight(28)
        
        combo_layout.addWidget(combo)
        combo_frame.setLayout(combo_layout)
        
        layout.addWidget(combo_frame, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        
        if side == "left":
            self.combo_finalista_left = combo
            self.title_label_left = title_label
        else:
            self.combo_finalista_right = combo
            self.title_label_right = title_label
        
        finalista_frame.setLayout(layout)
        return finalista_frame
    
    def create_match_card(self, round_name: str, side: str, index: int) -> QFrame:
        match_frame = QFrame()
        match_frame.setObjectName("matchCard")
        match_frame.setProperty("round", round_name)
        match_frame.setProperty("side", side)
        
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(6, 6, 6, 6)
        
        combo_a = QComboBox()
        combo_a.setObjectName("teamCombo")
        combo_a.setProperty("slot", "A")
        combo_a.addItem("Selecciona equipo...", None)
        combo_a.setMinimumWidth(160)
        combo_a.setMaximumHeight(26)
        
        vs_label = QLabel("vs")
        vs_label.setObjectName("vsLabel")
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_label.setStyleSheet("font-size: 8pt; font-weight: bold; color: #666; margin: 0px;")
        vs_label.setMaximumHeight(14)
        
        combo_b = QComboBox()
        combo_b.setObjectName("teamCombo")
        combo_b.setProperty("slot", "B")
        combo_b.addItem("Selecciona equipo...", None)
        combo_b.setMinimumWidth(160)
        combo_b.setMaximumHeight(26)
        
        layout.addWidget(combo_a)
        layout.addWidget(vs_label)
        layout.addWidget(combo_b)
        
        match_frame.setLayout(layout)
        
        if round_name == "octavos" and side == "left":
            self.combos_octavos_left.extend([combo_a, combo_b])
        elif round_name == "octavos" and side == "right":
            self.combos_octavos_right.extend([combo_a, combo_b])
        elif round_name == "cuartos" and side == "left":
            self.combos_cuartos_left.extend([combo_a, combo_b])
        elif round_name == "cuartos" and side == "right":
            self.combos_cuartos_right.extend([combo_a, combo_b])
        elif round_name == "semis" and side == "left":
            self.combos_semis_left.extend([combo_a, combo_b])
        elif round_name == "semis" and side == "right":
            self.combos_semis_right.extend([combo_a, combo_b])
        
        return match_frame
    
    def get_all_combos(self):
        combos = (self.combos_octavos_left + self.combos_octavos_right +
                self.combos_cuartos_left + self.combos_cuartos_right +
                self.combos_semis_left + self.combos_semis_right)
        if self.combo_finalista_left:
            combos.append(self.combo_finalista_left)
        if self.combo_finalista_right:
            combos.append(self.combo_finalista_right)
        return combos
    
    def populate_team_combos(self, equipos: list[dict]):
        """Función centralizada para poblar todos los combos con la lista de equipos."""
        all_combos = self.get_all_combos()
        
        for combo in all_combos:
            current_text = combo.currentText()
            current_data = combo.currentData()
            
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Selecciona equipo...", None)
            
            for eq in equipos:
                combo.addItem(eq['nombre'], eq['id'])
            
            # Restaurar selección previa si existe
            if current_data is not None:
                idx = combo.findData(current_data)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            elif current_text and current_text != "Selecciona equipo...":
                idx = combo.findText(current_text)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            
            combo.blockSignals(False)
    
    def update_crown_visibility(self, ganador_equipo_id=None):
        """Actualiza el texto del label Finalista. Añade corona solo al ganador."""
        if self.title_label_left and self.combo_finalista_left:
            left_team_id = self.combo_finalista_left.currentData()
            # Añadir corona solo si este equipo es el ganador
            is_winner = ganador_equipo_id is not None and left_team_id == ganador_equipo_id
            self.title_label_left.setText("👑 Finalista" if is_winner else "Finalista")
        
        if self.title_label_right and self.combo_finalista_right:
            right_team_id = self.combo_finalista_right.currentData()
            # Añadir corona solo si este equipo es el ganador
            is_winner = ganador_equipo_id is not None and right_team_id == ganador_equipo_id
            self.title_label_right.setText("👑 Finalista" if is_winner else "Finalista")


class PageCuadroEliminatorias(QWidget):
    
    randomizar_octavos_signal = Signal()
    guardar_emparejamientos_signal = Signal(list)
    reiniciar_emparejamientos_signal = Signal()
    emparejamientos_cambiados_signal = Signal()
    
    def __init__(self):
        super().__init__()
        self.modo_actual = "configurable"
        self.bracket_widget = None
        self.equipos_disponibles = []
        self.setup_ui()
        self.conectar_senales()
    
    def setup_ui(self):
        self.setObjectName("pageRoot")
        
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 4, 20, 12)
        layout_principal.setSpacing(8)
        # Eliminado AlignTop para permitir centrado vertical
        
        self.crear_cabecera(layout_principal)
        
        content_card = QFrame()
        content_card.setObjectName("contentCard")
        content_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        self.crear_botones_accion(card_layout)
        
        self.bracket_widget = BracketWidget()
        self.bracket_widget.setMinimumHeight(500)
        
        card_layout.addWidget(self.bracket_widget, 1)
        
        # Añadir stretcher superior para centrar el contenido
        layout_principal.addStretch(1)
        layout_principal.addWidget(content_card, 0)
        # Añadir stretcher inferior para centrar el contenido
        layout_principal.addStretch(1)
        
        self.setLayout(layout_principal)
        
        self.cargar_equipos_en_combos()
    
    def cargar_equipos_en_combos(self):
        """Carga la lista de equipos en todos los combos del bracket."""
        if not self.bracket_widget:
            return
        
        from app.models.team_model import TeamModel
        try:
            equipos_dict = TeamModel.listar_equipos()
            if equipos_dict:
                self.equipos_disponibles = equipos_dict
                self.bracket_widget.populate_team_combos(equipos_dict)
        except Exception as e:
            print(f"Error cargando equipos en bracket: {e}")
    
    def crear_cabecera(self, layout_padre: QVBoxLayout):
        titulo = QLabel("Cuadro de eliminatorias")
        titulo.setObjectName("titleLabel")
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_padre.addWidget(titulo)
    
    def crear_botones_accion(self, layout_padre: QVBoxLayout):
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(10)
        
        self.randomizar_octavos = QPushButton("Randomizar octavos")
        self.guardar_emparejamientos = QPushButton("Guardar emparejamientos")
        self.guardar_emparejamientos.setObjectName("successButton")
        self.reiniciar_emparejamientos = QPushButton("Reiniciar emparejamientos")
        self.reiniciar_emparejamientos.setObjectName("dangerButton")
        
        layout_botones.addWidget(self.randomizar_octavos)
        layout_botones.addWidget(self.guardar_emparejamientos)
        layout_botones.addWidget(self.reiniciar_emparejamientos)
        layout_botones.addStretch()
        
        layout_padre.addLayout(layout_botones)
    
    def conectar_senales(self):
        # Conectar "Randomizar octavos" a la señal que el controlador escucha
        self.randomizar_octavos.clicked.connect(self._on_randomizar_wrapper)
        self.guardar_emparejamientos.clicked.connect(self.on_guardar_emparejamientos)
        self.reiniciar_emparejamientos.clicked.connect(self.on_reiniciar_emparejamientos)
    
    def _on_randomizar_wrapper(self):
        """Wrapper que emite la señal para que el controlador maneje la randomización.
        
        Este método captura errores y proporciona feedback al usuario.
        """
        try:
            print("[PAGE BRACKET] _on_randomizar_wrapper - INICIO")
            print("[PAGE BRACKET] Emitiendo señal randomizar_octavos_signal...")
            self.randomizar_octavos_signal.emit()
            print("[PAGE BRACKET] Señal randomizar_octavos_signal emitida correctamente")
        except Exception as e:
            print(f"[PAGE BRACKET] ❌ ERROR en _on_randomizar_wrapper: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error de randomización",
                f"Error al intentar randomizar octavos:\n{str(e)}"
            )
    
    def on_randomizar_octavos_OLD_VISUAL_ONLY(self):
        """MÉTODO ANTIGUO - SOLO CAMBIABA UI, NO PERSISTÍA EN BD.
        
        Este método está deprecado. Ahora se usa _on_randomizar_wrapper que emite
        una señal que el controlador captura para crear partidos reales en BD.
        """
        if not self.equipos_disponibles or len(self.equipos_disponibles) < 16:
            QMessageBox.warning(
                self,
                "Equipos insuficientes",
                f"Se necesitan 16 equipos para generar los octavos de final.\n"
                f"Actualmente hay {len(self.equipos_disponibles)} equipos disponibles."
            )
            return
        
        # Tomar los primeros 16 equipos y mezclarlos
        equipos_seleccionados = self.equipos_disponibles[:16]
        random.shuffle(equipos_seleccionados)
        
        # Rellenar los combos de octavos (solo octavos)
        all_octavos_combos = self.bracket_widget.combos_octavos_left + self.bracket_widget.combos_octavos_right
        
        for i, combo in enumerate(all_octavos_combos):
            if i < len(equipos_seleccionados):
                equipo = equipos_seleccionados[i]
                combo.blockSignals(True)
                idx = combo.findData(equipo['id'])
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                combo.blockSignals(False)
        
        QMessageBox.information(
            self,
            "Octavos randomizados",
            "Los emparejamientos de octavos se han generado aleatoriamente."
        )
    
    def on_reiniciar_emparejamientos(self):
        """Reinicia todos los emparejamientos del bracket."""
        respuesta = QMessageBox.question(
            self,
            "Confirmar reinicio",
            "¿Está seguro de que desea reiniciar todos los emparejamientos?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            # Resetear todos los combos
            all_combos = self.bracket_widget.get_all_combos()
            for combo in all_combos:
                combo.blockSignals(True)
                combo.setCurrentIndex(0)  # "Selecciona equipo..."
                combo.blockSignals(False)
            
            # Borrar estado guardado
            self.bracket_widget.bracket_state = None
            
            QMessageBox.information(
                self,
                "Reinicio completado",
                "Todos los emparejamientos han sido reiniciados."
            )
    
    def _on_reiniciar_wrapper(self):
        """Wrapper para emitir la señal de reinicio."""
        try:
            print("[PAGE BRACKET] _on_reiniciar_wrapper - Emitiendo reiniciar_emparejamientos_signal")
            self.reiniciar_emparejamientos_signal.emit()
        except Exception as e:
            print(f"[PAGE BRACKET] ❌ ERROR en _on_reiniciar_wrapper: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error de reinicio",
                f"Error al intentar reiniciar emparejamientos:\n{str(e)}"
            )
    
    def on_guardar_emparejamientos(self):
        """Guarda el estado actual de todos los emparejamientos."""
        # Recopilar todos los emparejamientos
        bracket_data = self._recopilar_bracket_completo()
        
        # Guardar en memoria (bracket_state)
        self.bracket_widget.bracket_state = bracket_data
        
        # Mostrar resumen en consola para verificación
        print("=== Estado del Bracket Guardado ===")
        print(f"Octavos: {len(bracket_data['octavos'])} enfrentamientos")
        print(f"Cuartos: {len(bracket_data['cuartos'])} enfrentamientos")
        print(f"Semifinales: {len(bracket_data['semifinales'])} enfrentamientos")
        print(f"Final: {len(bracket_data['final'])} enfrentamientos")
        print(json.dumps(bracket_data, indent=2, ensure_ascii=False))
        
        # Validar octavos antes de emitir señal
        emparejamientos_octavos = self.get_emparejamientos_octavos()
        
        # Validación básica de octavos
        valid = True
        for i, emp in enumerate(emparejamientos_octavos, 1):
            local = emp['local']
            visitante = emp['visitante']
            
            if local == "Selecciona equipo..." or visitante == "Selecciona equipo...":
                valid = False
                break
            
            if local == visitante:
                QMessageBox.warning(
                    self,
                    "Emparejamiento inválido",
                    f"El partido {i} tiene el mismo equipo como local y visitante."
                )
                return
        
        if not valid:
            QMessageBox.information(
                self,
                "Guardado con advertencia",
                "El bracket se ha guardado, pero algunos emparejamientos están incompletos."
            )
        else:
            # Verificar duplicados solo si está completo
            equipos_usados = []
            for emp in emparejamientos_octavos:
                if emp['local'] in equipos_usados:
                    QMessageBox.warning(
                        self,
                        "Equipo duplicado",
                        f"El equipo '{emp['local']}' está asignado en múltiples partidos."
                    )
                    return
                if emp['visitante'] in equipos_usados:
                    QMessageBox.warning(
                        self,
                        "Equipo duplicado",
                        f"El equipo '{emp['visitante']}' está asignado en múltiples partidos."
                    )
                    return
                equipos_usados.append(emp['local'])
                equipos_usados.append(emp['visitante'])
            
            QMessageBox.information(
                self,
                "Guardado correctamente",
                "Los emparejamientos se han guardado correctamente."
            )
        
        # Emitir señal con los octavos (compatibilidad con controlador)
        self.guardar_emparejamientos_signal.emit(emparejamientos_octavos)
    
    def _recopilar_bracket_completo(self) -> dict:
        """Recopila el estado completo del bracket desde todos los combos."""
        bracket_data = {
            "octavos": [],
            "cuartos": [],
            "semifinales": [],
            "final": []
        }
        
        # Octavos
        all_octavos = self.bracket_widget.combos_octavos_left + self.bracket_widget.combos_octavos_right
        for i in range(0, len(all_octavos), 2):
            if i+1 < len(all_octavos):
                equipo_a = all_octavos[i].currentText()
                equipo_b = all_octavos[i+1].currentText()
                bracket_data["octavos"].append((equipo_a, equipo_b))
        
        # Cuartos
        all_cuartos = self.bracket_widget.combos_cuartos_left + self.bracket_widget.combos_cuartos_right
        for i in range(0, len(all_cuartos), 2):
            if i+1 < len(all_cuartos):
                equipo_a = all_cuartos[i].currentText()
                equipo_b = all_cuartos[i+1].currentText()
                bracket_data["cuartos"].append((equipo_a, equipo_b))
        
        # Semifinales
        all_semis = self.bracket_widget.combos_semis_left + self.bracket_widget.combos_semis_right
        for i in range(0, len(all_semis), 2):
            if i+1 < len(all_semis):
                equipo_a = all_semis[i].currentText()
                equipo_b = all_semis[i+1].currentText()
                bracket_data["semifinales"].append((equipo_a, equipo_b))
        
        # Final
        if self.bracket_widget.combo_finalista_left and self.bracket_widget.combo_finalista_right:
            finalista_a = self.bracket_widget.combo_finalista_left.currentText()
            finalista_b = self.bracket_widget.combo_finalista_right.currentText()
            bracket_data["final"].append((finalista_a, finalista_b))
        
        return bracket_data
    
    def get_emparejamientos_octavos(self) -> list[dict]:
        emparejamientos = []
        if not self.bracket_widget:
            return emparejamientos
        
        combos_left = self.bracket_widget.combos_octavos_left
        combos_right = self.bracket_widget.combos_octavos_right
        
        for i in range(0, len(combos_left), 2):
            if i+1 < len(combos_left):
                emp = {
                    'local': combos_left[i].currentText(),
                    'visitante': combos_left[i+1].currentText()
                }
                emparejamientos.append(emp)
        
        for i in range(0, len(combos_right), 2):
            if i+1 < len(combos_right):
                emp = {
                    'local': combos_right[i].currentText(),
                    'visitante': combos_right[i+1].currentText()
                }
                emparejamientos.append(emp)
        
        return emparejamientos
    
    def obtener_emparejamientos(self) -> list[dict]:
        return self.get_emparejamientos_octavos()
    
    def set_emparejamientos_octavos(self, emparejamientos: list[dict]):
        if not self.bracket_widget:
            return
        
        combos_left = self.bracket_widget.combos_octavos_left
        combos_right = self.bracket_widget.combos_octavos_right
        
        all_octavos = combos_left + combos_right
        
        idx = 0
        for emp in emparejamientos[:8]:
            local = emp.get('local', 'Selecciona equipo...')
            visitante = emp.get('visitante', 'Selecciona equipo...')
            
            if idx < len(all_octavos):
                index_local = all_octavos[idx].findText(local)
                if index_local >= 0:
                    all_octavos[idx].setCurrentIndex(index_local)
                idx += 1
            
            if idx < len(all_octavos):
                index_visitante = all_octavos[idx].findText(visitante)
                if index_visitante >= 0:
                    all_octavos[idx].setCurrentIndex(index_visitante)
                idx += 1
    
    def set_cuadro(self, datos: dict):
        """Actualiza el cuadro visual con los datos de los partidos."""
        print(f"\n[PageBracket set_cuadro] Recibiendo datos:")
        for ronda, partidos in datos.items():
            print(f"  {ronda}: {len(partidos)} partidos")
            for p in partidos[:2]:  # Primeros 2 partidos de cada ronda
                print(f"    - Slot {p.get('slot')}: {p.get('local_nombre')} vs {p.get('visitante_nombre')}")
        
        if not self.bracket_widget:
            return
        
        # Mapeo de combos por ronda
        combos_map = {
            'Octavos': {
                'left': self.bracket_widget.combos_octavos_left,
                'right': self.bracket_widget.combos_octavos_right
            },
            'Cuartos': {
                'left': self.bracket_widget.combos_cuartos_left,
                'right': self.bracket_widget.combos_cuartos_right
            },
            'Semifinal': {
                'left': self.bracket_widget.combos_semis_left,
                'right': self.bracket_widget.combos_semis_right
            }
        }
        
        # Limpiar todo primero
        self.limpiar_cuadro()
        
        print(f"[PageBracket set_cuadro] Cuadro limpiado, comenzando a rellenar...")
        
        # Rellenar cada ronda
        for ronda, partidos in datos.items():
            if ronda not in combos_map:
                print(f"[PageBracket set_cuadro] Ignorando ronda '{ronda}' (no está en combos_map)")
                continue
            
            print(f"[PageBracket set_cuadro] Procesando {ronda}: {len(partidos)} partidos")
            
            # Separar partidos por lado según la ronda
            # Para Octavos: slots impares (1,3,5,7) → izquierda, pares (2,4,6,8) → derecha
            # Para Cuartos: slots 1,2 → izquierda, slots 3,4 → derecha
            # Para Semifinal: slot 1 → izquierda, slot 2 → derecha
            if ronda == 'Octavos':
                partidos_left = [p for p in partidos if p.get('slot', 0) % 2 == 1]
                partidos_right = [p for p in partidos if p.get('slot', 0) % 2 == 0]
            elif ronda == 'Cuartos':
                partidos_left = [p for p in partidos if p.get('slot', 0) in [1, 2]]
                partidos_right = [p for p in partidos if p.get('slot', 0) in [3, 4]]
            elif ronda == 'Semifinal':
                partidos_left = [p for p in partidos if p.get('slot', 0) == 1]
                partidos_right = [p for p in partidos if p.get('slot', 0) == 2]
            else:
                # Fallback: lógica anterior
                partidos_left = [p for p in partidos if p.get('slot', 0) % 2 == 1]
                partidos_right = [p for p in partidos if p.get('slot', 0) % 2 == 0]
            
            print(f"[PageBracket set_cuadro]   - Izquierda: {len(partidos_left)} partidos {[p.get('slot') for p in partidos_left]}")
            print(f"[PageBracket set_cuadro]   - Derecha: {len(partidos_right)} partidos {[p.get('slot') for p in partidos_right]}")
            
            # Rellenar lado izquierdo
            combos_left = combos_map[ronda]['left']
            for i, partido in enumerate(partidos_left):
                if i * 2 < len(combos_left):
                    # Combo A (local)
                    combo_a = combos_left[i * 2]
                    local_id = partido.get('equipo_local_id')
                    
                    # Hacer visible el match_card padre si hay equipos
                    if local_id or partido.get('equipo_visitante_id'):
                        match_card = combo_a.parent()
                        if match_card:
                            match_card.show()
                    
                    if local_id:
                        idx = combo_a.findData(local_id)
                        if idx >= 0:
                            combo_a.blockSignals(True)
                            combo_a.setCurrentIndex(idx)
                            combo_a.blockSignals(False)
                            # Marcar ganador con estilo que funciona en modo claro y oscuro
                            if partido.get('ganador_equipo_id') == local_id:
                                combo_a.setStyleSheet("""
                                    QComboBox {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(40, 167, 69, 0.3),
                                            stop:1 rgba(40, 167, 69, 0.15));
                                        border: 2px solid #28a745;
                                        font-weight: bold;
                                        color: #28a745;
                                    }
                                    QComboBox:disabled {
                                        color: #1e7e34;
                                    }
                                """)
                    
                    # Combo B (visitante)
                    if i * 2 + 1 < len(combos_left):
                        combo_b = combos_left[i * 2 + 1]
                        visitante_id = partido.get('equipo_visitante_id')
                        if visitante_id:
                            idx = combo_b.findData(visitante_id)
                            if idx >= 0:
                                combo_b.blockSignals(True)
                                combo_b.setCurrentIndex(idx)
                                combo_b.blockSignals(False)
                                # Marcar ganador con estilo que funciona en modo claro y oscuro
                                if partido.get('ganador_equipo_id') == visitante_id:
                                    combo_b.setStyleSheet("""
                                        QComboBox {
                                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(40, 167, 69, 0.3),
                                                stop:1 rgba(40, 167, 69, 0.15));
                                        border: 2px solid #28a745;
                                        font-weight: bold;
                                        color: #28a745;
                                    }
                                    QComboBox:disabled {
                                        color: #1e7e34;
                                    }
                                """)
                        # Rellenar lado derecho
            combos_right = combos_map[ronda]['right']
            for i, partido in enumerate(partidos_right):
                if i * 2 < len(combos_right):
                    # Combo A (local)
                    combo_a = combos_right[i * 2]
                    local_id = partido.get('equipo_local_id')
                    
                    # Hacer visible el match_card padre si hay equipos
                    if local_id or partido.get('equipo_visitante_id'):
                        match_card = combo_a.parent()
                        if match_card:
                            match_card.show()
                    
                    if local_id:
                        idx = combo_a.findData(local_id)
                        if idx >= 0:
                            combo_a.blockSignals(True)
                            combo_a.setCurrentIndex(idx)
                            combo_a.blockSignals(False)
                            # Marcar ganador con estilo que funciona en modo claro y oscuro
                            if partido.get('ganador_equipo_id') == local_id:
                                combo_a.setStyleSheet("""
                                    QComboBox {
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(40, 167, 69, 0.3),
                                            stop:1 rgba(40, 167, 69, 0.15));
                                        border: 2px solid #28a745;
                                        font-weight: bold;
                                        color: #28a745;
                                    }
                                    QComboBox:disabled {
                                        color: #1e7e34;
                                    }
                                """)
                    
                    # Combo B (visitante)
                    if i * 2 + 1 < len(combos_right):
                        combo_b = combos_right[i * 2 + 1]
                        visitante_id = partido.get('equipo_visitante_id')
                        if visitante_id:
                            idx = combo_b.findData(visitante_id)
                            if idx >= 0:
                                combo_b.blockSignals(True)
                                combo_b.setCurrentIndex(idx)
                                combo_b.blockSignals(False)
                                # Marcar ganador con estilo que funciona en modo claro y oscuro
                                if partido.get('ganador_equipo_id') == visitante_id:
                                    combo_b.setStyleSheet("""
                                        QComboBox {
                                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(40, 167, 69, 0.3),
                                                stop:1 rgba(40, 167, 69, 0.15));
                                            border: 2px solid #28a745;
                                            font-weight: bold;
                                            color: #28a745;
                                        }
                                        QComboBox:disabled {
                                            color: #1e7e34;
                                        }
                                    """)
        
        # Rellenar finalistas si existe la Final
        if 'Final' in datos and len(datos['Final']) > 0:
            final = datos['Final'][0]
            
            # Finalista izquierdo (local)
            if self.bracket_widget.combo_finalista_left:
                local_id = final.get('equipo_local_id')
                if local_id:
                    idx = self.bracket_widget.combo_finalista_left.findData(local_id)
                    if idx >= 0:
                        self.bracket_widget.combo_finalista_left.blockSignals(True)
                        self.bracket_widget.combo_finalista_left.setCurrentIndex(idx)
                        self.bracket_widget.combo_finalista_left.blockSignals(False)
                        # Marcar campeón con estilo dorado que funciona en ambos modos
                        if final.get('ganador_equipo_id') == local_id:
                            self.bracket_widget.combo_finalista_left.setStyleSheet("""
                                QComboBox {
                                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 rgba(255, 215, 0, 0.4),
                                        stop:1 rgba(255, 215, 0, 0.2));
                                    border: 2px solid #FFD700;
                                    font-weight: bold;
                                    color: #B8860B;
                                }
                                QComboBox:disabled {
                                    color: #8B6914;
                                }
                            """)
            
            # Finalista derecho (visitante)
            if self.bracket_widget.combo_finalista_right:
                visitante_id = final.get('equipo_visitante_id')
                if visitante_id:
                    idx = self.bracket_widget.combo_finalista_right.findData(visitante_id)
                    if idx >= 0:
                        self.bracket_widget.combo_finalista_right.blockSignals(True)
                        self.bracket_widget.combo_finalista_right.setCurrentIndex(idx)
                        self.bracket_widget.combo_finalista_right.blockSignals(False)
                        # Marcar campeón con estilo dorado que funciona en ambos modos
                        if final.get('ganador_equipo_id') == visitante_id:
                            self.bracket_widget.combo_finalista_right.setStyleSheet("""
                                QComboBox {
                                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 rgba(255, 215, 0, 0.4),
                                        stop:1 rgba(255, 215, 0, 0.2));
                                    border: 2px solid #FFD700;
                                    font-weight: bold;
                                    color: #B8860B;
                                }
                                QComboBox:disabled {
                                    color: #8B6914;
                                }
                            """)
        
        # Actualizar visibilidad de las coronas con el ID del ganador
        ganador_id = None
        if 'Final' in datos and len(datos['Final']) > 0:
            ganador_id = datos['Final'][0].get('ganador_equipo_id')
        
        if self.bracket_widget:
            self.bracket_widget.update_crown_visibility(ganador_id)
    
    def actualizar_cuadro_visual(self, datos: dict):
        """Alias para set_cuadro para compatibilidad."""
        self.set_cuadro(datos)
    
    def limpiar_cuadro(self):
        """Limpia todos los combos del cuadro y resetea estilos."""
        if self.bracket_widget:
            all_combos = self.bracket_widget.get_all_combos()
            for combo in all_combos:
                combo.setCurrentIndex(0)
                combo.setStyleSheet("")  # Resetear estilos (quitar marcas de ganador)
            
            # Ocultar coronas al limpiar (sin ganador)
            self.bracket_widget.update_crown_visibility(ganador_equipo_id=None)
    
    def set_modo(self, modo: str):
        self.modo_actual = modo
        
        if not self.bracket_widget:
            return
        
        all_combos = self.bracket_widget.get_all_combos()
        
        if modo == "solo_lectura":
            for combo in all_combos:
                combo.setEnabled(False)
            
            self.randomizar_octavos.setEnabled(False)
            self.guardar_emparejamientos.setEnabled(False)
            self.reiniciar_emparejamientos.setEnabled(False)
            
        elif modo == "configurable":
            for combo in all_combos:
                combo.setEnabled(True)
            
            self.randomizar_octavos.setEnabled(True)
            self.guardar_emparejamientos.setEnabled(True)
            self.reiniciar_emparejamientos.setEnabled(True)


PageBracket = PageCuadroEliminatorias
