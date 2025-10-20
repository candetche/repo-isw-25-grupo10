from dataclasses import dataclass
from typing import List
from .turno import Turno
from .visitante import Visitante

# Clase definida pero sin funciones implementadas
@dataclass
class Inscripcion:
    """Representa el registro exitoso de una reserva."""
    turno: Turno
    visitantes: List[Visitante]
    total_personas: int
    acepta_terminos: bool
    email_contacto: str

