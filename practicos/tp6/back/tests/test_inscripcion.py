import pytest
from datetime import date, time, timedelta
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
    ErrorChoqueHorario,
    ErrorAnticipacion,
    ErrorEmailInvalido,
    ErrorFechaPasada,
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

    FECHA_HOY = date(2025, 10, 15)
    FECHA_AYER = FECHA_HOY - timedelta(days=1)
    dias_hasta_lunes = (0 - FECHA_HOY.weekday() + 7) % 7
    FECHA_LUNES_CERRADO = FECHA_HOY + timedelta(days=dias_hasta_lunes if dias_hasta_lunes != 0 else 7)  # Evita el lunes de hoy si es hoy
    FECHA_3_DIAS_ANTICIPACION = FECHA_HOY + timedelta(days=3)

    EMAIL_VALIDO = "juancito@gmail.com"

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
    turno_jardineria_poco_cupo = Turno(id=301, actividad_nombre="Jardinería", fecha=FECHA_HOY, hora=time(10, 0),cupo_ocupado=10)
    turno_invalido_cerrado = Turno(id=999, actividad_nombre="Tirolesa", fecha=FECHA_HOY, hora=time(18, 30), cupo_ocupado=0)
    turno_lunes_cerrado = Turno(id=110, actividad_nombre="Tirolesa", fecha=FECHA_LUNES_CERRADO, hora=time(14, 0),cupo_ocupado=0)
    turno_25_dic = Turno(id=120, actividad_nombre="Tirolesa", fecha=date(FECHA_HOY.year, 12, 25), hora=time(14, 0),cupo_ocupado=0)
    turno_1_ene = Turno(id=130, actividad_nombre="Tirolesa", fecha=date(FECHA_HOY.year + 1, 1, 1), hora=time(14, 0),cupo_ocupado=0)
    turno_anticipacion_excesiva = Turno(id=140, actividad_nombre="Tirolesa", fecha=FECHA_3_DIAS_ANTICIPACION,hora=time(14, 0), cupo_ocupado=0)
    turno_fecha_pasada = Turno(id=160, actividad_nombre="Tirolesa", fecha=FECHA_AYER, hora=time(10, 0),cupo_ocupado=0)
    turnos_disponibles = [turno_tirolesa_con_cupo, turno_palestra_sin_cupo, turno_jardineria_poco_cupo, turno_fecha_pasada]

    # INSCRIPCIONES EXISTENTES (Para Test 8)
    turno_ana_ya_existente = Turno(id=500, actividad_nombre="Jardinería", fecha=FECHA_HOY, hora=time(14, 0), cupo_ocupado=1)
    inscripcion_ana = Inscripcion(turno=turno_ana_ya_existente, visitantes=[visitante_ana_reserva], total_personas=1,acepta_terminos=True, email_contacto=EMAIL_VALIDO)

    repo = RepositorioEnMemoria(inscripciones=[inscripcion_ana])

    # INICIALIZAR SERVICIO
    servicio = ServicioInscripcion(setup_actividades, turnos_disponibles, repo, fecha_actual=FECHA_HOY)

    return {
        "servicio": servicio,
        "repo": repo,
        "EMAIL_VALIDO": EMAIL_VALIDO,
        "turno_tirolesa_con_cupo": turno_tirolesa_con_cupo,
        "turno_palestra_sin_cupo": turno_palestra_sin_cupo,
        "turno_jardineria_poco_cupo": turno_jardineria_poco_cupo,
        "turno_invalido_cerrado": turno_invalido_cerrado,
        "turno_lunes_cerrado": turno_lunes_cerrado,
        "turno_25_dic": turno_25_dic,
        "turno_1_ene": turno_1_ene,
        "turno_anticipacion_excesiva": turno_anticipacion_excesiva,
        "turno_fecha_pasada": turno_fecha_pasada,
        # Visitantes
        "visitante_ana_reserva": visitante_ana_reserva,
        "visitante_beto_valido": visitante_beto_valido,
        "visitante_ema_sin_talle": visitante_ema_sin_talle,
        "visitante_ceci_edad_8": visitante_ceci_edad_8,
        "visitante_fede_edad_11": visitante_fede_edad_11,
        "visitante_bebe": visitante_bebe,
        "visitante_julio_nuevo": visitante_julio_nuevo,
    }

