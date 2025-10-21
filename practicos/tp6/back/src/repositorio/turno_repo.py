from base import RepositorioBase

class RepositorioTurno(RepositorioBase):
    def obtener_por_fecha(self, fecha):
        return self.ejecutar("SELECT * FROM Turno WHERE fecha = ?", (fecha,), fetchall=True)
    
    def obtener_por_actividad_y_fecha(self, actividad_id, fecha_a, fecha_b):
        return self.ejecutar("""SELECT * FROM Turno 
            WHERE actividad_id = ?
            AND fecha >= ? 
            AND fecha <= ?
            """, (actividad_id, fecha_a, fecha_b), fetchall=True)

    def actualizar_cupo(self, turno_id, nuevo_cupo):
        self.ejecutar("""
            UPDATE Turno SET cupo_disponible = ?
            WHERE id = ?
        """, (nuevo_cupo, turno_id), commit=True)
