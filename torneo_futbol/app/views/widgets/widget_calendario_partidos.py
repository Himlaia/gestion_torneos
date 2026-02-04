from PySide6.QtWidgets import QCalendarWidget
from PySide6.QtCore import Qt, QDate, Signal, QRect
from PySide6.QtGui import QTextCharFormat, QColor, QPainter
from datetime import date


class CalendarioPartidos(QCalendarWidget):
    
    dia_clicked_signal = Signal(QDate)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.marked_dates = {}  # QDate -> QColor
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.clicked.connect(self._on_date_clicked)
        
    def setMarkedDates(self, dates_with_color: dict):
        """Set dates to mark with colored dots. dates_with_color is a dict {QDate: QColor}"""
        self.marked_dates = dates_with_color
        try:
            if hasattr(self, 'viewport') and callable(self.viewport):
                self.viewport().update()
            else:
                self.update()
        except Exception as e:
            print(f"[CALENDARIO DEBUG] Error en setMarkedDates: {e}")
            self.update()  # Fallback
    
    def paintCell(self, painter: QPainter, rect: QRect, date: QDate):
        """Override paintCell to draw custom indicators (dots) on marked dates."""
        super().paintCell(painter, rect, date)
        
        if date in self.marked_dates:
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            
            color = self.marked_dates[date]
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Draw small circle in bottom-right corner
            dot_size = 7
            margin = 4
            center_x = rect.right() - margin - dot_size // 2
            center_y = rect.bottom() - margin - dot_size // 2
            
            painter.drawEllipse(center_x - dot_size // 2, center_y - dot_size // 2, dot_size, dot_size)
            painter.restore()
    
    def set_partidos(self, partidos: list[dict]):
        """Legacy method for compatibility. Extracts dates and marks them."""
        partidos_por_dia = {}
        
        for partido in partidos:
            fecha_str = partido.get('fecha_hora', '')
            if not fecha_str:
                continue
            
            try:
                if ' ' in fecha_str:
                    fecha_str = fecha_str.split(' ')[0]
                
                parts = fecha_str.split('-')
                if len(parts) == 3:
                    anio = int(parts[0])
                    mes = int(parts[1])
                    dia = int(parts[2])
                    fecha = date(anio, mes, dia)
                    
                    if fecha not in partidos_por_dia:
                        partidos_por_dia[fecha] = []
                    partidos_por_dia[fecha].append(partido)
            except:
                continue
        
        # Convert to marked dates with color
        marked = {}
        for fecha, lista_partidos in partidos_por_dia.items():
            qdate = QDate(fecha.year, fecha.month, fecha.day)
            
            tiene_pendiente = any(p.get('estado') == 'Pendiente' for p in lista_partidos)
            tiene_jugado = any(p.get('estado') == 'Jugado' for p in lista_partidos)
            
            # Teal/green dot
            if tiene_jugado:
                color = QColor(22, 160, 133)  # Green/teal
            elif tiene_pendiente:
                color = QColor(22, 160, 133)  # Same color for consistency
            else:
                color = QColor(22, 160, 133)
            
            marked[qdate] = color
        
        self.setMarkedDates(marked)
    
    def refresh_calendar_marks(self):
        """Refresh calendar marks by querying database for programmed matches."""
        from app.models.match_model import MatchModel
        
        try:
            partidos = MatchModel.listar_partidos()
            fechas_con_partidos = {}
            
            for partido in partidos:
                fecha_str = partido.get('fecha_hora', '')
                if not fecha_str:
                    continue
                
                try:
                    if ' ' in fecha_str:
                        fecha_str = fecha_str.split(' ')[0]
                    
                    parts = fecha_str.split('-')
                    if len(parts) == 3:
                        anio = int(parts[0])
                        mes = int(parts[1])
                        dia = int(parts[2])
                        fecha = date(anio, mes, dia)
                        
                        if fecha not in fechas_con_partidos:
                            fechas_con_partidos[fecha] = []
                        fechas_con_partidos[fecha].append(partido)
                except:
                    continue
            
            # Apply marking
            marked = {}
            for fecha, lista_partidos in fechas_con_partidos.items():
                qdate = QDate(fecha.year, fecha.month, fecha.day)
                
                tiene_pendiente = any(p.get('estado') == 'Pendiente' for p in lista_partidos)
                tiene_jugado = any(p.get('estado') == 'Jugado' for p in lista_partidos)
                
                # Teal/green dot
                if tiene_jugado:
                    color = QColor(22, 160, 133)
                elif tiene_pendiente:
                    color = QColor(22, 160, 133)
                else:
                    color = QColor(22, 160, 133)
                
                marked[qdate] = color
            
            self.setMarkedDates(marked)
        except:
            pass
    
    def _on_date_clicked(self, qdate: QDate):
        self.dia_clicked_signal.emit(qdate)
    
    def cambiar_mes(self, anio: int, mes: int):
        self.setCurrentPage(anio, mes)
