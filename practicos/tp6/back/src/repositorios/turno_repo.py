from back.src.repositorios.base import RepositorioBase

class RepositorioTurno(RepositorioBase):
    def obtener_por_fecha(self, fecha):
        """
        Devuelve los turnos de una fecha específica (YYYY-MM-DD).
        Incluye log para depuración.
        """
        print(f"🧩 DEBUG: buscando turnos para fecha = {fecha}")

        resultados = self.ejecutar("""
                                   SELECT id, actividad_id, fecha, hora, cupo_disponible
                                   FROM Turno
                                   WHERE fecha LIKE ? OR date (fecha) = date (?)
                                   ORDER BY hora ASC
                                   """, (f"%{fecha}%", fecha), fetchall=True)

        print(f"✅ DEBUG: se encontraron {len(resultados)} turnos para {fecha}")
        return resultados

    def obtener_por_actividad_y_fecha(self, actividad_id, fecha_a, fecha_b):
        return self.ejecutar("""SELECT * FROM Turno 
            WHERE actividad_id = ?
            AND fecha >= ? 
            AND fecha <= ?
            """, (actividad_id, fecha_a, fecha_b), fetchall=True)

    def actualizar_cupo(self, turno_id: int, nuevo_cupo: int):
        """
        Actualiza el cupo disponible de un turno.
        Si el nuevo cupo es negativo, se fuerza a 0.
        """

        # Asegurarse de no permitir valores negativos
        if nuevo_cupo < 0:
            nuevo_cupo = 0

        # Ejecutar actualización en la base de datos
        self.ejecutar("""
                      UPDATE Turno
                      SET cupo_disponible = ?
                      WHERE id = ?
                      """, (nuevo_cupo, turno_id), commit=True)

        # (Opcional) Verificar si se actualizó correctamente
        actualizado = self.ejecutar(
            "SELECT cupo_disponible FROM Turno WHERE id = ?",
            (turno_id,),
            fetchone=True
        )

        if actualizado:
            print(f"✅ Cupo actualizado correctamente para turno {turno_id}: nuevo cupo = {actualizado[0]}")
        else:
            print(f"⚠️ Advertencia: no se encontró el turno con id {turno_id}")

