"""Widget visual para mostrar el cuadro de eliminatorias con estilo bracket clásico."""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush
from typing import Union


class WidgetCuadroVisual(QWidget):
    """
    Widget que dibuja el cuadro de eliminatorias de 16 equipos con estructura simétrica.
    El bracket se organiza con dos mitades (izquierda/derecha) que convergen en el centro.
    """
    
    def __init__(self, parent=None):
        """Inicializa el widget visual del cuadro."""
        super().__init__(parent)
        self.datos_cuadro = None
        self.setMinimumSize(1400, 900)
        
        # Colores
        self.color_caja = QColor(44, 62, 80)
        self.color_borde = QColor(52, 152, 219)
        self.color_texto = QColor(255, 255, 255)
        self.color_linea = QColor(52, 152, 219)
        self.color_campeon = QColor(241, 196, 15)
        self.color_texto_campeon = QColor(44, 62, 80)
    
    def setData(self, data: dict):
        """
        Establece los datos del cuadro y actualiza la visualización.
        
        Args:
            data: Diccionario con estructura:
                {
                    "octavos": [tupla/lista/dict, ...] x 8,
                    "cuartos": [...] x 4,
                    "semifinales": [...] x 2,
                    "final": [tupla/lista/dict] x 1,
                    "campeon": str | None
                }
        """
        self.datos_cuadro = data
        self.update()
    
    def set_datos_cuadro(self, datos: dict):
        """Alias de setData para mantener compatibilidad."""
        self.setData(datos)
    
    def paintEvent(self, event):
        """Dibuja el cuadro de eliminatorias completo con estructura simétrica."""
        super().paintEvent(event)
        
        if not self.datos_cuadro:
            self._dibujar_mensaje_vacio()
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Dimensiones
        ancho_caja = 160
        alto_caja = 45
        radio = 8
        margen_lateral = 30
        margen_top = 40
        espacio_equipo = 8
        espacio_vertical = 20
        
        # Posiciones X simétricas
        espacio_ronda = (w - 2 * margen_lateral - 2 * ancho_caja) / 7
        
        # Izquierda
        x_oct_izq = margen_lateral
        x_cuartos_izq = x_oct_izq + ancho_caja + espacio_ronda
        x_semi_izq = x_cuartos_izq + ancho_caja + espacio_ronda
        
        # Derecha (espejo)
        x_semi_der = w - margen_lateral - ancho_caja
        x_cuartos_der = x_semi_der - ancho_caja - espacio_ronda
        x_oct_der = x_cuartos_der - ancho_caja - espacio_ronda
        
        # Centro
        x_final = (w - ancho_caja) / 2
        
        # Extraer datos
        octavos = self.datos_cuadro.get("octavos", [])
        cuartos = self.datos_cuadro.get("cuartos", [])
        semifinales = self.datos_cuadro.get("semifinales", [])
        final = self.datos_cuadro.get("final", [])
        campeon = self.datos_cuadro.get("campeon")
        
        # Guardar posiciones para líneas
        pos_oct_izq = []
        pos_oct_der = []
        pos_cuartos_izq = []
        pos_cuartos_der = []
        pos_semi_izq = []
        pos_semi_der = []
        pos_final = []
        
        # ===== OCTAVOS IZQUIERDA =====
        y = margen_top
        for i in range(4):
            local, visitante = self._extraer_equipos(octavos[i] if i < len(octavos) else None)
            
            rect_local = QRectF(x_oct_izq, y, ancho_caja, alto_caja)
            self._dibujar_caja(painter, rect_local, local, radio)
            
            y_vis = y + alto_caja + espacio_equipo
            rect_vis = QRectF(x_oct_izq, y_vis, ancho_caja, alto_caja)
            self._dibujar_caja(painter, rect_vis, visitante, radio)
            
            y_centro = y + alto_caja + espacio_equipo / 2
            pos_oct_izq.append((x_oct_izq + ancho_caja, y_centro))
            
            y = y_vis + alto_caja + espacio_vertical
        
        # ===== OCTAVOS DERECHA =====
        y = margen_top
        for i in range(4, 8):
            local, visitante = self._extraer_equipos(octavos[i] if i < len(octavos) else None)
            
            rect_local = QRectF(x_oct_der, y, ancho_caja, alto_caja)
            self._dibujar_caja(painter, rect_local, local, radio)
            
            y_vis = y + alto_caja + espacio_equipo
            rect_vis = QRectF(x_oct_der, y_vis, ancho_caja, alto_caja)
            self._dibujar_caja(painter, rect_vis, visitante, radio)
            
            y_centro = y + alto_caja + espacio_equipo / 2
            pos_oct_der.append((x_oct_der, y_centro))
            
            y = y_vis + alto_caja + espacio_vertical
        
        # ===== CUARTOS IZQUIERDA =====
        for i in range(2):
            local, visitante = self._extraer_equipos(cuartos[i] if i < len(cuartos) else None)
            
            # Calcular Y basado en octavos para alineación
            y1, y2 = pos_oct_izq[i*2][1], pos_oct_izq[i*2+1][1]
            y_centro = (y1 + y2) / 2
            y_local = y_centro - alto_caja - espacio_equipo / 2
            
            rect_local = QRectF(x_cuartos_izq, y_local, ancho_caja, alto_caja)
            self._dibujar_caja(painter, rect_local, local, radio)
            
            y_vis = y_local + alto_caja + espacio_equipo
            rect_vis = QRectF(x_cuartos_izq, y_vis, ancho_caja, alto_caja)
            self._dibujar_caja(painter, rect_vis, visitante, radio)
            
            pos_cuartos_izq.append((x_cuartos_izq + ancho_caja, y_local + alto_caja + espacio_equipo / 2))
        
        # ===== CUARTOS DERECHA =====
        for i in range(2):
            local, visitante = self._extraer_equipos(cuartos[i + 2] if i + 2 < len(cuartos) else None)
            
            y1, y2 = pos_oct_der[i*2][1], pos_oct_der[i*2+1][1]
            y_centro = (y1 + y2) / 2
            y_local = y_centro - alto_caja - espacio_equipo / 2
            
            rect_local = QRectF(x_cuartos_der, y_local, ancho_caja, alto_caja)
            self._dibujar_caja(painter, rect_local, local, radio)
            
            y_vis = y_local + alto_caja + espacio_equipo
            rect_vis = QRectF(x_cuartos_der, y_vis, ancho_caja, alto_caja)
            self._dibujar_caja(painter, rect_vis, visitante, radio)
            
            pos_cuartos_der.append((x_cuartos_der, y_local + alto_caja + espacio_equipo / 2))
        
        # ===== SEMIFINAL IZQUIERDA =====
        local, visitante = self._extraer_equipos(semifinales[0] if len(semifinales) > 0 else None)
        y1, y2 = pos_cuartos_izq[0][1], pos_cuartos_izq[1][1]
        y_centro = (y1 + y2) / 2
        y_local = y_centro - alto_caja - espacio_equipo / 2
        
        rect_local = QRectF(x_semi_izq, y_local, ancho_caja, alto_caja)
        self._dibujar_caja(painter, rect_local, local, radio)
        
        y_vis = y_local + alto_caja + espacio_equipo
        rect_vis = QRectF(x_semi_izq, y_vis, ancho_caja, alto_caja)
        self._dibujar_caja(painter, rect_vis, visitante, radio)
        
        pos_semi_izq.append((x_semi_izq + ancho_caja, y_local + alto_caja + espacio_equipo / 2))
        
        # ===== SEMIFINAL DERECHA =====
        local, visitante = self._extraer_equipos(semifinales[1] if len(semifinales) > 1 else None)
        y1, y2 = pos_cuartos_der[0][1], pos_cuartos_der[1][1]
        y_centro = (y1 + y2) / 2
        y_local = y_centro - alto_caja - espacio_equipo / 2
        
        rect_local = QRectF(x_semi_der, y_local, ancho_caja, alto_caja)
        self._dibujar_caja(painter, rect_local, local, radio)
        
        y_vis = y_local + alto_caja + espacio_equipo
        rect_vis = QRectF(x_semi_der, y_vis, ancho_caja, alto_caja)
        self._dibujar_caja(painter, rect_vis, visitante, radio)
        
        pos_semi_der.append((x_semi_der, y_local + alto_caja + espacio_equipo / 2))
        
        # ===== FINAL =====
        local, visitante = self._extraer_equipos(final[0] if len(final) > 0 else None)
        y1, y2 = pos_semi_izq[0][1], pos_semi_der[0][1]
        y_centro = (y1 + y2) / 2
        y_local = y_centro - alto_caja - espacio_equipo / 2
        
        rect_local = QRectF(x_final, y_local, ancho_caja, alto_caja)
        self._dibujar_caja(painter, rect_local, local, radio)
        
        y_vis = y_local + alto_caja + espacio_equipo
        rect_vis = QRectF(x_final, y_vis, ancho_caja, alto_caja)
        self._dibujar_caja(painter, rect_vis, visitante, radio)
        
        y_centro_final = y_local + alto_caja + espacio_equipo / 2
        pos_final.append((x_final + ancho_caja / 2, y_centro_final))
        
        # ===== CAMPEÓN =====
        if campeon:
            y_camp = y_vis + alto_caja + 30
            ancho_camp = ancho_caja + 40
            x_camp = (w - ancho_camp) / 2
            rect_camp = QRectF(x_camp, y_camp, ancho_camp, alto_caja + 15)
            
            painter.setBrush(QBrush(self.color_campeon))
            painter.setPen(QPen(self.color_campeon.darker(120), 3))
            painter.drawRoundedRect(rect_camp, radio + 2, radio + 2)
            
            font = QFont("Arial", 14, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(self.color_texto_campeon))
            painter.drawText(rect_camp, Qt.AlignmentFlag.AlignCenter, f"🏆 {campeon}")
            
            # Línea al campeón
            painter.setPen(QPen(self.color_linea, 2))
            x_centro = x_final + ancho_caja / 2
            painter.drawLine(QPointF(x_centro, y_vis + alto_caja), QPointF(x_centro, y_camp))
        
        # ===== LÍNEAS =====
        self._dibujar_lineas(painter, pos_oct_izq, pos_cuartos_izq)
        self._dibujar_lineas(painter, pos_oct_der, pos_cuartos_der)
        self._dibujar_lineas(painter, pos_cuartos_izq, pos_semi_izq)
        self._dibujar_lineas(painter, pos_cuartos_der, pos_semi_der)
        
        # Líneas a la final
        painter.setPen(QPen(self.color_linea, 2))
        if pos_semi_izq and pos_final:
            painter.drawLine(QPointF(pos_semi_izq[0][0], pos_semi_izq[0][1]), 
                           QPointF(pos_final[0][0], pos_final[0][1]))
        if pos_semi_der and pos_final:
            painter.drawLine(QPointF(pos_semi_der[0][0], pos_semi_der[0][1]), 
                           QPointF(pos_final[0][0], pos_final[0][1]))
    
    def _dibujar_caja(self, painter: QPainter, rect: QRectF, texto: str, radio: int):
        """Dibuja una caja redondeada con texto."""
        painter.setBrush(QBrush(self.color_caja))
        painter.setPen(QPen(self.color_borde, 2))
        painter.drawRoundedRect(rect, radio, radio)
        
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(self.color_texto))
        
        metrics = painter.fontMetrics()
        if metrics.horizontalAdvance(texto) > rect.width() - 10:
            texto = metrics.elidedText(texto, Qt.TextElideMode.ElideRight, int(rect.width() - 10))
        
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, texto)
    
    def _dibujar_lineas(self, painter: QPainter, origen: list, destino: list):
        """Dibuja líneas tipo bracket entre rondas."""
        painter.setPen(QPen(self.color_linea, 2))
        
        for i in range(len(destino)):
            x1_1, y1_1 = origen[i*2]
            x1_2, y1_2 = origen[i*2+1]
            x2, y2 = destino[i]
            
            x_medio = (x1_1 + x2) / 2
            y_medio = (y1_1 + y1_2) / 2
            
            # Líneas horizontales desde partidos origen
            painter.drawLine(QPointF(x1_1, y1_1), QPointF(x_medio, y1_1))
            painter.drawLine(QPointF(x1_2, y1_2), QPointF(x_medio, y1_2))
            
            # Líneas verticales convergiendo
            painter.drawLine(QPointF(x_medio, y1_1), QPointF(x_medio, y_medio))
            painter.drawLine(QPointF(x_medio, y1_2), QPointF(x_medio, y_medio))
            
            # Línea hacia destino
            painter.drawLine(QPointF(x_medio, y_medio), QPointF(x2, y2))
    
    def _extraer_equipos(self, partido: Union[tuple, list, dict, None]) -> tuple:
        """Extrae los nombres de equipos del formato del partido."""
        if isinstance(partido, dict):
            return (partido.get("local", "Pendiente"), partido.get("visitante", "Pendiente"))
        elif isinstance(partido, (tuple, list)) and len(partido) >= 2:
            return (str(partido[0]), str(partido[1]))
        return ("Pendiente", "Pendiente")
    
    def _dibujar_mensaje_vacio(self):
        """Dibuja un mensaje cuando no hay datos."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        font = QFont("Arial", 16)
        painter.setFont(font)
        painter.setPen(QPen(QColor(127, 140, 141)))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No hay datos del cuadro disponibles")
