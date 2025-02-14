from fastapi import FastAPI, APIRouter, HTTPException, Depends
import random
import re
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
from models.usuarios import Usuario
from typing import List, Optional
from db.db import get_db_connection

router = APIRouter()


@router.post("/usuarios", tags=["Usuarios"])
def crear_usuario(usuario: Usuario):
    #Conexión a la base de datos:
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor() 

    #Gnerador IDs
    def generar_id():
        return "GYMB"+ "".join(random.choices('0123456789', k=4))
    id_usuario = generar_id()

    #Fecha actual
    fecha_actual = datetime.now()

    #Validación de estatura
    if usuario.estatura >= 3:
        return {"mensaje": "La estatura es inválida", "exitoso" : False}
    
    #Validación de peso
    if usuario.peso >= 1000:
        return {"mensaje": "El peso no es válido", "exitoso": False}
    
    # Validación de ID de usuario
    cursor.execute("SELECT 1 FROM tb_usuario WHERE id_usuario = ?", (id_usuario))
    if cursor.fetchone():
        conn.close()
        return {"mensaje": "Ya existe un usuario con ese ID", "exitoso": False}, 400
    
    #Validación de nombre de usuario
    if len(usuario.nombre_usuario) > 100:  # Ejemplo: Máximo 100 caracteres
        conn.close()
        return {"mensaje": "El nombre es demasiado largo", "exitoso": False}, 400
    
    # Validación de correo
    if not re.match(r"[^@]+@[^@]+\.[^@]+", usuario.correo):
        conn.close()
        return {"mensaje": "El correo electrónico no es válido", "exitoso": False}, 400
    # Adicionalmente, verifica si ya existe el correo:
    cursor.execute("SELECT 1 FROM tb_usuario WHERE correo = ?", (usuario.correo,))
    if cursor.fetchone():
        conn.close()
        return {"mensaje": "Ya existe un usuario con ese correo", "exitoso": False}, 400
    
    # Validación de celular
    if not re.match(r"^\d{9}$", usuario.celular):  # Ejemplo: 9 dígitos
        conn.close()
        return {"mensaje": "El número de celular no es válido", "exitoso": False}, 400
    # Verifica si existe:
    cursor.execute("SELECT 1 FROM tb_usuario WHERE celular = ?", (usuario.celular,))
    if cursor.fetchone():
        conn.close()
        return {"mensaje": "Ya existe un usuario con ese celular", "exitoso": False}, 400
    
    # Validación de registros requeridos
    campos_requeridos = ["nombre_usuario", "apellido_paterno", "apellido_materno", "celular",
    "correo", "clave", "estatura", "peso"]
    for campo in campos_requeridos:
        if not getattr(usuario, campo):  # getattr() accede al atributo dinámicamente
            conn.close()
            return {"mensaje": f"Falta el campo obligatorio: {campo}", "exitoso": False}, 400


    cursor.execute("""
        INSERT INTO tb_usuario (id_usuario, nombre_usuario, apellido_paterno, apellido_materno, 
                   celular, correo, clave, fecha_registro, estatura, peso, estado, foto) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_usuario, usuario.nombre_usuario, usuario.apellido_paterno, usuario.apellido_materno, 
          usuario.celular, usuario.correo, usuario.clave, fecha_actual, usuario.estatura, 
          usuario.peso, usuario.estado, usuario.foto))
    
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario creado exitosamente", "exitoso" : True}


@router.get("/usuarios", tags=["Usuarios"])
def listar_usuarios():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, nombre_usuario, apellido_paterno, correo, clave FROM tb_usuario")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    content = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return content


class LoginRequest(BaseModel):
    correo: str
    clave: str

@router.post("/login", tags=["Usuarios"])
def ingresar_a_la_aplicacion(request: LoginRequest):
    """
    Inicia sesión en la aplicación y devuelve todos los datos del usuario, excepto la clave.
    """
    conn = get_db_connection()
    if not conn:
        return {"isValid": False, "message": "Error en la conexión a la base de datos"}
    
    try:
        cursor = conn.cursor()
        
        # Verificar si el correo existe
        cursor.execute("SELECT id_usuario FROM tb_usuario WHERE correo = ?", (request.correo,))
        user = cursor.fetchone()
        
        if not user:
            return {"isValid": False, "message": "Correo incorrecto"}
        
        user_id = user[0]
        
        # Verificar la clave
        cursor.execute("SELECT clave FROM tb_usuario WHERE id_usuario = ?", (user_id,))
        stored_password = cursor.fetchone()
        
        if not stored_password or request.clave != stored_password[0]:
            return {"isValid": False, "message": "Clave incorrecta"}
        
        # Obtener todos los datos del usuario excepto la clave
        cursor.execute("""
            SELECT id_usuario, nombre_usuario, apellido_paterno, apellido_materno, celular, correo, 
                   fecha_registro, estatura, peso, estado, foto
            FROM tb_usuario WHERE id_usuario = ?
        """, (user_id,))
        
        user_data = cursor.fetchone()
        columns = [column[0] for column in cursor.description]
        user_info = dict(zip(columns, user_data))
        
        return {"isValid": True, "content": user_info}

    except Exception as e:
        return {"isValid": False, "message": f"Error al iniciar sesión: {str(e)}"}
    
    finally:
        conn.close()


@router.get("/usuarios/todos", tags=["Usuarios"])
def obtener_todos_los_usuarios():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_usuario")  # Traer todos los campos de la tabla
    rows = cursor.fetchall()
    
    # Obtener los nombres de las columnas
    columns = [column[0] for column in cursor.description]
    
    # Convertir los resultados en una lista de diccionarios
    usuarios = [dict(zip(columns, row)) for row in rows]

    conn.close()
    return usuarios


##parámetros query
@router.put("/usuarios/{id_usuario}", tags=["Usuarios"])
def actualizar_usuario(id_usuario: str, usuario: Usuario):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    
    try:
        cursor = conn.cursor()

        # Verificar si el usuario existe antes de actualizar
        cursor.execute("SELECT id_usuario FROM tb_usuario WHERE id_usuario = ?", (id_usuario,))
        existing_user = cursor.fetchone()
        if not existing_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Actualizar los datos del usuario
        cursor.execute("""
            UPDATE tb_usuario 
            SET  
                celular = ?, correo = ?, clave = ?, estatura = ?, peso = ?, foto = ?
            WHERE id_usuario = ?
        """, (
            usuario.celular, usuario.correo, usuario.clave, usuario.estatura,
            usuario.peso, usuario.foto, id_usuario
        ))

        conn.commit()
        return {"mensaje": "Usuario actualizado exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")
    
    finally:
        conn.close()



@router.delete("/usuarios/{id_usuario}", tags=["Usuarios"])
def eliminar_usuario(id_usuario: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    try:
        cursor = conn.cursor()

        # 1. Verificar si el usuario existe antes de eliminar
        cursor.execute("SELECT 1 FROM tb_usuario WHERE id_usuario = ?", (id_usuario,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")  

        # 2. Eliminar el usuario
        cursor.execute("DELETE FROM tb_usuario WHERE id_usuario = ?", (id_usuario,))
        conn.commit()
        return {"mensaje": "Usuario eliminado de la base de datos exitosamente"}

    except Exception as e:
        conn.rollback()  
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")  

    finally:
        conn.close()

