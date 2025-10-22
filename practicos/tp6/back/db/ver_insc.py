import sqlite3

RUTA_BD = "./bd_ecopark.db"

def ver_y_limpiar_inscripciones():
    conn = sqlite3.connect(RUTA_BD)
    cursor = conn.cursor()

    print("📋 INSCRIPCIONES REGISTRADAS:\n")

    # Traer inscripciones con sus visitantes
    cursor.execute("""
        SELECT I.id, I.turno_id, I.email_contacto, I.total_personas, I.acepta_terminos,
               T.fecha, T.hora, A.nombre
        FROM Inscripcion I
        JOIN Turno T ON I.turno_id = T.id
        JOIN Actividad A ON T.actividad_id = A.id
        ORDER BY T.fecha, T.hora
    """)

    inscripciones = cursor.fetchall()

    if not inscripciones:
        print("🟢 No hay inscripciones registradas.\n")
    else:
        for ins in inscripciones:
            ins_id, turno_id, email, total, acepta, fecha, hora, actividad = ins
            print(f"🧾 Inscripción #{ins_id}")
            print(f"   Actividad: {actividad}")
            print(f"   Turno: {fecha} {hora}")
            print(f"   Email: {email}")
            print(f"   Personas: {total}")
            print(f"   Acepta términos: {'Sí' if acepta else 'No'}")

            # Obtener visitantes asociados
            cursor.execute("""
                SELECT nombre, dni, edad, talle
                FROM Visitante
                WHERE inscripcion_id = ?
            """, (ins_id,))
            visitantes = cursor.fetchall()

            for v in visitantes:
                print(f"     👤 {v[0]} (DNI {v[1]}, {v[2]} años, talle {v[3]})")
            print("")

        print(f"🗑️ Eliminando {len(inscripciones)} inscripciones...\n")

        # Borrar en orden correcto (Visitante → Inscripcion)
        cursor.execute("DELETE FROM Visitante")
        cursor.execute("DELETE FROM Inscripcion")

        # Restaurar cupos disponibles
        cursor.execute("""
            UPDATE Turno
            SET cupo_disponible = (
                SELECT capacidad_maxima
                FROM Actividad
                WHERE Actividad.id = Turno.actividad_id
            )
        """)

        conn.commit()
        print("✅ Inscripciones eliminadas y cupos restaurados correctamente.\n")

    conn.close()


if __name__ == "__main__":
    ver_y_limpiar_inscripciones()
