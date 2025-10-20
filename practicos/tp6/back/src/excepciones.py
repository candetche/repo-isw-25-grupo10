class ValidacionError(Exception):
    """Excepción personalizada para errores de validación."""
    pass
class ErrorSinCupo(ValidacionError):
    """Cupo disponible es menor a la cantidad de personas solicitada."""
    pass
class ErrorTerminosNoAceptados(ValidacionError):
    """No se aceptaron los términos y condiciones."""
    pass
class ErrorHorarioInvalido(ValidacionError):
    """El turno está fuera del horario de la actividad."""
    pass
class ErrorFaltaTalle(ValidacionError):
    """Falta el talle de vestimenta requerido para la actividad."""
    pass
class ErrorRestriccionEdad(ValidacionError):
    """El participante no cumple con la restricción de edad de la actividad."""
    pass
class ErrorParqueCerrado(ValidacionError):
    """El parque está cerrado en el horario solicitado."""
    pass
class ErrorChoqueHorario(ValidacionError):
    """El participante ya está inscrito en otro turno que choca en horario."""
    pass
class ErrorAnticipacion(ValidacionError):
    """La fecha de la inscripción no cumple las reglas de cierre o anticipación."""
    pass
class ErrorEmailInvalido(ValidacionError):
    """El formato del correo electrónico de contacto es inválido."""
    pass
class ErrorFechaPasada(ValidacionError):
    """La fecha del turno ya pasó."""
    pass