"""Servicio de generación de informes PDF con fpdf2."""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fpdf import FPDF

from app.config import RESOURCES_DIR, REPORTS_GENERATED_DIR
from app.models.db import get_connection


# ──────────────────────────────────────────────
#  Clase base PDF con estilo del torneo
# ──────────────────────────────────────────────
class TournamentPDF(FPDF):
    """PDF base con header/footer estilizados para el torneo."""

    ACCENT = (22, 160, 133)       # #16a085
    TEXT_DARK = (44, 62, 80)      # #2c3e50
    TEXT_LIGHT = (255, 255, 255)
    HEADER_BG = (44, 62, 80)      # #2c3e50
    ROW_ALT = (241, 248, 245)     # fondo alterno
    BORDER_COLOR = (189, 195, 199)

    def __init__(self, title: str = "Informe", orientation="P", **kwargs):
        super().__init__(orientation=orientation, **kwargs)
        self.report_title = title
        self._register_fonts()
        self.set_auto_page_break(auto=True, margin=20)
        self.alias_nb_pages()

    # ── Fuentes ──────────────────────────────────
    def _register_fonts(self):
        fonts_dir = RESOURCES_DIR / "fonts"
        medium = fonts_dir / "Poppins-Medium.ttf"
        semi = fonts_dir / "Poppins-SemiBold.ttf"
        if medium.exists():
            self.add_font("Poppins", "", str(medium), uni=True)
        if semi.exists():
            self.add_font("Poppins", "B", str(semi), uni=True)
        # Fallback si las fuentes no existen
        self._has_poppins = medium.exists()

    def _font(self, style="", size=10):
        family = "Poppins" if self._has_poppins else "Helvetica"
        self.set_font(family, style, size)

    # ── Header ───────────────────────────────────
    def header(self):
        # Logo / imagen de fondo (si existe)
        logo = RESOURCES_DIR / "img" / "cesped.jpg"
        if logo.exists():
            self.image(str(logo), 10, 6, 20)

        self._font("B", 14)
        self.set_text_color(*self.TEXT_DARK)
        self.cell(25)  # margen para logo
        self.cell(0, 8, "Gestion de Torneo de Futbol", ln=True)

        self._font("", 9)
        self.set_text_color(100, 100, 100)
        self.cell(25)
        self.cell(0, 5, self.report_title, ln=True)

        # Línea decorativa
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.8)
        self.line(10, self.get_y() + 2, self.w - 10, self.get_y() + 2)
        self.ln(6)

    # ── Footer ───────────────────────────────────
    def footer(self):
        self.set_y(-15)
        self._font("", 7)
        self.set_text_color(140, 140, 140)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 10, f"Generado: {fecha}", align="L")
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="R", new_x="LMARGIN")

    # ── Helpers de tabla ─────────────────────────
    def section_title(self, text: str):
        self._font("B", 12)
        self.set_text_color(*self.ACCENT)
        self.cell(0, 9, text, ln=True)
        self.set_text_color(*self.TEXT_DARK)
        self.ln(2)

    def table_header(self, columns: list[tuple[str, int]]):
        """columns = [(label, width), ...]"""
        self._font("B", 8)
        self.set_fill_color(*self.HEADER_BG)
        self.set_text_color(*self.TEXT_LIGHT)
        self.set_draw_color(*self.BORDER_COLOR)
        for label, w in columns:
            self.cell(w, 8, label, border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(*self.TEXT_DARK)

    def table_row(self, values: list[str], widths: list[int], row_idx: int = 0):
        self._font("", 8)
        if row_idx % 2 == 1:
            self.set_fill_color(*self.ROW_ALT)
            fill = True
        else:
            self.set_fill_color(255, 255, 255)
            fill = True
        self.set_draw_color(*self.BORDER_COLOR)
        for val, w in zip(values, widths):
            self.cell(w, 7, str(val), border=1, fill=fill, align="C")
        self.ln()


# ──────────────────────────────────────────────
#  Servicio de generación de informes
# ──────────────────────────────────────────────
class ReportService:
    """Genera los 3 tipos de informes PDF del torneo."""

    # ═══════════════════════════════════════════
    #  INFORME 1: Equipos y Jugadores
    # ═══════════════════════════════════════════
    @staticmethod
    def generate_equipos_jugadores(
        output_path: Optional[str] = None,
        equipo_id: Optional[int] = None
    ) -> str:
        """
        Genera informe de equipos con sus jugadores y estadísticas.

        Args:
            output_path: Ruta de salida. Si None, genera en reports/generated/
            equipo_id: Filtro opcional por equipo

        Returns:
            Ruta del PDF generado
        """
        if not output_path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(REPORTS_GENERATED_DIR / f"equipos_jugadores_{ts}.pdf")

        pdf = TournamentPDF(title="Informe de Equipos y Jugadores")
        pdf.add_page()

        conn = get_connection()
        try:
            # Obtener equipos
            if equipo_id:
                equipos = conn.execute(
                    "SELECT id, nombre, curso, color FROM equipos WHERE id = ?",
                    (equipo_id,)
                ).fetchall()
            else:
                equipos = conn.execute(
                    "SELECT id, nombre, curso, color FROM equipos ORDER BY nombre"
                ).fetchall()

            if not equipos:
                pdf.section_title("No se encontraron equipos")
                pdf.output(output_path)
                return output_path

            cols = [
                ("Jugador", 50), ("Posicion", 28), ("Curso", 22),
                ("Goles", 18), ("Amarillas", 22), ("Rojas", 18)
            ]
            col_widths = [c[1] for c in cols]

            for eq in equipos:
                eq_id, eq_nombre, eq_curso, eq_color = eq

                # Verificar espacio para cabecera + al menos 2 filas
                if pdf.get_y() > pdf.h - 60:
                    pdf.add_page()

                pdf.section_title(f"{eq_nombre}")
                pdf._font("", 8)
                pdf.set_text_color(100, 100, 100)
                info_parts = []
                if eq_curso:
                    info_parts.append(f"Curso: {eq_curso}")
                if eq_color:
                    info_parts.append(f"Color: {eq_color}")
                if info_parts:
                    pdf.cell(0, 5, " | ".join(info_parts), ln=True)
                    pdf.ln(2)

                # Jugadores del equipo
                jugadores = conn.execute("""
                    SELECT p.nombre || ' ' || p.apellidos AS jugador,
                           p.posicion,
                           p.curso,
                           COALESCE(p.goles, 0) AS goles,
                           COALESCE(p.t_amarillas, 0) AS amarillas,
                           COALESCE(p.t_rojas, 0) AS rojas
                    FROM participantes p
                    WHERE p.equipo_id = ? AND p.tipo_jugador IN ('Jugador', 'Ambos')
                    ORDER BY p.apellidos, p.nombre
                """, (eq_id,)).fetchall()

                if jugadores:
                    pdf.table_header(cols)
                    total_goles = 0
                    total_amar = 0
                    total_rojas = 0
                    for idx, j in enumerate(jugadores):
                        nombre, pos, curso, goles, amar, rojas = j
                        pdf.table_row(
                            [nombre or "", pos or "-", curso or "-",
                             str(goles), str(amar), str(rojas)],
                            col_widths, idx
                        )
                        total_goles += goles
                        total_amar += amar
                        total_rojas += rojas

                    # Fila de totales
                    pdf._font("B", 8)
                    pdf.set_fill_color(*TournamentPDF.ACCENT)
                    pdf.set_text_color(*TournamentPDF.TEXT_LIGHT)
                    pdf.set_draw_color(*TournamentPDF.BORDER_COLOR)
                    pdf.cell(col_widths[0] + col_widths[1] + col_widths[2],
                             7, "TOTALES", border=1, fill=True, align="C")
                    pdf.cell(col_widths[3], 7, str(total_goles),
                             border=1, fill=True, align="C")
                    pdf.cell(col_widths[4], 7, str(total_amar),
                             border=1, fill=True, align="C")
                    pdf.cell(col_widths[5], 7, str(total_rojas),
                             border=1, fill=True, align="C")
                    pdf.ln()
                    pdf.set_text_color(*TournamentPDF.TEXT_DARK)
                else:
                    pdf._font("", 9)
                    pdf.set_text_color(150, 150, 150)
                    pdf.cell(0, 7, "Sin jugadores registrados", ln=True)
                    pdf.set_text_color(*TournamentPDF.TEXT_DARK)

                pdf.ln(6)

        finally:
            conn.close()

        pdf.output(output_path)
        return output_path

    # ═══════════════════════════════════════════
    #  INFORME 2: Partidos y Resultados
    # ═══════════════════════════════════════════
    @staticmethod
    def generate_partidos_resultados(
        output_path: Optional[str] = None,
        eliminatoria: Optional[str] = None
    ) -> str:
        """
        Genera informe de partidos y resultados.

        Args:
            output_path: Ruta de salida
            eliminatoria: Filtro opcional por fase

        Returns:
            Ruta del PDF generado
        """
        if not output_path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(REPORTS_GENERATED_DIR / f"partidos_resultados_{ts}.pdf")

        pdf = TournamentPDF(title="Informe de Partidos y Resultados", orientation="L")
        pdf.add_page()

        conn = get_connection()
        try:
            # Obtener fases disponibles
            if eliminatoria:
                fases = [eliminatoria]
            else:
                rows = conn.execute(
                    "SELECT DISTINCT eliminatoria FROM partidos ORDER BY "
                    "CASE eliminatoria "
                    "  WHEN 'octavos' THEN 1 WHEN 'cuartos' THEN 2 "
                    "  WHEN 'semifinal' THEN 3 WHEN 'final' THEN 4 "
                    "  ELSE 5 END"
                ).fetchall()
                fases = [r[0] for r in rows]

            if not fases:
                pdf.section_title("No se encontraron partidos")
                pdf.output(output_path)
                return output_path

            cols = [
                ("Slot", 14), ("Equipo Local", 52), ("Goles", 16),
                ("Goles", 16), ("Equipo Visitante", 52), ("Arbitro", 44),
                ("Fecha", 36), ("Penaltis", 20), ("Estado", 22)
            ]
            col_widths = [c[1] for c in cols]

            fase_labels = {
                "octavos": "Octavos de Final",
                "cuartos": "Cuartos de Final",
                "semifinal": "Semifinales",
                "final": "Final"
            }

            for fase in fases:
                if pdf.get_y() > pdf.h - 50:
                    pdf.add_page()

                label = fase_labels.get(fase, fase.capitalize())
                pdf.section_title(label)

                partidos = conn.execute("""
                    SELECT p.slot,
                           COALESCE(el.nombre, '(Por definir)') AS local,
                           COALESCE(p.goles_local, '-') AS gl,
                           COALESCE(p.goles_visitante, '-') AS gv,
                           COALESCE(ev.nombre, '(Por definir)') AS visitante,
                           COALESCE(ar.nombre || ' ' || ar.apellidos, '-') AS arbitro,
                           COALESCE(p.fecha_hora, '-') AS fecha,
                           p.penaltis_local,
                           p.penaltis_visitante,
                           p.estado
                    FROM partidos p
                    LEFT JOIN equipos el ON p.equipo_local_id = el.id
                    LEFT JOIN equipos ev ON p.equipo_visitante_id = ev.id
                    LEFT JOIN participantes ar ON p.arbitro_id = ar.id
                    WHERE p.eliminatoria = ?
                    ORDER BY p.slot
                """, (fase,)).fetchall()

                if partidos:
                    pdf.table_header(cols)
                    for idx, p in enumerate(partidos):
                        slot, local, gl, gv, visit, arb, fecha, pl, pv, estado = p
                        # Formato penaltis
                        pen = ""
                        if pl is not None and pv is not None:
                            pen = f"{pl}-{pv}"
                        # Formato fecha
                        if fecha and fecha != "-":
                            try:
                                dt = datetime.fromisoformat(fecha)
                                fecha = dt.strftime("%d/%m/%Y %H:%M")
                            except (ValueError, TypeError):
                                pass
                        # Color de estado
                        estado_str = estado or "Pendiente"
                        pdf.table_row(
                            [str(slot), local, str(gl), str(gv),
                             visit, arb, str(fecha), pen, estado_str],
                            col_widths, idx
                        )
                else:
                    pdf._font("", 9)
                    pdf.set_text_color(150, 150, 150)
                    pdf.cell(0, 7, "Sin partidos en esta fase", ln=True)
                    pdf.set_text_color(*TournamentPDF.TEXT_DARK)

                pdf.ln(6)

        finally:
            conn.close()

        pdf.output(output_path)
        return output_path

    # ═══════════════════════════════════════════
    #  INFORME 3: Clasificación y Eliminatorias
    # ═══════════════════════════════════════════
    @staticmethod
    def generate_clasificacion_eliminatorias(
        output_path: Optional[str] = None,
        eliminatoria: Optional[str] = None
    ) -> str:
        """
        Genera informe de clasificación con tabla de posiciones.

        Args:
            output_path: Ruta de salida
            eliminatoria: Filtro opcional por fase

        Returns:
            Ruta del PDF generado
        """
        if not output_path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(
                REPORTS_GENERATED_DIR / f"clasificacion_{ts}.pdf"
            )

        pdf = TournamentPDF(title="Informe de Clasificacion y Eliminatorias")
        pdf.add_page()

        conn = get_connection()
        try:
            # Construir tabla de posiciones acumulada
            where_clause = ""
            params: list = []
            if eliminatoria:
                where_clause = "WHERE p.eliminatoria = ?"
                params = [eliminatoria]

            # Consulta para estadísticas por equipo
            query = f"""
                SELECT e.id, e.nombre,
                    COUNT(CASE WHEN p.estado = 'Jugado' AND
                        (p.equipo_local_id = e.id OR p.equipo_visitante_id = e.id)
                        THEN 1 END) AS pj,
                    COUNT(CASE WHEN p.estado = 'Jugado' AND p.ganador_equipo_id = e.id
                        THEN 1 END) AS pg,
                    COUNT(CASE WHEN p.estado = 'Jugado' AND p.ganador_equipo_id IS NULL
                        AND (p.equipo_local_id = e.id OR p.equipo_visitante_id = e.id)
                        AND p.goles_local IS NOT NULL
                        THEN 1 END) AS pe,
                    COUNT(CASE WHEN p.estado = 'Jugado'
                        AND p.ganador_equipo_id IS NOT NULL
                        AND p.ganador_equipo_id != e.id
                        AND (p.equipo_local_id = e.id OR p.equipo_visitante_id = e.id)
                        THEN 1 END) AS pp,
                    COALESCE(SUM(CASE
                        WHEN p.estado = 'Jugado' AND p.equipo_local_id = e.id
                            THEN p.goles_local
                        WHEN p.estado = 'Jugado' AND p.equipo_visitante_id = e.id
                            THEN p.goles_visitante
                        ELSE 0 END), 0) AS gf,
                    COALESCE(SUM(CASE
                        WHEN p.estado = 'Jugado' AND p.equipo_local_id = e.id
                            THEN p.goles_visitante
                        WHEN p.estado = 'Jugado' AND p.equipo_visitante_id = e.id
                            THEN p.goles_local
                        ELSE 0 END), 0) AS gc
                FROM equipos e
                LEFT JOIN partidos p ON (p.equipo_local_id = e.id
                    OR p.equipo_visitante_id = e.id)
                    {where_clause.replace('WHERE', 'AND') if where_clause else ''}
                GROUP BY e.id, e.nombre
                HAVING pj > 0
                ORDER BY (pg * 3 + pe) DESC, (gf - gc) DESC, gf DESC
            """
            equipos_stats = conn.execute(query, params).fetchall()

            if not equipos_stats:
                pdf.section_title("No hay datos de clasificacion disponibles")
                pdf.output(output_path)
                return output_path

            # Tabla de posiciones
            fase_label = ""
            if eliminatoria:
                fase_labels = {
                    "octavos": "Octavos de Final",
                    "cuartos": "Cuartos de Final",
                    "semifinal": "Semifinales",
                    "final": "Final"
                }
                fase_label = f" - {fase_labels.get(eliminatoria, eliminatoria.capitalize())}"

            pdf.section_title(f"Tabla de Posiciones{fase_label}")

            cols = [
                ("Pos", 12), ("Equipo", 48), ("PJ", 14), ("PG", 14),
                ("PE", 14), ("PP", 14), ("GF", 14), ("GC", 14),
                ("Dif", 16), ("Pts", 16)
            ]
            col_widths = [c[1] for c in cols]

            pdf.table_header(cols)
            for idx, row in enumerate(equipos_stats):
                eq_id, nombre, pj, pg, pe, pp, gf, gc = row
                dif = gf - gc
                pts = pg * 3 + pe
                dif_str = f"+{dif}" if dif > 0 else str(dif)
                pdf.table_row(
                    [str(idx + 1), nombre, str(pj), str(pg), str(pe),
                     str(pp), str(gf), str(gc), dif_str, str(pts)],
                    col_widths, idx
                )

            pdf.ln(8)

            # Estadísticas destacadas
            if pdf.get_y() > pdf.h - 60:
                pdf.add_page()

            pdf.section_title("Estadisticas Destacadas")

            # Máximo goleador (equipo)
            if equipos_stats:
                max_gf = max(equipos_stats, key=lambda x: x[6])
                pdf._font("", 9)
                pdf.cell(0, 6, f"Equipo mas goleador: {max_gf[1]} ({max_gf[6]} goles)", ln=True)

                min_gc = min(equipos_stats, key=lambda x: x[7])
                pdf.cell(0, 6, f"Mejor defensa: {min_gc[1]} ({min_gc[7]} goles recibidos)", ln=True)

                max_wins = max(equipos_stats, key=lambda x: x[3])
                pdf.cell(0, 6, f"Mas victorias: {max_wins[1]} ({max_wins[3]} victorias)", ln=True)

            pdf.ln(4)

            # Goleadores individuales
            goleadores_query = """
                SELECT p.nombre || ' ' || p.apellidos AS jugador,
                       e.nombre AS equipo,
                       COALESCE(p.goles, 0) AS goles
                FROM participantes p
                LEFT JOIN equipos e ON p.equipo_id = e.id
                WHERE p.goles > 0
                ORDER BY p.goles DESC
                LIMIT 10
            """
            goleadores = conn.execute(goleadores_query).fetchall()

            if goleadores:
                if pdf.get_y() > pdf.h - 50:
                    pdf.add_page()

                pdf.section_title("Top 10 Goleadores")
                gol_cols = [("Pos", 12), ("Jugador", 60), ("Equipo", 50), ("Goles", 20)]
                gol_widths = [c[1] for c in gol_cols]
                pdf.table_header(gol_cols)
                for idx, g in enumerate(goleadores):
                    jugador, equipo, goles = g
                    pdf.table_row(
                        [str(idx + 1), jugador, equipo or "-", str(goles)],
                        gol_widths, idx
                    )

            # Tarjetas
            tarjetas_query = """
                SELECT p.nombre || ' ' || p.apellidos AS jugador,
                       e.nombre AS equipo,
                       COALESCE(p.t_amarillas, 0) AS amarillas,
                       COALESCE(p.t_rojas, 0) AS rojas
                FROM participantes p
                LEFT JOIN equipos e ON p.equipo_id = e.id
                WHERE p.t_amarillas > 0 OR p.t_rojas > 0
                ORDER BY p.t_rojas DESC, p.t_amarillas DESC
                LIMIT 10
            """
            tarjetas = conn.execute(tarjetas_query).fetchall()

            if tarjetas:
                if pdf.get_y() > pdf.h - 50:
                    pdf.add_page()

                pdf.section_title("Tarjetas Disciplinarias (Top 10)")
                tar_cols = [
                    ("Pos", 12), ("Jugador", 60), ("Equipo", 50),
                    ("Amarillas", 24), ("Rojas", 20)
                ]
                tar_widths = [c[1] for c in tar_cols]
                pdf.table_header(tar_cols)
                for idx, t in enumerate(tarjetas):
                    jugador, equipo, amar, rojas = t
                    pdf.table_row(
                        [str(idx + 1), jugador, equipo or "-",
                         str(amar), str(rojas)],
                        tar_widths, idx
                    )

        finally:
            conn.close()

        pdf.output(output_path)
        return output_path
