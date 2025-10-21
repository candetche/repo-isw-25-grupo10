
from peewee import *
from pathlib import Path

## Modelos de peewee para la base de datos SQLite (ORM)
# --- RUTA DINÁMICA ---
DIRECTORIO_SCRIPT = Path(__file__).resolve().parent 
DB_PATH = DIRECTORIO_SCRIPT.parent.parent / "db" / "bd_ecopark.db"

db = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class ActividadDB(BaseModel):
    id = AutoField()
    nombre = CharField()
    capacidad_maxima = IntegerField()
    requiere_vestimenta = BooleanField(default=False)
    edad_minima = IntegerField(null=True)

    class Meta:
        table_name = 'Actividad'

class TurnoDB(BaseModel):
    id = AutoField()
    actividad_id = ForeignKeyField(ActividadDB, backref='turnos')
    fecha = CharField()  # Mantener como CharField para compatibilidad
    hora = CharField()
    cupo_disponible = IntegerField()

    class Meta:
        table_name = 'Turno'

class InscripcionDB(BaseModel):
    id = AutoField()
    turno_id = ForeignKeyField(TurnoDB, backref='inscripciones')
    mail = CharField()
    total_personas = IntegerField()
    acepto_terminos = BooleanField(default=False)

    class Meta:
        table_name = 'Inscripcion'

class VisitanteDB(BaseModel):
    id = AutoField()
    inscripcion_id = ForeignKeyField(InscripcionDB, backref='visitantes')
    nombre = CharField()
    dni = IntegerField()
    edad = IntegerField()
    talle = CharField(null=True)

    class Meta:
        table_name = 'Visitante'