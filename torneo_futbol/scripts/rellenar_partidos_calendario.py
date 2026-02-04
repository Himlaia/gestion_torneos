import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)


def get_db_path():
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "torneo.db"


DB_PATH = get_db_path()


ELIMINATORIAS = ["octavos", "cuartos", "semifinal", "final", "fase_grupos", "amistoso"]
HORARIOS = ["16:00", "18:00", "20:00"]
ESTADOS_POSIBLES = ["Pendiente", "Jugado"]


def conectar_bd():
    db_abs = DB_PATH.resolve()
    print(f"[SCRIPT-DB] Ruta absoluta BD: {db_abs}")
    conn = sqlite3.connect(db_abs)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def obtener_columnas_tabla(conn, tabla):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [row[1] for row in cursor.fetchall()]
    return columnas


def cargar_equipos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM equipos")
    equipos = cursor.fetchall()
    if not equipos:
        print("[WARN] No hay equipos en la tabla equipos. No se pueden generar partidos.")
    return equipos


def cargar_arbitros(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, apellidos FROM participantes
        WHERE tipo_jugador IN ('Árbitro', 'Ambos')
    """)
    arbitros = cursor.fetchall()
    return arbitros


def existe_partido(conn, fecha_hora, local_id, visitante_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM partidos
        WHERE fecha_hora = ?
          AND ((equipo_local_id = ? AND equipo_visitante_id = ?)
               OR (equipo_local_id = ? AND equipo_visitante_id = ?))
    """, (fecha_hora, local_id, visitante_id, visitante_id, local_id))
    count = cursor.fetchone()[0]
    return count > 0


def generar_partidos_mes(conn, equipos, arbitros, columnas_partidos, ano, mes, num_partidos=15):
    if not equipos or len(equipos) < 2:
        print(f"[WARN] No hay suficientes equipos para generar partidos en {ano}-{mes:02d}")
        return 0
    
    insertados = 0
    dias_mes = (datetime(ano, mes % 12 + 1, 1) if mes < 12 else datetime(ano + 1, 1, 1)) - timedelta(days=1)
    max_dia = dias_mes.day
    
    equipos_por_dia = {}
    emparejamientos_usados = set()
    
    for _ in range(num_partidos):
        intentos = 0
        max_intentos = 50
        while intentos < max_intentos:
            dia = random.randint(1, max_dia)
            horario = random.choice(HORARIOS)
            fecha_hora_str = f"{ano}-{mes:02d}-{dia:02d} {horario}"
            
            eq1, eq2 = random.sample(equipos, 2)
            local_id = eq1[0]
            visitante_id = eq2[0]
            
            clave_dia = f"{ano}-{mes:02d}-{dia:02d}"
            if clave_dia not in equipos_por_dia:
                equipos_por_dia[clave_dia] = set()
            
            if local_id in equipos_por_dia[clave_dia] or visitante_id in equipos_por_dia[clave_dia]:
                intentos += 1
                continue
            
            emparejamiento = tuple(sorted([local_id, visitante_id]))
            if emparejamiento in emparejamientos_usados:
                intentos += 1
                continue
            
            if existe_partido(conn, fecha_hora_str, local_id, visitante_id):
                intentos += 1
                continue
            
            equipos_por_dia[clave_dia].add(local_id)
            equipos_por_dia[clave_dia].add(visitante_id)
            emparejamientos_usados.add(emparejamiento)
            
            break
        
        if intentos >= max_intentos:
            continue
        
        eliminatoria = random.choice(ELIMINATORIAS)
        slot = random.randint(1, 100)
        
        arbitro_id = None
        if arbitros:
            arb = random.choice(arbitros)
            arbitro_id = arb[0]
        
        estado = random.choices(ESTADOS_POSIBLES, weights=[70, 30])[0]
        
        goles_local = None
        goles_visitante = None
        penaltis_local = None
        penaltis_visitante = None
        ganador_equipo_id = None
        
        if estado == "Jugado":
            goles_local = random.randint(0, 5)
            goles_visitante = random.randint(0, 5)
            
            if goles_local > goles_visitante:
                ganador_equipo_id = local_id
            elif goles_visitante > goles_local:
                ganador_equipo_id = visitante_id
            else:
                penaltis_local = random.randint(3, 5)
                penaltis_visitante = random.randint(3, 5)
                while penaltis_local == penaltis_visitante:
                    penaltis_visitante = random.randint(3, 5)
                if penaltis_local > penaltis_visitante:
                    ganador_equipo_id = local_id
                else:
                    ganador_equipo_id = visitante_id
        
        campos = []
        valores = []
        
        campos.append("eliminatoria")
        valores.append(eliminatoria)
        campos.append("slot")
        valores.append(slot)
        
        if "fecha_hora" in columnas_partidos:
            campos.append("fecha_hora")
            valores.append(fecha_hora_str)
        elif "fecha" in columnas_partidos:
            campos.append("fecha")
            valores.append(fecha_hora_str)
        
        campos.append("equipo_local_id")
        valores.append(local_id)
        campos.append("equipo_visitante_id")
        valores.append(visitante_id)
        
        if "arbitro_id" in columnas_partidos:
            campos.append("arbitro_id")
            valores.append(arbitro_id)
        
        if "goles_local" in columnas_partidos:
            campos.append("goles_local")
            valores.append(goles_local)
        if "goles_visitante" in columnas_partidos:
            campos.append("goles_visitante")
            valores.append(goles_visitante)
        
        if "penaltis_local" in columnas_partidos:
            campos.append("penaltis_local")
            valores.append(penaltis_local)
        if "penaltis_visitante" in columnas_partidos:
            campos.append("penaltis_visitante")
            valores.append(penaltis_visitante)
        
        if "ganador_equipo_id" in columnas_partidos:
            campos.append("ganador_equipo_id")
            valores.append(ganador_equipo_id)
        elif "ganador_id" in columnas_partidos:
            campos.append("ganador_id")
            valores.append(ganador_equipo_id)
        
        if "estado" in columnas_partidos:
            campos.append("estado")
            valores.append(estado)
        
        placeholders = ", ".join(["?"] * len(campos))
        campos_str = ", ".join(campos)
        sql = f"INSERT INTO partidos ({campos_str}) VALUES ({placeholders})"
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, valores)
            conn.commit()
            insertados += 1
        except sqlite3.IntegrityError as e:
            pass
    
    return insertados


