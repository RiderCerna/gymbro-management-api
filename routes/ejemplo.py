from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DRIVER = "ODBC Driver 17 for SQL Server"

def get_db_connection(database_name: str):
    try:
        connection_string = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_HOST},{DB_PORT};"
            f"DATABASE={database_name};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD}"
        )
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

app = FastAPI()
router = APIRouter()

# MODELOS DE DATOS
class Usuario(BaseModel):
    nombre: str
    email: str
    edad: Optional[int] = None
    peso: Optional[float] = None

class Ejercicio(BaseModel):
    nombre: str
    musculo: str
    dificultad: str

class Rutina(BaseModel):
    usuario_id: int
    ejercicios: List[int]
    duracion: int  # Minutos

# ENDPOINTS DE USUARIOS
@router.post("/usuarios", tags=["Usuarios"])
def crear_usuario(usuario: Usuario):
    conn = get_db_connection("mi_base_datos")
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Usuarios (nombre, email, edad, peso) VALUES (?, ?, ?, ?)",
                   usuario.nombre, usuario.email, usuario.edad, usuario.peso)
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario creado"}

@router.get("/usuarios", tags=["Usuarios"])
def listar_usuarios():
    conn = get_db_connection("mi_base_datos")
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, edad, peso FROM Usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return [dict(zip([column[0] for column in cursor.description], row)) for row in usuarios]

# ENDPOINTS DE EJERCICIOS
@router.post("/ejercicios", tags=["Ejercicios"])
def agregar_ejercicio(ejercicio: Ejercicio):
    conn = get_db_connection("mi_base_datos")
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Ejercicios (nombre, musculo, dificultad) VALUES (?, ?, ?)",
                   ejercicio.nombre, ejercicio.musculo, ejercicio.dificultad)
    conn.commit()
    conn.close()
    return {"mensaje": "Ejercicio agregado"}

@router.get("/ejercicios", tags=["Ejercicios"])
def listar_ejercicios():
    conn = get_db_connection("mi_base_datos")
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, musculo, dificultad FROM Ejercicios")
    ejercicios = cursor.fetchall()
    conn.close()
    return [dict(zip([column[0] for column in cursor.description], row)) for row in ejercicios]

# ENDPOINTS DE RUTINAS
@router.post("/rutinas", tags=["Rutinas"])
def crear_rutina(rutina: Rutina):
    conn = get_db_connection("mi_base_datos")
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Rutinas (usuario_id, duracion) OUTPUT INSERTED.id VALUES (?, ?)",
                   rutina.usuario_id, rutina.duracion)
    rutina_id = cursor.fetchone()[0]
    for ejercicio_id in rutina.ejercicios:
        cursor.execute("INSERT INTO RutinaEjercicios (rutina_id, ejercicio_id) VALUES (?, ?)",
                       rutina_id, ejercicio_id)
    conn.commit()
    conn.close()
    return {"mensaje": "Rutina creada", "rutina_id": rutina_id}

@router.get("/rutinas", tags=["Rutinas"])
def listar_rutinas():
    conn = get_db_connection("mi_base_datos")
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario_id, duracion FROM Rutinas")
    rutinas = cursor.fetchall()
    conn.close()
    return [dict(zip([column[0] for column in cursor.description], row)) for row in rutinas]

# REGISTRAR EL ROUTER
app.include_router(router)
