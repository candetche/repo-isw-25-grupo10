from base import RepositorioBase

class InscripcionRepo(RepositorioBase):    
    def agregar_inscripcion(self, turno_id, mail, total_personas, acepto_terminos):
        self.ejecutar("""
            INSERT INTO Inscripcion (turno_id, mail, total_personas, acepto_terminos)
            VALUES (?, ?, ?, ?)
        """, (turno_id, mail, total_personas, acepto_terminos), commit=True)
    
    def obtener_por_turno(self, turno_id):
        return self.ejecutar("""
            SELECT * FROM Inscripcion 
            WHERE turno_id = ?
        """, (turno_id,), fetchall=True)