# TEST 1
def test_inscripcion_singular_valida_pasa(setup_inscripcion):
    """Test 1: Probar inscribirse a una actividad del listado que poseen cupos disponibles, seleccionando un horario,
    ingresando los datos del visitante ( nombre, DNI, edad, talla de la vestimenta si la actividad lo requiere) y
    aceptando los términos y condiciones (pasa)."""
    s = setup_inscripcion

    inscripcion = s['servicio'].inscribir(
        turno=s['turno_tirolesa_con_cupo'],
        participantes=[s['visitante_beto_valido']],
        acepta_terminos=True,
        email_contacto=s['EMAIL_VALIDO']
    )

    assert inscripcion is not None
    assert isinstance(inscripcion, Inscripcion)

# TEST 2
def test_inscripcion_sin_cupo_falla(setup_inscripcion):
    """Test 2: Probar inscribirse a una actividad que no tiene cupo (falla)."""
    s = setup_inscripcion

    # Palestra está llena (cupo_ocupado=12) y capacidad es 12.
    with pytest.raises(ErrorSinCupo):
        s['servicio'].inscribir(
            turno=s['turno_palestra_sin_cupo'],
            participantes=[s['visitante_beto_valido']],  # Solo 1 persona
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )


# TEST 3
def test_inscripcion_sin_talle_no_requerido_pasa(setup_inscripcion):
    """Test 3: Probar inscribirse a una actividad sin ingresar talle de vestimenta porque la actividad no la requiere (pasa)."""
    s = setup_inscripcion

    # Jardinería no requiere talle. Usamos visitante_ema_sin_talle.
    inscripcion = s['servicio'].inscribir(
        turno=s['turno_jardineria_poco_cupo'],
        participantes=[s['visitante_ema_sin_talle']],  # Talle es None, pero la regla dice NO se requiere
        acepta_terminos=True,
        email_contacto=s['EMAIL_VALIDO']
    )

    # RED: Este assert DEBE FALLAR inicialmente porque el servicio retorna None.
    assert inscripcion is not None

#TEST 4
def test_inscripcion_horario_invalido_falla(setup_inscripcion):
    """Test 4: Probar inscribirse a un horario en el cual el parque está cerrado (falla)."""
    s = setup_inscripcion

    # Turno 18:30 está fuera del rango 9:00-18:00
    with pytest.raises(ErrorHorarioInvalido):
        s['servicio'].inscribir(
            turno=s['turno_invalido_cerrado'],  # Hora 18:30
            participantes=[s['visitante_beto_valido']],
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )


#TEST 5
def test_inscripcion_sin_aceptar_terminos_falla(setup_inscripcion):
    """Test 5: Probar inscribirse a una actividad sin aceptar los términos y condiciones (falla)."""
    s = setup_inscripcion

    with pytest.raises(ErrorTerminosNoAceptados):
        s['servicio'].inscribir(
            turno=s['turno_tirolesa_con_cupo'],
            participantes=[s['visitante_beto_valido']],
            acepta_terminos=False,  # Clave del fallo
            email_contacto=s['EMAIL_VALIDO']
        )

#TEST 6
def test_inscripcion_sin_talle_requerido_falla(setup_inscripcion):
    """Test 6: Probar inscribirse a una actividad sin ingresar el talle de la vestimenta requerido (falla)."""
    s = setup_inscripcion

    # Tirolesa requiere talle, Ema (v_ema_sin_talle) no lo provee.
    with pytest.raises(ErrorFaltaTalle):
        s['servicio'].inscribir(
            turno=s['turno_tirolesa_con_cupo'],
            participantes=[s['visitante_ema_sin_talle']],  # Talle es None, pero la actividad lo requiere
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )

#TEST 7
# Caso 7 (Alta): Intentar inscribirse con edad inválida en Palestra (mínimo 12)
def test_inscripcion_edad_invalida_falla(setup_inscripcion):
    """Test 7: Probar inscribirse a una actividad seleccionando una edad inválida (falla)."""
    s = setup_inscripcion
    FECHA_HOY = date(2025, 10, 15)

    # Palestra tiene edad mínima 12. Fede tiene 11 (v_fede_edad_11).
    turno_palestra_con_cupo = Turno(id=201, actividad_nombre="Palestra", fecha=FECHA_HOY, hora=time(16, 0),
                                    cupo_ocupado=0)

    with pytest.raises(ErrorRestriccionEdad):
        s['servicio'].inscribir(
            turno=turno_palestra_con_cupo,
            participantes=[s['visitante_fede_edad_11']],  # 11 años < 12 años
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )

