#!/usr/bin/env python3
"""Script para agregar traducciones de labels de filtrado y paneles de detalle"""

import xml.etree.ElementTree as ET
from pathlib import Path

def agregar_mensaje(context_elem, source_text, translation_text):
    """Agrega un mensaje de traducción al contexto si no existe."""
    # Verificar si ya existe
    for msg in context_elem.findall('message'):
        source = msg.find('source')
        if source is not None and source.text == source_text:
            # Ya existe, actualizar si está vacía
            trans = msg.find('translation')
            if trans is not None:
                if not trans.text or trans.get('type') == 'unfinished':
                    trans.text = translation_text
                    if 'type' in trans.attrib:
                        del trans.attrib['type']
            return
    
    # Crear nuevo mensaje
    message = ET.SubElement(context_elem, 'message')
    source = ET.SubElement(message, 'source')
    source.text = source_text
    translation = ET.SubElement(message, 'translation')
    translation.text = translation_text

# Traducciones por contexto
traducciones = {
    'PageGestionParticipantes': [
        # Labels de filtros
        ("Rol:", "Role:"),
        ("Equipo:", "Team:"),
        ("Curso:", "Grade:"),
        
        # Panel de detalle
        ("Detalle del participante", "Participant Details"),
        ("Datos", "Data"),
        ("Estadísticas", "Statistics"),
        ("Asignaciones", "Assignments"),
        
        # Tab Datos
        ("Nombre completo:", "Full name:"),
        ("Nombre y apellidos del participante", "Participant's full name"),
        ("Fecha de nacimiento:", "Birth date:"),
        ("Roles:", "Roles:"),
        ("Es jugador", "Is player"),
        ("Es árbitro", "Is referee"),
        ("Equipo asignado:", "Assigned team:"),
        ("Sin equipo", "No team"),
        ("Posición:", "Position:"),
        ("Sin definir", "Undefined"),
        ("Portero", "Goalkeeper"),
        ("Defensa", "Defender"),
        ("Centrocampista", "Midfielder"),
        ("Delantero", "Forward"),
        
        # Tab Estadísticas
        ("Goles:", "Goals:"),
        ("Tarjetas amarillas:", "Yellow cards:"),
        ("Tarjetas rojas:", "Red cards:"),
        
        # Tab Asignaciones
        ("Equipo", "Team"),
        ("Equipo actual: Sin equipo", "Current team: No team"),
        ("Seleccionar equipo:", "Select team:"),
        ("-- Selecciona equipo --", "-- Select team --"),
        ("Guardar asignación", "Save assignment"),
        ("Quitar equipo", "Remove team"),
        ("Partidos arbitrados", "Refereed matches"),
        ("Ronda", "Round"),
        ("Fecha", "Date"),
        ("Local", "Home"),
        ("Visitante", "Away"),
        ("La asignación de árbitros se gestiona desde la sección Partidos.", 
         "Referee assignment is managed from the Matches section."),
    ],
    'PageCalendarioPartidos': [
        # Labels de filtros
        ("Ronda:", "Round:"),
        ("Estado:", "State:"),
        
        # Panel de detalle
        ("Match Details", "Match Details"),
        ("Datos", "Data"),
        ("Convocatoria", "Squad"),
        ("Resultado", "Result"),
        
        # Tab Datos
        ("Seleccione un partido", "Select a match"),
        ("Equipo Local:", "Home Team:"),
        ("-- Seleccionar --", "-- Select --"),
        ("Equipo Visitante:", "Away Team:"),
        ("Fase:", "Phase:"),
        ("Octavos", "Round of 16"),
        ("Estado:", "State:"),
        ("Programado", "Scheduled"),
        ("Jugado", "Played"),
        ("Fecha y hora:", "Date and time:"),
        ("Árbitro:", "Referee:"),
        ("Sin árbitro", "No referee"),
    ]
}

# Ruta al archivo .ts
ts_path = Path(__file__).parent / "translations" / "torneo_en.ts"

# Parsear archivo
tree = ET.parse(ts_path)
root = tree.getroot()

total = 0

# Procesar cada contexto
for context_name, mensajes in traducciones.items():
    # Buscar o crear contexto
    context = None
    for ctx in root.findall('context'):
        name_elem = ctx.find('name')
        if name_elem is not None and name_elem.text == context_name:
            context = ctx
            break
    
    if context is None:
        print(f"[WARN] Contexto no encontrado: {context_name}")
        continue
    
    # Agregar mensajes
    for source_text, translation_text in mensajes:
        agregar_mensaje(context, source_text, translation_text)
    
    total += len(mensajes)
    print(f"+ {len(mensajes)} traducciones en {context_name}")

# Guardar con formato
ET.indent(tree, space='    ')
tree.write(ts_path, encoding='utf-8', xml_declaration=True)

print(f"\n[OK] {total} traducciones agregadas/actualizadas")
print(f"Archivo: {ts_path}")