def main():
    conn = conectar_bd()
    
    columnas_partidos = obtener_columnas_tabla(conn, "partidos")
    print(f"[INFO] Columnas en tabla partidos: {columnas_partidos}")
    
    equipos = cargar_equipos(conn)
    print(f"[INFO] Equipos disponibles: {len(equipos)}")
    
    arbitros = cargar_arbitros(conn)
    print(f"[INFO] Árbitros disponibles: {len(arbitros)}")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM partidos")
    count_antes = cursor.fetchone()[0]
    print(f"[INFO] Partidos existentes antes de insertar: {count_antes}")
    
    hoy = datetime.now()
    ano_actual = hoy.year
    mes_actual = hoy.month
    
    mes_pasado = mes_actual - 1
    ano_pasado = ano_actual
    if mes_pasado < 1:
        mes_pasado = 12
        ano_pasado -= 1
    
    mes_siguiente = mes_actual + 1
    ano_siguiente = ano_actual
    if mes_siguiente > 12:
        mes_siguiente = 1
        ano_siguiente += 1
    
    meses_a_generar = [
        (ano_pasado, mes_pasado, "Mes pasado"),
        (ano_actual, mes_actual, "Mes actual"),
        (ano_siguiente, mes_siguiente, "Mes siguiente")
    ]
    
    total_insertados = 0
    
    for ano, mes, etiqueta in meses_a_generar:
        print(f"\n[INFO] Generando partidos para {etiqueta} ({ano}-{mes:02d})...")
        num_partidos = random.randint(12, 20)
        insertados = generar_partidos_mes(conn, equipos, arbitros, columnas_partidos, ano, mes, num_partidos)
        print(f"[OK] {etiqueta} ({ano}-{mes:02d}): {insertados} partidos insertados")
        total_insertados += insertados
    
    cursor.execute("SELECT COUNT(*) FROM partidos")
    count_despues = cursor.fetchone()[0]
    print(f"\n[INFO] Partidos totales después de insertar: {count_despues}")
    
    cursor.execute("SELECT MIN(fecha_hora), MAX(fecha_hora) FROM partidos")
    min_fecha, max_fecha = cursor.fetchone()
    print(f"[INFO] Rango de fechas en BD: {min_fecha} hasta {max_fecha}")
    
    fecha_inicio = f"{ano_pasado}-{mes_pasado:02d}-01"
    fecha_fin_mes_sig = datetime(ano_siguiente, mes_siguiente % 12 + 1 if mes_siguiente < 12 else 1, 1, 0, 0, 0) if mes_siguiente < 12 else datetime(ano_siguiente + 1, 1, 1, 0, 0, 0)
    fecha_fin = fecha_fin_mes_sig.strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT COUNT(*) FROM partidos 
        WHERE date(fecha_hora) >= ? AND date(fecha_hora) < ?
    """, (fecha_inicio, fecha_fin))
    count_rango = cursor.fetchone()[0]
    print(f"[INFO] Partidos en rango {fecha_inicio} a {fecha_fin}: {count_rango}")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"[RESUMEN] Total de partidos insertados: {total_insertados}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
