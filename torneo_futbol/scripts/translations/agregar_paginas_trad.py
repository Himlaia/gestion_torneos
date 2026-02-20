#!/usr/bin/env python3
"""Script para agregar traducciones de las páginas al archivo torneo_en.ts"""

def agregar_traducciones_paginas():
    """Agrega contextos de páginas al archivo torneo_en.ts"""
    
    # Leer archivo actual
    with open('translations/torneo_en.ts', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Nuevos contextos a agregar (antes del cierre de </TS>)
    nuevos_contextos = '''<context>
    <name>PageGestionEquipos</name>
    <message>
        <source>Gestión de equipos</source>
        <translation>Teams Management</translation>
    </message>
</context>
<context>
    <name>PageGestionParticipantes</name>
    <message>
        <source>Gestión de participantes</source>
        <translation>Participants Management</translation>
    </message>
</context>
<context>
    <name>PageCalendarioPartidos</name>
    <message>
        <source>Calendario / Partidos</source>
        <translation>Schedule / Matches</translation>
    </message>
</context>
'''
    
    # Reemplazar el cierre </TS> con los nuevos contextos y el cierre
    contenido = contenido.replace('</TS>', nuevos_contextos + '</TS>')
    
    # Guardar archivo
    with open('translations/torneo_en.ts', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✓ Traducciones de páginas agregadas a torneo_en.ts")

if __name__ == "__main__":
    agregar_traducciones_paginas()
