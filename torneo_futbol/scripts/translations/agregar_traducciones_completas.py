#!/usr/bin/env python3
"""Script para agregar traducciones completas de todas las páginas al archivo .ts"""

import xml.etree.ElementTree as ET
from pathlib import Path

def agregar_mensaje(context_elem, source_text, translation_text, comment=""):
    """Agrega un mensaje de traducción al contexto."""
    # Verificar si ya existe
    for msg in context_elem.findall('message'):
        source = msg.find('source')
        if source is not None and source.text == source_text:
            # Actualizar traducción existente
            trans = msg.find('translation')
            if trans is not None:
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
    if comment:
        comment_elem = ET.SubElement(message, 'comment')
        comment_elem.text = comment

# Traducciones por contexto
traducciones = {
    'PageGestionEquipos': [
        ("Buscar equipo…", "Search team…"),
        ("Nuevo equipo", "New Team"),
        ("Editar equipo", "Edit Team"),
        ("Eliminar equipo", "Delete Team"),
        ("Nombre", "Name"),
        ("Colores", "Colors"),
        ("Escudo", "Badge"),
        ("Nº jugadores", "No. Players"),
        ("Detalle del equipo", "Team Details"),
        ("Nombre:", "Name:"),
        ("Nombre del equipo", "Team name"),
        ("Colores:", "Colors:"),
        ("Ej: Rojo y blanco", "E.g: Red and white"),
        ("Escudo:", "Badge:"),
        ("Sin escudo", "No badge"),
        ("Seleccionar escudo", "Select Badge"),
        ("Guardar equipo", "Save Team"),
        ("Cancelar", "Cancel"),
    ],
    'PageGestionParticipantes': [
        ("Buscar por nombre…", "Search by name…"),
        ("Nuevo", "New"),
        ("Nuevo participante", "New participant"),
        ("Editar", "Edit"),
        ("Editar participante seleccionado", "Edit selected participant"),
        ("Eliminar", "Delete"),
        ("Eliminar participante seleccionado", "Delete selected participant"),
        ("Todos", "All"),
        ("Jugadores", "Players"),
        ("Árbitros", "Referees"),
        ("Ambos", "Both"),
        ("Nombre", "Name"),
        ("F. Nac.", "Birth Date"),
        ("Curso", "Grade"),
        ("Rol(es)", "Role(s)"),
        ("Equipo", "Team"),
        ("Guardar", "Save"),
        ("Cancelar", "Cancel"),
    ],
    'PageCalendarioPartidos': [
        ("Todos", "All"),
        ("Octavos", "Round of 16"),
        ("Cuartos", "Quarterfinals"),
        ("Semifinales", "Semifinals"),
        ("Final", "Final"),
        ("Pendientes", "Pending"),
        ("Jugados", "Played"),
        ("Nuevo partido", "New Match"),
        ("Reiniciar torneo", "Reset Tournament"),
        ("Calendario mensual", "Monthly Calendar"),
        ("💡 Haga clic en un día con partidos para ver detalles", "💡 Click on a day with matches to see details"),
        ("Detalle del partido", "Match Details"),
        ("Seleccione un partido", "Select a match"),
        ("Guardar", "Save"),
        ("Eliminar", "Delete"),
        ("Cancelar", "Cancel"),
    ]
}

# Ruta al archivo .ts
ts_path = Path(__file__).parent / "translations" / "torneo_en.ts"

# Parsear archivo
tree = ET.parse(ts_path)
root = tree.getroot()

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
        context = ET.SubElement(root, 'context')
        name_elem = ET.SubElement(context, 'name')
        name_elem.text = context_name
        print(f"✓ Contexto creado: {context_name}")
    
    # Agregar mensajes
    for source_text, translation_text in mensajes:
        agregar_mensaje(context, source_text, translation_text)
    
    print(f"✓ {len(mensajes)} traducciones agregadas/actualizadas en {context_name}")

# Guardar con formato
ET.indent(tree, space='    ')
tree.write(ts_path, encoding='utf-8', xml_declaration=True)

print(f"\n✅ Archivo actualizado: {ts_path}")
print("Ejecuta lrelease para compilar las traducciones.")
