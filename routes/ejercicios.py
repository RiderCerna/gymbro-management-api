from fastapi import FastAPI, APIRouter, HTTPException, Depends
import os
import pyodbc
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
from models.ejercicios import Ejercicio 
from typing import List, Optional
from db.db import get_db_connection

router = APIRouter()

@router.post("/ejercicios", tags=["Ejercicios"])
def agregar_ejercicio(ejercicio: Ejercicio):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tb_ejercicio (id_ejercicio, nombre_ejercicio, descripcion, imagen, id_grupo_muscular, id_tipo_ejercicio, 
    dificultad, equipamiento_necesario, descripcion_ejecucion, errores_comunes, repeticiones_recomendadas, series_recomendadas,
    tiempo_bajo_tension_recomendado, descanso_entre_series_recomendado, carga_recomendada, beneficios, precauciones) 
    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (ejercicio.id_ejercicio, ejercicio.nombre_ejercicio, ejercicio.descripcion, ejercicio.imagen, ejercicio.id_grupo_muscular, 
          ejercicio.id_tipo_ejercicio, ejercicio.dificultad, ejercicio.equipamiento_necesario, ejercicio.descripcion_ejecucion, 
          ejercicio.errores_comunes, ejercicio.repeticiones_recomendadas, ejercicio.series_recomendadas, 
          ejercicio.tiempo_bajo_tension_recomendado, ejercicio.descanso_entre_series_recomendado, ejercicio.carga_recomendada, 
          ejercicio.beneficios, ejercicio.precauciones))
    conn.commit()
    conn.close()
    return {"mensaje": "Ejercicio agregado exitosamente"}

@router.get("/ejercicios", tags=["Ejercicios"])
def listar_ejercicios():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT id_ejercicio, nombre_ejercicio, descripcion, id_grupo_muscular FROM tb_ejercicio")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    content = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return content





