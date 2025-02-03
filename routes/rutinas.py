from fastapi import FastAPI, APIRouter, HTTPException, Depends
import os
import pyodbc
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
from models.rutinas import Rutina
from typing import List, Optional
from db.db import get_db_connection

router = APIRouter()

@router.post("/rutinas", tags=["Rutinas"])
def crear_rutina(rutina: Rutina):
    fecha_actual = datetime.now()
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()   
    cursor.execute("""
        INSERT INTO tb_entrenamiento (id_entrenamiento, id_usuario, fecha) 
        VALUES (?, ?, ?)
    """, (rutina.id_entrenamiento, rutina.id_usuario, fecha_actual))

    conn.commit()
    conn.close()
    return {"mensaje": "Rutina creado exitosamente", "exitoso" : True}

@router.get("/rutinas", tags=["Rutinas"])
def listar_rutinas():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT id_entrenamiento., id_usuario, fecha FROM tb_entrenamiento")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    content = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return content