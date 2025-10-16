# backend/src/repositorio.py
from typing import List
# Se asume que Inscripcion se importará desde .modelos
from .modelos.inscripcion import Inscripcion



class RepositorioEnMemoria:
    """Mock de repositorio que guarda las inscripciones en una lista."""

    def __init__(self, inscripciones: List[Inscripcion] = None):
        self.inscripciones = inscripciones or []

    # Método para simular la persistencia que usará el servicio
    def guardar_inscripcion(self, inscripcion: Inscripcion):
        self.inscripciones.append(inscripcion)