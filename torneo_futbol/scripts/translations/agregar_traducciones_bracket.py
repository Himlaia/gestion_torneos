#!/usr/bin/env python3
"""Script para agregar traducciones de bracket y labels de formularios."""
import xml.etree.ElementTree as ET

# Cargar archivo
tree = ET.parse('translations/torneo_en.ts')
root = tree.getroot()

# Buscar contexto PageGestionParticipantes
context_participantes = None
for context in root.findall('context'):
    name_elem = context.find('name')
    if name_elem is not None and name_elem.text == 'PageGestionParticipantes':
        context_participantes = context
        break

# Buscar contexto PageCalendarioPartidos
context_partidos = None
for context in root.findall('context'):
    name_elem = context.find('name')
    if name_elem is not None and name_elem.text == 'PageCalendarioPartidos':
        context_partidos = context
        break

# Buscar o crear contexto PageCuadroEliminatorias
context_bracket = None
for context in root.findall('context'):
    name_elem = context.find('name')
    if name_elem is not None and name_elem.text == 'PageCuadroEliminatorias':
        context_bracket = context
        break

if not context_bracket:
    context_bracket = ET.SubElement(root, 'context')
    ET.SubElement(context_bracket, 'name').text = 'PageCuadroEliminatorias'

# Buscar o crear contexto BracketWidget
context_bracket_widget = None
for context in root.findall('context'):
    name_elem = context.find('name')
    if name_elem is not None and name_elem.text == 'BracketWidget':
        context_bracket_widget = context
        break

if not context_bracket_widget:
    context_bracket_widget = ET.SubElement(root, 'context')
    ET.SubElement(context_bracket_widget, 'name').text = 'BracketWidget'

# Función para verificar si ya existe una traducción
def traduccion_existe(context, source_text):
    for message in context.findall('message'):
        source = message.find('source')
        if source is not None and source.text == source_text:
            return True
    return False

# Función para agregar traducción
def agregar_traduccion(context, source_text, translation_text):
    if not traduccion_existe(context, source_text):
        message = ET.SubElement(context, 'message')
        ET.SubElement(message, 'source').text = source_text
        ET.SubElement(message, 'translation').text = translation_text
        return True
    return False

# Traducciones para PageGestionParticipantes (labels de formulario)
traducciones_participantes = [
    ("Rol:", "Role:"),
    ("Equipo:", "Team:"),
    ("Curso:", "Grade:"),
    ("Nombre completo:", "Full name:"),
    ("Fecha de nacimiento:", "Birth date:"),
    ("Roles:", "Roles:"),
    ("Es jugador", "Is player"),
    ("Es árbitro", "Is referee"),
    ("Equipo asignado:", "Assigned team:"),
    ("Posición:", "Position:"),
]

# Traducciones para PageCalendarioPartidos (labels de filtros)
traducciones_partidos = [
    ("Ronda:", "Round:"),
    ("Estado:", "Status:"),
]

# Traducciones para PageCuadroEliminatorias
traducciones_bracket = [
    ("Cuadro de eliminatorias", "Knockout Bracket"),
    ("Randomizar octavos", "Randomize Round of 16"),
    ("Guardar emparejamientos", "Save Pairings"),
    ("Exportar resultados (CSV)", "Export Results (CSV)"),
]

# Traducciones para BracketWidget (nombres de rondas)
traducciones_bracket_widget = [
    ("Octavos", "Round of 16"),
    ("Cuartos", "Quarterfinals"),
    ("Semifinal", "Semifinal"),
    ("Finalista", "Finalist"),
]

# Agregar traducciones
count_participantes = 0
count_partidos = 0
count_bracket = 0
count_bracket_widget = 0

if context_participantes:
    for source, translation in traducciones_participantes:
        if agregar_traduccion(context_participantes, source, translation):
            count_participantes += 1

if context_partidos:
    for source, translation in traducciones_partidos:
        if agregar_traduccion(context_partidos, source, translation):
            count_partidos += 1

for source, translation in traducciones_bracket:
    if agregar_traduccion(context_bracket, source, translation):
        count_bracket += 1

for source, translation in traducciones_bracket_widget:
    if agregar_traduccion(context_bracket_widget, source, translation):
        count_bracket_widget += 1

# Guardar archivo
tree.write('translations/torneo_en.ts', encoding='utf-8', xml_declaration=True)

# Mostrar resumen
print(f"+ {count_participantes} en PageGestionParticipantes")
print(f"+ {count_partidos} en PageCalendarioPartidos")
print(f"+ {count_bracket} en PageCuadroEliminatorias")
print(f"+ {count_bracket_widget} en BracketWidget")
print(f"\n[OK] {count_participantes + count_partidos + count_bracket + count_bracket_widget} traducciones agregadas")
