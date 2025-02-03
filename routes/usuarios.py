from fastapi import FastAPI, APIRouter, HTTPException, Depends
import os
import pyodbc
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
from models.usuarios import Usuario
from typing import List, Optional
from db.db import get_db_connection

router = APIRouter()


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
        INSERT INTO tb_usuario (id_usuario, nombre_usuario, apellido_paterno, apellido_materno, celular, correo, contraseña, fecha_registro, estatura, peso, estado, foto) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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