from peewee import *
from .modelos import db

## Repositorio base para operaciones comunes
class RepositorioBase:
    def __init__(self, modelo):
        self.modelo = modelo
        self.db = db

    def get_connection(self):
        return self.db

    def ejecutar(self, query):
        with self.db.atomic():
            return query.execute()

    def obtener_por_id(self, id):
        return self.modelo.get_or_none(self.modelo.id == id)

    def obtener_todos(self):
        return list(self.modelo.select())
    

# Repositorio en memoria para pruebas
class RepositorioEnMemoria:
    """Mock de repositorio que guarda las inscripciones en una lista."""
    def __init__(self, inscripciones=None):
        self.inscripciones = inscripciones or []

    def guardar_inscripcion(self, inscripcion):
        self.inscripciones.append(inscripcion)