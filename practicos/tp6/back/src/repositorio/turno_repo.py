from .modelos import Turno
from .base import RepositorioBase

class RepositorioTurno(RepositorioBase):
    def __init__(self):
        super().__init__(Turno)

    def obtener_por_fecha(self, fecha):
        return list(self.modelo.select().where(self.modelo.fecha == fecha))

    def obtener_por_actividad_y_fecha(self, actividad_id, fecha_a, fecha_b):
        return list(self.modelo
                   .select()
                   .where(
                       (self.modelo.actividad_id == actividad_id) & 
                       (self.modelo.fecha >= fecha_a) & 
                       (self.modelo.fecha <= fecha_b)
                   ))

    def actualizar_cupo(self, turno_id, nuevo_cupo):
        return self.actualizar(turno_id, cupo_disponible=nuevo_cupo)
