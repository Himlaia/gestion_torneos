import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path


NOMBRES = [
    "Alejandro", "Carlos", "David", "Daniel", "Diego", "Fernando", "Francisco",
    "Javier", "Jorge", "José", "Juan", "Luis", "Manuel", "Miguel", "Pablo",
    "Pedro", "Rafael", "Raúl", "Roberto", "Sergio", "Adrián", "Alberto",
    "Antonio", "Ángel", "Eduardo", "Enrique", "Gonzalo", "Héctor", "Hugo",
    "Ignacio", "Iván", "Jaime", "Jesús", "Joaquín", "Marcos", "Mario",
    "Mateo", "Nicolás", "Óscar", "Ricardo", "Rubén", "Salvador", "Samuel",
    "Santiago", "Tomás", "Víctor", "Ana", "Andrea", "Beatriz", "Carmen",
    "Carolina", "Clara", "Cristina", "Elena", "Emma", "Eva", "Isabel",
    "Julia", "Laura", "Lucía", "María", "Marta", "Natalia", "Paula",
    "Raquel", "Rosa", "Sandra", "Sara", "Sofía", "Teresa", "Valentina"
]

APELLIDOS = [
    "García", "Rodríguez", "González", "Fernández", "López", "Martínez",
    "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández",
    "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
    "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez",
    "Serrano", "Blanco", "Suárez", "Molina", "Morales", "Ortega", "Delgado",
    "Castro", "Ortiz", "Rubio", "Marín", "Sanz", "Núñez", "Iglesias",
    "Medina", "Garrido", "Santos", "Castillo", "Cortés", "Guerrero",
    "Lozano", "Cano", "Méndez", "Cruz", "Prieto", "Flores", "Herrera",
    "Peña", "León", "Márquez", "Cabrera", "Gallego", "Calvo"
]

CURSOS = ["1º ESO", "2º ESO", "3º ESO", "4º ESO"]

POSICIONES = ["Portero", "Defensa", "Centrocampista", "Delantero"]

TIPOS_JUGADOR = ["Jugador", "Árbitro", "Ambos"]


def get_db_path():
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    db_path = project_root / "data" / "torneo.db"
    return db_path


def obtener_fecha_nacimiento(curso):
    current_year = datetime.now().year
    
    if curso == "1º ESO":
        birth_year = current_year - 12
    elif curso == "2º ESO":
        birth_year = current_year - 13
    elif curso == "3º ESO":
        birth_year = current_year - 14
    else:
        birth_year = current_year - 15
    
    mes = random.randint(1, 12)
    
    if mes == 2:
        dia = random.randint(1, 28)
    elif mes in [4, 6, 9, 11]:
        dia = random.randint(1, 30)
    else:
        dia = random.randint(1, 31)
    
    return f"{dia:02d}/{mes:02d}/{birth_year}"


def generar_posicion():
    rand = random.random()
    
    if rand < 0.10:
        return "Portero"
    elif rand < 0.45:
        return "Defensa"
    elif rand < 0.80:
        return "Centrocampista"
    else:
        return "Delantero"


def generar_tipo_jugador():
    rand = random.random()
    
    if rand < 0.80:
        return "Jugador"
    elif rand < 0.95:
        return "Ambos"
    else:
        return "Árbitro"


def participante_existe(cursor, nombre, apellidos):
    cursor.execute(
        "SELECT COUNT(*) FROM participantes WHERE nombre = ? AND apellidos = ?",
        (nombre, apellidos)
    )
    return cursor.fetchone()[0] > 0