#TEST 8
def test_inscripcion_concurrencia_falla(setup_inscripcion):
    """Test 8: Probar inscribirse en un horario en el cuál el visitante ya tenga otra actividad (falla)."""
    s = setup_inscripcion

    # Ana (V001) ya tiene una reserva a las 14:00.
    # Intentamos inscribir a Ana a Tirolesa, también a las 14:00.
    with pytest.raises(ErrorChoqueHorario):
        s['servicio'].inscribir(
            turno=s['turno_tirolesa_con_cupo'],  # Mismo horario que la reserva existente de Ana (14:00)
            participantes=[s['visitante_ana_reserva']],  # Ana (DNI V001)
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )

#TEST 9
def test_inscripcion_multiple_valida_pasa(setup_inscripcion):
    """Test 9: Probar inscribir más de una persona con cupo y datos requeridos (pasa)."""
    s = setup_inscripcion

    # Tirolesa (10 capacidad - 3 ocupados = 7 disponibles). Inscribimos 3.
    participantes_multiples = [
        s['visitante_beto_valido'],  # Talle L, 28 años
        s['visitante_ceci_edad_8'],  # Talle S, 8 años (mínimo ok para Tirolesa)
        Visitante(nombre="Julio", dni=123456, edad=30, talle="XL")  # Talle XL
    ]

    inscripcion = s['servicio'].inscribir(
        turno=s['turno_tirolesa_con_cupo'],
        participantes=participantes_multiples,  # 3 personas
        acepta_terminos=True,
        email_contacto=s['EMAIL_VALIDO']
    )

    # RED: Este assert DEBE FALLAR inicialmente.
    assert inscripcion is not None
    assert len(inscripcion.visitantes) == 3

#TEST 10
def test_inscripcion_multiple_sin_cupo_falla(setup_inscripcion):
    """Test 10: Probar inscribir más de un visitante a una actividad que no tiene cupo para todos ellos (falla)."""
    s = setup_inscripcion

    # Jardinería (12 capacidad - 10 ocupados = 2 disponibles). Intentamos inscribir 3.
    participantes_insuficientes = [s['visitante_beto_valido'], s['visitante_ana_reserva'], s['visitante_ceci_edad_8']]  # Total: 3 personas

    with pytest.raises(ErrorSinCupo):
        s['servicio'].inscribir(
            turno=s['turno_jardineria_poco_cupo'],  # Solo 2 cupos disponibles
            participantes=participantes_insuficientes,  # Intentamos inscribir 3
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )

#TEST 11
def test_inscripcion_dia_parque_cerrado_falla(setup_inscripcion):
    """Probar inscribirse a una actividad cuya fecha de inicio caiga en Lunes (falla)."""
    s = setup_inscripcion

    with pytest.raises(ErrorParqueCerrado):
        s['servicio'].inscribir(
            turno=s['turno_lunes_cerrado'],
            participantes=[s['visitante_beto_valido']],
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )


# TEST 12 (MODIFICADO)
def test_con_inscripcion_fecha_pasada_falla(setup_inscripcion):
    """Probar inscribirse a una actividad cuya fecha ya ocurrió (falla)."""
    s = setup_inscripcion

    with pytest.raises(ErrorFechaPasada):
        s['servicio'].inscribir(
            turno=s['turno_fecha_pasada'],  # Turno con fecha de ayer
            participantes=[s['visitante_beto_valido']],
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )

# TEST 13
def test_inscripcion_con_anticipacion_excesiva_falla(setup_inscripcion):
    """Probar inscribirse a una actividad cuya fecha de inicio sea 3 o más días después de la fecha actual (falla)."""
    s = setup_inscripcion
    
    with pytest.raises(ErrorAnticipacion):
        s['servicio'].inscribir(
            turno=s['turno_anticipacion_excesiva'], # Fecha es +3 días
            participantes=[s['visitante_beto_valido']],
            acepta_terminos=True,
            email_contacto=s['EMAIL_VALIDO']
        )

# TEST 14
def test_inscripcion_con_email_invalido_falla(setup_inscripcion):
    """Probar inscribirse con un email de contacto que no tiene formato válido (falla)."""
    s = setup_inscripcion

    email_invalido = "correo@invalido"  # Le falta el dominio (.com, .ar, etc.)

    with pytest.raises(ErrorEmailInvalido):
        s['servicio'].inscribir(
            turno=s['turno_tirolesa_con_cupo'],
            participantes=[s['visitante_beto_valido']],
            acepta_terminos=True,
            email_contacto=email_invalido  # Clave del fallo
        )
