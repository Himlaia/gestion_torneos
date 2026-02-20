#!/usr/bin/env python3
"""Script para agregar traducciones al archivo torneo_en.ts"""

def agregar_traducciones():
    """Agrega contextos y traducciones al archivo torneo_en.ts"""
    
    # Leer archivo actual
    with open('translations/torneo_en.ts', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Nuevos contextos a agregar (antes del cierre de </TS>)
    nuevos_contextos = '''
<context>
    <name>MainWindowCode</name>
    <message>
        <source>Torneo</source>
        <translation>Tournament</translation>
    </message>
    <message>
        <source>Inicio</source>
        <translation>Home</translation>
    </message>
    <message>
        <source>Gestión de equipos</source>
        <translation>Teams Management</translation>
    </message>
    <message>
        <source>Gestión de participantes</source>
        <translation>Participants Management</translation>
    </message>
    <message>
        <source>Calendario / Partidos</source>
        <translation>Schedule / Matches</translation>
    </message>
    <message>
        <source>Cuadro de eliminatorias</source>
        <translation>Knockout Bracket</translation>
    </message>
    <message>
        <source>Herramientas</source>
        <translation>Tools</translation>
    </message>
    <message>
        <source>Reloj digital</source>
        <translation>Digital Clock</translation>
    </message>
    <message>
        <source>Ver</source>
        <translation>View</translation>
    </message>
    <message>
        <source>Cambiar tema</source>
        <translation>Change Theme</translation>
    </message>
    <message>
        <source>Idioma</source>
        <translation>Language</translation>
    </message>
    <message>
        <source>Español</source>
        <translation>Spanish</translation>
    </message>
    <message>
        <source>English</source>
        <translation>English</translation>
    </message>
    <message>
        <source>Ayuda</source>
        <translation>Help</translation>
    </message>
    <message>
        <source>Créditos</source>
        <translation>Credits</translation>
    </message>
</context>
<context>
    <name>PageInicio</name>
    <message>
        <source>Gestión de torneos</source>
        <translation>Tournament Management</translation>
    </message>
    <message>
        <source>Equipos</source>
        <translation>Teams</translation>
    </message>
    <message>
        <source>Gestiona los equipos del torneo</source>
        <translation>Manage tournament teams</translation>
    </message>
    <message>
        <source>Participantes</source>
        <translation>Participants</translation>
    </message>
    <message>
        <source>Administra jugadores y árbitros</source>
        <translation>Manage players and referees</translation>
    </message>
    <message>
        <source>Programa y gestiona los partidos</source>
        <translation>Schedule and manage matches</translation>
    </message>
    <message>
        <source>Visualiza el cuadro del torneo</source>
        <translation>View tournament bracket</translation>
    </message>
    <message>
        <source>Consulta la documentación</source>
        <translation>Consult documentation</translation>
    </message>
    <message>
        <source>Información del proyecto</source>
        <translation>Project information</translation>
    </message>
</context>
'''
    
    # Reemplazar el cierre </TS> con los nuevos contextos y el cierre
    contenido = contenido.replace('</TS>', nuevos_contextos + '</TS>')
    
    # Guardar archivo
    with open('translations/torneo_en.ts', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✓ Traducciones agregadas a torneo_en.ts")

if __name__ == "__main__":
    agregar_traducciones()
