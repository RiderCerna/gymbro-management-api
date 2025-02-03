from pydantic import BaseModel
from typing import List, Optional


class Usuario(BaseModel):
    id_usuario: str
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