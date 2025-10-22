from dataclasses import dataclass


# Clase definida pero sin funciones implementadas
@dataclass
class Actividad:
    id = int
    nombre = str
    capacidad_maxima = int
    requiere_vestimenta = bool
    edad_minima = int
