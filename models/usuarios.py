from pydantic import BaseModel, Field
from typing import List, Optional
import random
'''' Funcion para autogenerar IDS

'''

class Usuario(BaseModel):
    nombre_usuario: str
    apellido_paterno: str
    apellido_materno: str
    celular: str 
    correo: str
    contraseña: str
    estatura: float
    peso: float
    estado: str
    foto: Optional[str] = None


