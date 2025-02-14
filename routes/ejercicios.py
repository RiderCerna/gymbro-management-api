from fastapi import FastAPI, APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from db.db import get_db_connection
from models.ejercicios import Ejercicio

router = APIRouter()

# Modelos de respuesta
class ResponseModel(BaseModel):
    isValid: bool
    content: List[dict] = []

@router.post("/ejercicios", tags=["Ejercicios"], response_model=ResponseModel)
def agregar_ejercicio(ejercicio: Ejercicio):
    """
    Agrega un nuevo ejercicio a la base de datos.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO tb_ejercicio (
                id_ejercicio, nombre_ejercicio, descripcion, imagen, id_grupo_muscular, id_tipo_ejercicio, 
                dificultad, equipamiento_necesario, descripcion_ejecucion, errores_comunes, repeticiones_recomendadas, 
                series_recomendadas, tiempo_bajo_tension_recomendado, descanso_entre_series_recomendado, carga_recomendada, 
                beneficios, precauciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            ejercicio.id_ejercicio, ejercicio.nombre_ejercicio, ejercicio.descripcion, ejercicio.imagen, 
            ejercicio.id_grupo_muscular, ejercicio.id_tipo_ejercicio, ejercicio.dificultad, ejercicio.equipamiento_necesario, 
            ejercicio.descripcion_ejecucion, ejercicio.errores_comunes, ejercicio.repeticiones_recomendadas, 
            ejercicio.series_recomendadas, ejercicio.tiempo_bajo_tension_recomendado, ejercicio.descanso_entre_series_recomendado, 
            ejercicio.carga_recomendada, ejercicio.beneficios, ejercicio.precauciones
        ))
        conn.commit()
        return {"isValid": True, "content": [{"mensaje": "Ejercicio agregado exitosamente"}]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar el ejercicio: {e}")
    finally:
        conn.close()

@router.get("/ejercicios", tags=["Ejercicios"], response_model=ResponseModel)
def listar_ejercicios():
    """
    Lista todos los ejercicios de la base de datos.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
                       select 
                        E.id_ejercicio,
                        E.nombre_ejercicio,
                        E.descripcion,
                        E.imagen,
                        E.dificultad,
                        E.id_grupo_muscular,
                        G.nombre_grupo_muscular,
                        E.id_tipo_ejercicio,
                        TE.nombre_tipo_ejercicio,
                        E.equipamiento_necesario
                        from  tb_ejercicio E
                        inner join tb_tipo_ejercicio TE ON  E.id_tipo_ejercicio = TE.id_tipo_ejercicio
                        inner join tb_grupo_muscular G ON E.id_grupo_muscular = G.id_grupo_muscular
                       """)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        content = [dict(zip(columns, row)) for row in rows]
        
        return {"isValid": True, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar los ejercicios: {e}")
    finally:
        conn.close()



@router.get("/ejercicios/{id_ejercicio}", tags=["Ejercicios"])
def obtener_detalle_ejercicio(id_ejercicio: str):
    """
    Obtiene el detalle de un ejercicio por su ID.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                E.id_ejercicio, E.nombre_ejercicio, E.descripcion, E.imagen, E.id_grupo_muscular, 
                G.nombre_grupo_muscular, E.id_tipo_ejercicio, TE.nombre_tipo_ejercicio, 
                E.dificultad, E.equipamiento_necesario, E.descripcion_ejecucion, 
                E.errores_comunes, E.repeticiones_recomendadas, E.series_recomendadas, 
                E.tiempo_bajo_tension_recomendado, E.descanso_entre_series_recomendado, 
                E.carga_recomendada, E.beneficios, E.precauciones
            FROM tb_ejercicio E
            INNER JOIN tb_tipo_ejercicio TE ON E.id_tipo_ejercicio = TE.id_tipo_ejercicio
            INNER JOIN tb_grupo_muscular G ON E.id_grupo_muscular = G.id_grupo_muscular
            WHERE E.id_ejercicio = ?
        """, (id_ejercicio,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Ejercicio con id {id_ejercicio} no encontrado.")
        
        columns = [column[0] for column in cursor.description]
        content = dict(zip(columns, row))
        
        return {"isValid": True, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el detalle del ejercicio: {e}")
    finally:
        conn.close()

