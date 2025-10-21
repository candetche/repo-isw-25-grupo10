# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date, time

# Importar tus módulos internos
from back.src.modelos.visitante import Visitante
from back.src.modelos.turno import Turno
from back.src.servicio_inscripcion import ServicioInscripcion
from back.src.repositorios.turno_repo import RepositorioTurno
from back.src.repositorios.inscripcion_repo import InscripcionRepo
from back.src.repositorios.actividad_repo import RepositorioActividad
from back.src.repositorios.visitante_repo import VisitanteRepo
from back.src.excepciones import (
    ErrorSinCupo, ErrorTerminosNoAceptados, ErrorHorarioInvalido, ErrorFaltaTalle,
    ErrorRestriccionEdad, ErrorParqueCerrado, ErrorChoqueHorario,
    ErrorAnticipacion, ErrorEmailInvalido, ErrorFechaPasada
)


app = FastAPI(title="EcoHarmony Park API")



# --- Habilitar CORS para permitir peticiones desde React ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción poner tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de entrada (para FastAPI) ---
class VisitanteIn(BaseModel):
    nombre: str
    dni: int
    edad: int
    talle: str | None = None

class InscripcionIn(BaseModel):
    actividad: str
    fecha: str     # formato YYYY-MM-DD
    hora: str      # formato HH:MM
    participantes: list[VisitanteIn]
    email: str
    acepta_terminos: bool


# --- Endpoint principal ---
@app.post("/api/inscribirse")
def inscribirse(payload: InscripcionIn):
    try:
        # 1️⃣ Repositorios y datos auxiliares
        repo_insc = InscripcionRepo()
        repo_turno = RepositorioTurno()
        repo_act = RepositorioActividad()
        repo_visit = VisitanteRepo()

        # Buscar la actividad en la BD
        act = repo_act.obtener_por_nombre(payload.actividad)
        if not act:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

        # Buscar el turno correspondiente
        turnos = repo_turno.obtener_por_actividad_y_fecha(act[0], payload.fecha, payload.fecha)
        turno_match = next((t for t in turnos if t[3] == payload.hora), None)
        if not turno_match:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        # turno_match = (id, actividad_id, fecha, hora, cupo_disponible)
        turno = Turno(
            id=turno_match[0],
            actividad_nombre=payload.actividad,
            fecha=datetime.strptime(payload.fecha, "%Y-%m-%d").date(),
            hora=datetime.strptime(payload.hora, "%H:%M").time(),
            cupo_ocupado=(repo_act.obtener_por_id(act[0])[2] - turno_match[4])  # capacidad_maxima - cupo_disponible
        )

        # 2️⃣ Crear visitantes
        participantes = [Visitante(**v.dict()) for v in payload.participantes]

        # 3️⃣ Configuración de actividades (deberías moverla a una constante)
        setup_actividades = {
            "Safari": {"capacidad": 8, "requiere_talle": False, "edad_minima": 0},
            "Palestra": {"capacidad": 12, "requiere_talle": True, "edad_minima": 12},
            "Jardinería": {"capacidad": 12, "requiere_talle": False, "edad_minima": 0},
            "Tirolesa": {"capacidad": 10, "requiere_talle": True, "edad_minima": 8},
        }

        # 4️⃣ Servicio principal
        # obtener inscripciones previas desde la BD
        inscripciones_previas = repo_insc.obtener_todas() if hasattr(repo_insc, "obtener_todas") else []
        repo_insc.inscripciones = inscripciones_previas  # el servicio las usará internamente
        servicio = ServicioInscripcion(setup_actividades, [turno], repo_insc)
        inscripcion = servicio.inscribir(
            turno=turno,
            participantes=participantes,
            acepta_terminos=payload.acepta_terminos,
            email_contacto=payload.email
        )

        # 5️⃣ Guardar inscripción y visitantes
        inscripcion_id = repo_insc.guardar(inscripcion)

        repo_turno.actualizar_cupo(turno.id, turno.cupo_ocupado)

        for v in payload.participantes:
            repo_visit.agregar_visitante(inscripcion_id, v.nombre, v.dni, v.edad, v.talle or "")
        return {"ok": True, "mensaje": f"Inscripción confirmada para {payload.actividad} el {payload.fecha} a las {payload.hora}"}

    except (
        ErrorSinCupo, ErrorTerminosNoAceptados, ErrorHorarioInvalido, ErrorFaltaTalle,
        ErrorRestriccionEdad, ErrorParqueCerrado, ErrorChoqueHorario,
        ErrorAnticipacion, ErrorEmailInvalido, ErrorFechaPasada
    ) as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/api/actividades")
def listar_actividades():
    try:
        repo_act = RepositorioActividad()
        actividades = repo_act.obtener_todas()

        out = []
        for a in actividades:
            # a es una tupla (id, nombre, capacidad_maxima, requiere_vestimenta, edad_minima)
            out.append({
                "id": a[0],
                "nombre": a[1],
                "cupos": a[2],
                "requiere_talle": bool(a[3]),
                "edad_min": a[4] if len(a) > 4 else 0
            })
        return out

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar actividades: {str(e)}")

@app.get("/api/turnos")
def listar_turnos(fecha: str | None = None):
    """
    Si se pasa ?fecha=YYYY-MM-DD, devuelve los turnos de ese día.
    Si no se pasa, devuelve todos los turnos desde hoy en adelante.
    """
    try:
        repo_turno = RepositorioTurno()

        if fecha:
            # Buscar turnos exactos para la fecha dada
            turnos = repo_turno.obtener_por_fecha(fecha)
        else:
            # Buscar todos los turnos desde hoy en adelante
            hoy = datetime.now().strftime("%Y-%m-%d")
            turnos = repo_turno.ejecutar("""
                SELECT id, actividad_id, fecha, hora, cupo_disponible
                FROM Turno
                WHERE fecha >= ?
                ORDER BY fecha, hora
            """, (hoy,), fetchall=True)

        out = [
            {
                "id": t[0],
                "actividad_id": t[1],
                "fecha": t[2],
                "hora": t[3],
                "cupos_disponibles": t[4],
            }
            for t in turnos
        ]

        return out

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar turnos: {str(e)}")
