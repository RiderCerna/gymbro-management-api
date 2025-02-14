from pydantic import BaseModel
from typing import Optional

class Rutina(BaseModel):
    id_entrenamiento: str
    id_usuario: str