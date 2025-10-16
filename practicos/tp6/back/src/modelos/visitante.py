from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import date, time

# Clase definida pero sin funciones implementadas
@dataclass
class Visitante:
    nombre: str
    dni: int
    edad: int
    talle: Optional[str] = None
