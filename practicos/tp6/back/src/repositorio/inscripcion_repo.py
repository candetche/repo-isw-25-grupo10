from peewee import *
from .base import RepositorioBase
from .modelos import InscripcionDB
from back.src.modelos.inscripcion import Inscripcion

class InscripcionRepo(RepositorioBase):  
    def __init__(self):
        super().__init__(InscripcionDB)

    def guardar_inscripcion(self, inscrpcion: Inscripcion):
        nueva_inscripcion = self.modelo.create(
            turno_id=inscrpcion.turno_id,
            mail=inscrpcion.mail,
            total_personas=inscrpcion.total_personas,
            acepto_terminos=inscrpcion.acepto_terminos
        )
        return nueva_inscripcion

    def obtener_por_turno(self, turno_id):
        return list(self.modelo.select().where(self.modelo.turno_id == turno_id))
