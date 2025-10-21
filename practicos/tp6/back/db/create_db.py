import sqlite3
from datetime import datetime, timedelta, time

# ========================================
# CONEXIÓN Y CREACIÓN DE TABLAS
# ========================================
# Para correr este script, asegurarse de estar parado 
# sobre la carpeta de BD y ejecutar: 
#       python create_db.py
# Esto creará la base de datos y las tablas necesarias 
# si no existen y cargará las ACTIVIDADES y TURNOS de 
# las próximas 4 semanas.
# ========================================
RUTA_BD = "./bd_ecopark.db"

# Crear o conectar a la base de datos
conn = sqlite3.connect(RUTA_BD)
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Actividad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        capacidad_maxima INTEGER NOT NULL,
        requiere_vestimenta INTEGER NOT NULL DEFAULT 0,
        edad_minima INTEGER
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Turno (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actividad_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        cupo_disponible INTEGER NOT NULL,
        FOREIGN KEY (actividad_id) REFERENCES Actividad(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Inscripcion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turno_id INTEGER NOT NULL,
        mail TEXT NOT NULL,
        total_personas INTEGER NOT NULL,
        acepto_terminos INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (turno_id) REFERENCES Turno(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Visitante (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inscripcion_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        dni INTEGER NOT NULL,
        edad INTEGER NOT NULL,
        talle TEXT,
        FOREIGN KEY (inscripcion_id) REFERENCES Inscripcion(id)
    )
""")

conn.commit()

# ========================================
# CONFIGURACIÓN DEL PARQUE NATURAL
# ========================================

HORARIO_INICIO = time(9, 0)
HORARIO_FIN = time(18, 0)
DURACION_TURNO_MIN = 30
DIAS_CERRADOS = [0]  # 0 = lunes
FERIADOS = ["2025-12-25", "2026-01-01"]
HORIZONTE_SEMANAS = 4  # generar turnos para las próximas 4 semanas

# ========================================
# CUPOS Y REGLAS POR ACTIVIDAD
# ========================================

ACTIVIDADES_PREDEFINIDAS = [
    ("Safari", 8, 0, None),        # (nombre, cupo, requiere_vestimenta, edad_minima)
    ("Palestra", 12, 1, 12),
    ("Jardinería", 12, 0, None),
    ("Tirolesa", 10, 1, 8)
]

# ========================================
# FUNCIONES AUXILIARES
# ========================================

def asegurar_actividades(cursor):
    """Inserta las actividades base si no existen."""
    for nombre, cupo, requiere_vestimenta, edad_minima in ACTIVIDADES_PREDEFINIDAS:
        cursor.execute("SELECT id FROM Actividad WHERE nombre = ?", (nombre,))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO Actividad (nombre, capacidad_maxima, requiere_vestimenta, edad_minima)
                VALUES (?, ?, ?, ?)
            """, (nombre, cupo, requiere_vestimenta, edad_minima))
    print("✅ Actividades base verificadas o insertadas correctamente.")

def obtener_ultima_fecha(cursor):
    cursor.execute("SELECT MAX(fecha) FROM Turno")
    resultado = cursor.fetchone()[0]
    if resultado:
        return datetime.strptime(resultado, "%Y-%m-%d").date()
    return None

def generar_turnos(cursor):
    """Genera turnos nuevos según las reglas del parque."""
    hoy = datetime.now().date()
    fecha_limite = hoy + timedelta(weeks=HORIZONTE_SEMANAS)
    ultima_fecha = obtener_ultima_fecha(cursor)

    if ultima_fecha and ultima_fecha >= fecha_limite:
        print(f"✅ Ya existen turnos hasta {ultima_fecha}")
        return

    fecha_inicio = (ultima_fecha + timedelta(days=1)) if ultima_fecha else hoy
    print(f"🧩 Generando turnos desde {fecha_inicio} hasta {fecha_limite}...")

    cursor.execute("SELECT id, capacidad_maxima FROM Actividad")
    actividades = cursor.fetchall()

    for actividad_id, capacidad in actividades:
        fecha = fecha_inicio
        while fecha <= fecha_limite:
            # Saltar lunes y feriados
            if fecha.weekday() not in DIAS_CERRADOS and fecha.strftime("%Y-%m-%d") not in FERIADOS:
                hora = datetime.combine(fecha, HORARIO_INICIO)
                fin = datetime.combine(fecha, HORARIO_FIN)

                while hora < fin:
                    cursor.execute("""
                        INSERT INTO Turno (actividad_id, fecha, hora, cupo_disponible)
                        VALUES (?, ?, ?, ?)
                    """, (actividad_id, fecha.strftime("%Y-%m-%d"), hora.strftime("%H:%M"), capacidad))
                    hora += timedelta(minutes=DURACION_TURNO_MIN)
            fecha += timedelta(days=1)
    print("✅ Turnos generados correctamente.")

# ========================================
# EJECUCIÓN DEL SCRIPT
# ========================================

if __name__ == "__main__":
    try:
        asegurar_actividades(cursor)
        generar_turnos(cursor)
        conn.commit()
        print("🎉 Proceso completado sin errores.")
    except Exception as e:
        print("⚠️ Error durante la generación de turnos:", e)
    finally:
        conn.close()
