import sqlite3
from typing import List
from pathlib import Path

# --- RUTA DINÁMICA ---
DIRECTORIO_SCRIPT = Path(__file__).resolve().parent
DB_PATH = DIRECTORIO_SCRIPT.parent.parent / "db" / "bd_ecopark.db"


class RepositorioBase:
    def __init__(self):
        self.db_path = DB_PATH

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def ejecutar(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute(query, params)

        result = None
        if fetchone:
            result = cur.fetchone()
        elif fetchall:
            result = cur.fetchall()

        if commit:
            conn.commit()

        conn.close()
        return result


# Repositorio en memoria para pruebas
from back.src.modelos.inscripcion import Inscripcion


class RepositorioEnMemoria(RepositorioBase):
    """Mock de repositorio que guarda las inscripciones en una lista."""

    def __init__(self, inscripciones: List[Inscripcion] = None):
        self.inscripciones = inscripciones or []

    # Método para simular la persistencia que usará el servicio
    def guardar_inscripcion(self, inscripcion: Inscripcion):
        self.inscripciones.append(inscripcion)
