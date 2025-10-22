from back.src.repositorios.base import RepositorioBase


class InscripcionRepo(RepositorioBase):
    def guardar(self, inscripcion):
        """Guarda una inscripción completa en la base de datos."""
        turno_id = inscripcion.turno.id
        email_contacto = inscripcion.email_contacto
        acepta_terminos = inscripcion.acepta_terminos
        total_personas = inscripcion.total_personas

        # Usar una única conexión/transaction para asegurar que lastrowid corresponda
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            # Insert Inscripcion
            cur.execute(
                """
                INSERT INTO Inscripcion (turno_id, email_contacto, total_personas, acepta_terminos)
                VALUES (?, ?, ?, ?)
                """,
                (turno_id, email_contacto, total_personas, int(acepta_terminos)),
            )
            inscripcion_id = cur.lastrowid
            # Insert Visitantes
            for v in inscripcion.visitantes:
                cur.execute(
                    """
                    INSERT INTO Visitante (inscripcion_id, nombre, dni, edad, talle)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (inscripcion_id, v.nombre, v.dni, v.edad, v.talle or ""),
                )
            conn.commit()
            return inscripcion_id
        finally:
            conn.close()

    def obtener_por_turno(self, turno_id):
        return self.ejecutar(
            "SELECT * FROM Inscripcion WHERE turno_id = ?", (turno_id,), fetchall=True
        )

    def obtener_todas(self):
        return self.ejecutar("SELECT * FROM Inscripcion", fetchall=True)
