from .base import RepositorioBase
from .modelos import VisitanteDB
from back.src.modelos.visitante import Visitante

class VisitanteRepo(RepositorioBase):
    def __init__(self):
        super().__init__(VisitanteDB)

    def guardar_visitante(self, visitante: Visitante):
        nuevo_visitante = self.modelo.create(
            inscripcion_id=visitante.inscripcion_id,
            nombre=visitante.nombre,
            dni=visitante.dni,
            edad=visitante.edad,
            talle=visitante.talle
        )
        return nuevo_visitante

    def obtener_todos(self):
        return super().obtener_todos()  
    
    def obtener_por_id(self, id):
        return super().obtener_por_id(id)

