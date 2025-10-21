from .base import RepositorioBase
from .modelos import ActividadDB
from back.src.modelos.actividad import Actividad

class RepositorioActividad(RepositorioBase):
    def __init__(self):
        super().__init__(ActividadDB)

    


