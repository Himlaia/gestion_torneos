#!/usr/bin/env python3#!/usr/bin/env python3
































































print(f"\n[OK] Traducciones del contenido interno agregadas")print(f"+ {count} traducciones agregadas a PageGestionParticipantes")# Mostrar resumentree.write('translations/torneo_en.ts', encoding='utf-8', xml_declaration=True)# Guardar archivo            count += 1        if agregar_traduccion(context_participantes, source, translation):    for source, translation in traducciones_contenido:if context_participantes:count = 0# Agregar traducciones]     "Referee assignments are managed from the Matches section."),    ("La asignación de árbitros se gestiona desde la sección Partidos.",     ("Partidos arbitrados", "Refereed matches"),  # Group box title    ("Seleccionar equipo:", "Select team:"),    ("Equipo actual: Sin equipo", "Current team: No team"),    ("Equipo actual:", "Current team:"),    ("Equipo", "Team"),  # Group box title    # Tab Asignaciones        ("Tarjetas rojas:", "Red cards:"),    ("Tarjetas amarillas:", "Yellow cards:"),    ("Goles:", "Goals:"),    # Tab Estadísticastraducciones_contenido = [# Traducciones para el contenido interno de los tabs    return False        return True        ET.SubElement(message, 'translation').text = translation_text        ET.SubElement(message, 'source').text = source_text        message = ET.SubElement(context, 'message')    if not traduccion_existe(context, source_text):def agregar_traduccion(context, source_text, translation_text):# Función para agregar traducción    return False            return True        if source is not None and source.text == source_text:        source = message.find('source')    for message in context.findall('message'):def traduccion_existe(context, source_text):# Función para verificar si ya existe una traducción        break        context_participantes = context    if name_elem is not None and name_elem.text == 'PageGestionParticipantes':    name_elem = context.find('name')for context in root.findall('context'):context_participantes = None# Buscar contexto PageGestionParticipantesroot = tree.getroot()tree = ET.parse('translations/torneo_en.ts')# Cargar archivoimport xml.etree.ElementTree as ET"""Script para agregar traducciones de contenido interno de tabs.""""""Script para agregar traducciones de contenido interno de tabs."""
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

# Traducciones para el contenido interno de los tabs
traducciones_contenido = [
    # Tab Estadísticas
    ("Goles:", "Goals:"),
    ("Tarjetas amarillas:", "Yellow cards:"),
    ("Tarjetas rojas:", "Red cards:"),
    
    # Tab Asignaciones
    ("Equipo", "Team"),  # Group box title
    ("Equipo actual:", "Current team:"),
    ("Equipo actual: Sin equipo", "Current team: No team"),
    ("Seleccionar equipo:", "Select team:"),
    ("Partidos arbitrados", "Refereed matches"),  # Group box title
    ("La asignación de árbitros se gestiona desde la sección Partidos.", 
     "Referee assignments are managed from the Matches section."),
]

# Agregar traducciones
count = 0

if context_participantes:
    for source, translation in traducciones_contenido:
        if agregar_traduccion(context_participantes, source, translation):
            count += 1

# Guardar archivo
tree.write('translations/torneo_en.ts', encoding='utf-8', xml_declaration=True)

# Mostrar resumen
print(f"+ {count} traducciones agregadas a PageGestionParticipantes")
print(f"\n[OK] Traducciones del contenido interno agregadas")
