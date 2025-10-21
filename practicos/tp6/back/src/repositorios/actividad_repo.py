from back.src.repositorios.base import RepositorioBase

class RepositorioActividad(RepositorioBase):
    def obtener_todas(self):
        return self.ejecutar("SELECT * FROM Actividad", fetchall=True)

    def obtener_por_id(self, actividad_id):
        return self.ejecutar("SELECT * FROM Actividad WHERE id = ?", (actividad_id,), fetchone=True)
    
    def obtener_por_nombre(self, nombre):
        return self.ejecutar("SELECT * FROM Actividad WHERE nombre = ?", (nombre,), fetchone=True)

