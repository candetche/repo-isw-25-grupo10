from back.src.repositorios.base import RepositorioBase

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

    #para que valide antes de dar al aceptar al final de todo (antes de guardar)
    def existe_choque_por_dni_y_fecha_hora(self, dni: int, fecha: str, hora: str) -> bool:
        """
        Verifica si un visitante (por DNI) ya está inscripto en cualquier actividad
        para la misma fecha y hora.
        """
        row = self.ejecutar(
            """
            SELECT 1
            FROM Visitante v
            JOIN Inscripcion i ON v.inscripcion_id = i.id
            JOIN Turno t ON i.turno_id = t.id
            WHERE v.dni = ? AND t.fecha = ? AND t.hora = ?
            LIMIT 1
            """,
            (dni, fecha, hora),
            fetchone=True,
        )
        return row is not None