from dataclasses import dataclass
from datetime import date, time


# Clase definida pero sin funciones implementadas
@dataclass
class Turno:
    """Representa un horario específico de una actividad con estado de ocupación."""

    id: int
    actividad_nombre: str  # Usamos nombre en lugar de ID para simplificar la consulta
    fecha: date
    hora: time
    cupo_ocupado: int
