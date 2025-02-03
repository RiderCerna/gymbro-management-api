from pydantic import BaseModel
from typing import List, Optional

class Ejercicio(BaseModel):
    id_ejercicio: str
    nombre_ejercicio: str
    descripcion: str
    imagen: str
    id_grupo_muscular: str
    id_tipo_ejercicio: str
    dificultad: str
    equipamiento_necesario: str
    descripcion_ejecucion: str
    errores_comunes: str
    repeticiones_recomendadas: str
    series_recomendadas: str
    tiempo_bajo_tension_recomendado: str
    descanso_entre_series_recomendado: str
    carga_recomendada: str
    beneficios: str
    precauciones: str
