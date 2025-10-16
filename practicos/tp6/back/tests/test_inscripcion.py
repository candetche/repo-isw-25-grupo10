import pytest
from datetime import date, time
from back.src.servicio_inscripcion import ServicioInscripcion
from back.src.repositorio import RepositorioEnMemoria
from back.src.modelos.visitante import Visitante
from back.src.modelos.turno import Turno
from back.src.modelos.inscripcion import Inscripcion
from back.src.excepciones import (
    ErrorSinCupo,
    ErrorTerminosNoAceptados,
    ErrorHorarioInvalido,
    ErrorFaltaTalle,
    ErrorRestriccionEdad,
    ErrorParqueCerrado,
    ErrorChoqueHorario
)

@pytest.fixture
def setup_actividades():
    """Define las reglas de negocio estáticas de las actividades (Cupos, Edad, Talles)."""
    return {
        "Safari": {"capacidad": 8, "edad_minima": None, "requiere_talle": False},
        "Palestra": {"capacidad": 12, "edad_minima": 12, "requiere_talle": True},
        "Jardinería": {"capacidad": 12, "edad_minima": None, "requiere_talle": False},
        "Tirolesa": {"capacidad": 10, "edad_minima": 8, "requiere_talle": True},
    }


@pytest.fixture
def setup_inscripcion(setup_actividades):
    """Define el estado inicial dinámico del sistema para todas las pruebas."""

    FECHA_HOY = date.today()

    # VISITANTES SETEADOS PARA TESTS
    visitante_ana_reserva = Visitante(nombre="Ana", dni=30123456, edad=30, talle="M")
    visitante_beto_valido = Visitante(nombre="Beto", dni=25678901, edad=28, talle="L")
    visitante_ema_sin_talle = Visitante(nombre="Ema", dni=18901234, edad=35, talle=None)
    visitante_ceci_edad_8 = Visitante(nombre="Ceci", dni=45678901, edad=8, talle="S")
    visitante_fede_edad_11 = Visitante(nombre="Fede", dni=42345678, edad=11, talle="S")
    visitante_bebe = Visitante(nombre="Gala", dni=50000001, edad=2, talle=None)
    visitante_julio_nuevo = Visitante(nombre="Julio", dni=39987654, edad=30, talle="XL")

    # TURNOS 
    turno_tirolesa_con_cupo = Turno(id=101, actividad_nombre="Tirolesa", fecha=FECHA_HOY, hora=time(14, 0), cupo_ocupado=3)
    turno_palestra_sin_cupo = Turno(id=202, actividad_nombre="Palestra", fecha=FECHA_HOY, hora=time(15, 0), cupo_ocupado=12)
    turno_jardineria_poco_cupo = Turno(id=301, actividad_nombre="Jardinería", fecha=FECHA_HOY, hora=time(10, 0),
                                   cupo_ocupado=10)
    turno_invalido_cerrado = Turno(id=999, actividad_nombre="Tirolesa", fecha=FECHA_HOY, hora=time(18, 30), cupo_ocupado=0)

    turnos_disponibles = [turno_tirolesa_con_cupo, turno_palestra_sin_cupo, turno_jardineria_poco_cupo]

    # INSCRIPCIONES EXISTENTES (Para Test 8)
    turno_ana_ya_existente = Turno(id=500, actividad_nombre="Jardinería", fecha=FECHA_HOY, hora=time(14, 0), cupo_ocupado=1)
    inscripcion_ana = Inscripcion(turno=turno_ana_ya_existente, visitantes=[visitante_ana_reserva], total_personas=1,
                                  acepta_terminos=True)

    repo = RepositorioEnMemoria(inscripciones=[inscripcion_ana])

    # INICIALIZAR SERVICIO
    servicio = ServicioInscripcion(setup_actividades, turnos_disponibles, repo)

    return {
        "servicio": servicio,
        "repo": repo,
        "turno_tirolesa_con_cupo": turno_tirolesa_con_cupo,
        "turno_palestra_sin_cupo": turno_palestra_sin_cupo,
        "turno_jardineria_poco_cupo": turno_jardineria_poco_cupo,
        "turno_invalido_cerrado": turno_invalido_cerrado,
        # Visitantes
        "visitante_ana_reserva": visitante_ana_reserva,
        "visitante_beto_valido": visitante_beto_valido,
        "visitante_ema_sin_talle": visitante_ema_sin_talle,
        "visitante_ceci_edad_8": visitante_ceci_edad_8,
        "visitante_fede_edad_11": visitante_fede_edad_11,
        "visitante_bebe": visitante_bebe,
        "visitante_julio_nuevo": visitante_julio_nuevo,
    }

# TEST 3
def test_participante_sin_talle_inscribe_actividad_no_requiere_talle_pasa(servicio, configuracion_actividades):
    turno = configuracion_actividades["_turnos"]["_t_Palestra_1200"]
    luz = configuracion_actividades["_p_Luz_Palestra_sin_talle"]

    with pytest.raises(ErrorFaltaTalle):
        servicio.inscribir(
            turno_id=turno["turno_id"],
            participantes=[luz],
            terminos_aceptados=True
        )