from fastapi import FastAPI, APIRouter, HTTPException, Depends

import os
import pyodbc
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
from models.usuarios import Usuario
from models.ejercicios import Ejercicio
from models.rutinas import Rutina
from typing import List, Optional

load_dotenv()

# Configuración de la base de datos
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = "ODBC Driver 17 for SQL Server"

def get_db_connection():
    try:
        connection_string = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_HOST},{DB_PORT};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD}"
        )
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

app = FastAPI(title="Gym Training API", description="API para gestionar entrenamientos y ejercicios")
router = APIRouter()

##BASE DE DATOS PRUEBA
@router.get("/check-db", tags=["Sistema"])
def check_db_connection():
    conn = get_db_connection()
    if conn:
        conn.close()
        return {"mensaje": "Conexión a la base de datos exitosa"}
    else:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")


# MODELOS DE DATOS



class Entrenamiento(BaseModel):
    id_entrenamiento: str
    id_usuario: str
    fecha: str

class DetalleEntrenamiento(BaseModel):
    id_detalle_entrenamiento: str
    id_entrenamiento: str
    id_ejercicio: str
    series: str
    peso: float
    repeticiones: str



# ENDPOINTS DE USUARIOS
@router.post("/usuarios", tags=["Usuarios"])
def crear_usuario(usuario: Usuario):
    fecha_actual = datetime.now()
    if usuario.estatura >= 3:
        return {"mensaje": "La estatura es invalida", "exitoso" : False}
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()   
    cursor.execute("""
   
    """, (usuario.id_usuario, usuario.nombre_usuario, usuario.apellido_paterno, usuario.apellido_materno, usuario.celular, usuario.correo, usuario.contraseña, fecha_actual, usuario.estatura, usuario.peso, usuario.estado, usuario.foto))
    
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario creado exitosamente", "exitoso" : True}


@router.get("/usuarios", tags=["Usuarios"])
def listar_usuarios():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, nombre_usuario, apellido_paterno FROM tb_usuario")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    content = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return content
    
""""
@router.get("/persona", tags=["Persona"])
def obtener_persona(database_name: str = Query(...)):
    db = get_db_connection(database_name)
    cursor = db.cursor()
    try:
        cursor.execute("EXEC SP_Obtener_Persona")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        content = [dict(zip(columns, row)) for row in rows]
        return JSONResponse(
            status_code=200,
            content={
                "isValid": True,
                "content": content,
                "error": None
            }
        )
    except Exception as e:
        logger.error(f"Error al obtener personas: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "isValid": False,
                "content": None,
                "error": str(e)
            }
        )
    finally:
        cursor.close()
        db.close()
"""

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
