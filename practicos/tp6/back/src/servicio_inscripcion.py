from typing import List, Optional, Dict
from datetime import date, time
from .modelos.inscripcion import Inscripcion
from .modelos.turno import Turno
from .modelos.visitante import Visitante
from .repositorio import RepositorioEnMemoria

class ServicioInscripcion:
    """Servicio de la lógica de negocio para gestionar inscripciones."""

    def __init__(self, setup_actividades: Dict, turnos_disponibles: List[Turno], repo: RepositorioEnMemoria):
        self.setup_actividades = setup_actividades
        self.turnos_disponibles = {t.id: t for t in turnos_disponibles}
        self.repo = repo
        self.horario_cierre = time(18, 0)
        self.horario_apertura = time(9, 0)

    def inscribir(self, turno: Turno, participantes: List[Visitante], acepta_terminos: bool) -> Optional[
        Inscripcion]:
        return None