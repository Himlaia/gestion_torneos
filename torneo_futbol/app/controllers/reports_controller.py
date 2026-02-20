"""Controlador de informes PDF."""
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from app.models.team_model import TeamModel
from app.models.match_model import MatchModel
from app.services.report_service import ReportService
from app.views.page_reports import PageReports


class ControladorReportes:
    """Orquesta la generación de informes PDF."""

    def __init__(self, vista: PageReports):
        self.vista = vista
        self._ultimo_pdf: str = ""
        self._conectar_senales()
        self.cargar_filtros()

    def _conectar_senales(self):
        self.vista.generar_signal.connect(self._on_generar)
        self.vista.guardar_como_signal.connect(self._on_guardar_como)

    # ── Carga de datos para filtros ──────────
    def cargar_filtros(self):
        """Carga equipos y fases disponibles en los combos de filtro."""
        try:
            # Equipos
            equipos_raw = TeamModel.listar_equipos()
            equipos = [{"id": e["id"], "nombre": e["nombre"]} for e in equipos_raw]
            self.vista.set_equipos(equipos)

            # Fases con partidos
            partidos = MatchModel.listar_partidos()
            fases_set = set()
            for p in partidos:
                elim = p.get("eliminatoria")
                if elim:
                    fases_set.add(elim.lower())

            orden = ["octavos", "cuartos", "semifinal", "final"]
            fases = [f for f in orden if f in fases_set]
            self.vista.set_eliminatorias(fases)
        except Exception as e:
            print(f"[REPORTS] Error cargando filtros: {e}")

    # ── Generación ───────────────────────────
    def _on_generar(self):
        """Genera el PDF del tipo seleccionado."""
        tipo = self.vista.get_tipo_informe()
        self.vista.clear_status()

        try:
            if tipo == "equipos_jugadores":
                equipo_id = self.vista.get_equipo_id()
                path = ReportService.generate_equipos_jugadores(
                    equipo_id=equipo_id
                )
            elif tipo == "partidos_resultados":
                eliminatoria = self.vista.get_eliminatoria()
                path = ReportService.generate_partidos_resultados(
                    eliminatoria=eliminatoria
                )
            elif tipo == "clasificacion":
                eliminatoria = self.vista.get_eliminatoria()
                path = ReportService.generate_clasificacion_eliminatorias(
                    eliminatoria=eliminatoria
                )
            else:
                self.vista.set_status("Tipo de informe no reconocido", is_success=False)
                return

            self._ultimo_pdf = path
            self.vista.set_status(
                f"PDF generado correctamente",
                is_success=True
            )
            self.vista.set_ultimo_pdf(path)

            # Abrir el PDF generado
            self._abrir_pdf(path)

        except Exception as e:
            self.vista.set_status(f"Error: {e}", is_success=False)
            print(f"[REPORTS ERROR] {e}")

    # ── Guardar como ─────────────────────────
    def _on_guardar_como(self):
        """Genera el PDF y permite al usuario elegir la ruta."""
        tipo = self.vista.get_tipo_informe()
        nombres = {
            "equipos_jugadores": "equipos_jugadores.pdf",
            "partidos_resultados": "partidos_resultados.pdf",
            "clasificacion": "clasificacion_eliminatorias.pdf",
        }
        nombre_default = nombres.get(tipo, "informe.pdf")

        path, _ = QFileDialog.getSaveFileName(
            self.vista,
            "Guardar informe como",
            nombre_default,
            "Archivos PDF (*.pdf)"
        )
        if not path:
            return

        self.vista.clear_status()

        try:
            if tipo == "equipos_jugadores":
                equipo_id = self.vista.get_equipo_id()
                result = ReportService.generate_equipos_jugadores(
                    output_path=path, equipo_id=equipo_id
                )
            elif tipo == "partidos_resultados":
                eliminatoria = self.vista.get_eliminatoria()
                result = ReportService.generate_partidos_resultados(
                    output_path=path, eliminatoria=eliminatoria
                )
            elif tipo == "clasificacion":
                eliminatoria = self.vista.get_eliminatoria()
                result = ReportService.generate_clasificacion_eliminatorias(
                    output_path=path, eliminatoria=eliminatoria
                )
            else:
                self.vista.set_status("Tipo no reconocido", is_success=False)
                return

            self._ultimo_pdf = result
            self.vista.set_status(
                f"PDF guardado correctamente",
                is_success=True
            )
            self.vista.set_ultimo_pdf(result)

        except Exception as e:
            self.vista.set_status(f"Error: {e}", is_success=False)
            print(f"[REPORTS ERROR] {e}")

    # ── Abrir PDF ────────────────────────────
    @staticmethod
    def _abrir_pdf(path: str):
        """Abre el PDF con el visor del sistema."""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            print(f"[REPORTS] No se pudo abrir el PDF: {e}")
