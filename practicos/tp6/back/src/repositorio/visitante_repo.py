from base import RepositorioBase

class VisitanteRepo(RepositorioBase):
    def obtener_por_dni(self, dni):
        return self.ejecutar("SELECT * FROM Visitante WHERE dni = ?", (dni,), fetchone=True)
    
    def obtener_por_inscipcion_id(self, inscripcion_id):
        return self.ejecutar("""
            SELECT * FROM Visitante 
            WHERE inscripcion_id = ?
        """, (inscripcion_id,), fetchone=True)
    
    def agregar_visitante(self, inscripcion_id, nombre, dni, edad, talle=""):
        self.ejecutar("""
            INSERT INTO Visitante (inscripcion_id, nombre, dni, edad, talle)
            VALUES (?, ?, ?, ?, ?)
        """, (inscripcion_id, nombre, dni, edad, talle), commit=True)

    