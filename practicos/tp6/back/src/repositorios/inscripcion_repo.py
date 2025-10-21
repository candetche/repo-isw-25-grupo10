from back.src.repositorios.base import RepositorioBase

class InscripcionRepo(RepositorioBase):
    def guardar(self, inscripcion):
        """Guarda una inscripción completa en la base de datos."""
        turno_id = inscripcion.turno.id
        email_contacto = inscripcion.email_contacto
        acepta_terminos = inscripcion.acepta_terminos
        total_personas = inscripcion.total_personas

        # Insertar la inscripción
        self.ejecutar("""
            INSERT INTO Inscripcion (turno_id, email_contacto, total_personas, acepta_terminos)
            VALUES (?, ?, ?, ?)
        """, (turno_id, email_contacto, total_personas, int(acepta_terminos)), commit=True)

        # Obtener el ID recién insertado
        inscripcion_id = self.ejecutar("SELECT last_insert_rowid()", fetchone=True)[0]

        # Insertar visitantes asociados
        for v in inscripcion.visitantes:
            self.ejecutar("""
                INSERT INTO Visitante (inscripcion_id, nombre, dni, edad, talle)
                VALUES (?, ?, ?, ?, ?)
            """, (inscripcion_id, v.nombre, v.dni, v.edad, v.talle or ""), commit=True)

        return inscripcion_id

    def obtener_por_turno(self, turno_id):
        return self.ejecutar("SELECT * FROM Inscripcion WHERE turno_id = ?", (turno_id,), fetchall=True)

    def obtener_todas(self):
        return self.ejecutar("SELECT * FROM Inscripcion", fetchall=True)