def crear_participantes_para_equipo(cursor, equipo_id, equipo_nombre, nombres_usados):
    num_participantes = random.randint(10, 14)
    participantes_creados = 0
    
    print(f"\n  Generando {num_participantes} participantes para '{equipo_nombre}'...")
    
    for _ in range(num_participantes):
        intentos = 0
        while intentos < 50:
            nombre = random.choice(NOMBRES)
            apellidos = random.choice(APELLIDOS)
            nombre_completo = f"{nombre} {apellidos}"
            
            if nombre_completo not in nombres_usados and not participante_existe(cursor, nombre, apellidos):
                nombres_usados.add(nombre_completo)
                break
            
            intentos += 1
        else:
            apellidos = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
            nombre_completo = f"{nombre} {apellidos}"
            nombres_usados.add(nombre_completo)
        
        curso = random.choice(CURSOS)
        fecha_nacimiento = obtener_fecha_nacimiento(curso)
        tipo_jugador = generar_tipo_jugador()
        posicion = generar_posicion()
        
        if tipo_jugador == "Árbitro":
            equipo_asignado = None
            posicion = "Sin definir"
        else:
            equipo_asignado = equipo_id
        
        cursor.execute("""
            INSERT INTO participantes (
                nombre, apellidos, fecha_nacimiento, curso, tipo_jugador,
                posicion, equipo_id, goles, t_amarillas, t_rojas
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
        """, (nombre, apellidos, fecha_nacimiento, curso, tipo_jugador, posicion, equipo_asignado))
        
        participantes_creados += 1
    
    return participantes_creados


def crear_arbitros_adicionales(cursor, nombres_usados, num_arbitros=5):
    print(f"\n  Generando {num_arbitros} árbitros adicionales sin equipo...")
    
    arbitros_creados = 0
    
    for _ in range(num_arbitros):
        intentos = 0
        while intentos < 50:
            nombre = random.choice(NOMBRES)
            apellidos = random.choice(APELLIDOS)
            nombre_completo = f"{nombre} {apellidos}"
            
            if nombre_completo not in nombres_usados and not participante_existe(cursor, nombre, apellidos):
                nombres_usados.add(nombre_completo)
                break
            
            intentos += 1
        else:
            apellidos = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
            nombre_completo = f"{nombre} {apellidos}"
            nombres_usados.add(nombre_completo)
        
        curso = random.choice(CURSOS)
        fecha_nacimiento = obtener_fecha_nacimiento(curso)
        
        cursor.execute("""
            INSERT INTO participantes (
                nombre, apellidos, fecha_nacimiento, curso, tipo_jugador,
                posicion, equipo_id, goles, t_amarillas, t_rojas
            )
            VALUES (?, ?, ?, ?, 'Árbitro', 'Sin definir', NULL, 0, 0, 0)
        """, (nombre, apellidos, fecha_nacimiento, curso))
        
        arbitros_creados += 1
    
    return arbitros_creados


def main():
    random.seed(42)
    
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"❌ Error: No se encontró la base de datos en {db_path}")
        return
    
    db_path_absoluta = db_path.resolve()
    print(f"📁 Ruta absoluta de la BD: {db_path_absoluta}")
    print(f"📁 Conectando a la base de datos...")
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, nombre FROM equipos ORDER BY nombre")
        equipos = cursor.fetchall()
        
        if not equipos:
            print("⚠️  No hay equipos en la base de datos. Crea equipos primero.")
            return
        
        print(f"✓ Encontrados {len(equipos)} equipos")
        
        nombres_usados = set()
        
        cursor.execute("SELECT nombre, apellidos FROM participantes")
        for nombre, apellidos in cursor.fetchall():
            nombres_usados.add(f"{nombre} {apellidos}")
        
        total_participantes = 0
        
        for equipo_id, equipo_nombre in equipos:
            num_creados = crear_participantes_para_equipo(
                cursor, equipo_id, equipo_nombre, nombres_usados
            )
            total_participantes += num_creados
        
        arbitros_creados = crear_arbitros_adicionales(cursor, nombres_usados, 5)
        total_participantes += arbitros_creados
        
        conn.commit()
        
        print(f"\n✓ Proceso completado exitosamente")
        print(f"  - Total de participantes creados: {total_participantes}")
        print(f"  - Árbitros sin equipo: {arbitros_creados}")
        
        cursor.execute("SELECT COUNT(*) FROM participantes")
        total_participantes_bd = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM equipos")
        total_equipos_bd = cursor.fetchone()[0]
        
        print(f"\n📊 Estado actual de la base de datos:")
        print(f"  - Total equipos en BD: {total_equipos_bd}")
        print(f"  - Total participantes en BD: {total_participantes_bd}")
        
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\n🔒 Conexión cerrada")


if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT DE RELLENADO DE PARTICIPANTES")
    print("=" * 60)
    
    main()
