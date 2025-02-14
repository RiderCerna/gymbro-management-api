from fastapi import FastAPI, APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from db.db import get_db_connection
from collections import defaultdict


router = APIRouter()


@router.get("/estadisticas_grafico_barras", tags=["Estadísticas"])
def obtener_progreso(id_usuario: str, id_ejercicio: int):

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT e.nombre_ejercicio, de.peso, en.fecha
            FROM 
                tb_detalle_entrenamiento de
            JOIN 
                tb_entrenamiento en ON de.id_entrenamiento = en.id_entrenamiento
            JOIN 
                tb_ejercicio e ON de.id_ejercicio = e.id_ejercicio
            WHERE 
                en.id_usuario = ?
            AND 
                de.id_ejercicio = ?
        """, (id_usuario, id_ejercicio))

        resultados = cursor.fetchall()

        # Convertir los resultados en una lista de objetos ProgresoEjercicio
        progreso_dict = defaultdict(list)
        for row in resultados:
            progreso_dict[row[0]].append({"peso": row[1], "fecha": row[2]})

        return dict(progreso_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {e}")

    finally:
        conn.close()

@router.get("/estadisticas_grafico_circulo", tags=["Estadísticas"])
def obtener_porcentaje_grupo_muscular(id_usuario: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    
    cursor = conn.cursor()
    try:
        # Obtener todos los ejercicios del usuario
        cursor.execute("""
            SELECT 
                gm.nombre_grupo_muscular,
                de.id_ejercicio
            FROM 
                tb_detalle_entrenamiento de
            JOIN 
                tb_entrenamiento en ON de.id_entrenamiento = en.id_entrenamiento
            JOIN 
                tb_ejercicio e ON de.id_ejercicio = e.id_ejercicio
            JOIN 
                tb_grupo_muscular gm ON e.id_grupo_muscular = gm.id_grupo_muscular
            WHERE
                en.id_usuario = ?;
        """, (id_usuario,))

        resultados = cursor.fetchall()

        if not resultados:
            return {"usuario": id_usuario, "estadisticas": []}

        # Contar ejercicios por grupo muscular
        conteo_por_grupo = defaultdict(int)
        for grupo_muscular, _ in resultados:
            conteo_por_grupo[grupo_muscular] += 1

        # Total de ejercicios realizados por el usuario
        total_ejercicios = sum(conteo_por_grupo.values())

        # Calcular porcentajes en Python
        estadisticas = [
            {
                "grupo_muscular": grupo,
                "total_ejercicios": count,
                "porcentaje": round((count * 100.0 / total_ejercicios), 2)
            }
            for grupo, count in conteo_por_grupo.items()
        ]

        return {"usuario": id_usuario, "estadisticas": estadisticas}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {e}")

    finally:
        conn.close()

@router.get("/peso_promedio_ejercicio", tags=["Estadísticas"])
def obtener_peso_promedio(id_usuario: str, id_grupo_muscular: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")
    
    cursor = conn.cursor()
    try:
        # Obtener datos sin cálculos SQL avanzados
        cursor.execute("""
            SELECT e.nombre_ejercicio, de.peso
            FROM 
                tb_detalle_entrenamiento de
            JOIN 
                tb_entrenamiento en ON de.id_entrenamiento = en.id_entrenamiento
            JOIN 
                tb_ejercicio e ON de.id_ejercicio = e.id_ejercicio
            WHERE 
                en.id_usuario = ? 
            AND 
                e.id_grupo_muscular = ?
        """, (id_usuario, id_grupo_muscular))

        resultados = cursor.fetchall()
        if not resultados:
            return {"usuario": id_usuario, "grupo_muscular": id_grupo_muscular, "estadisticas": []}

        # Calcular el promedio de peso por ejercicio en Python
        peso_por_ejercicio = defaultdict(list)
        for ejercicio, peso in resultados:
            peso_por_ejercicio[ejercicio].append(peso)

        # Obtener el promedio de cada ejercicio
        estadisticas = [
            {
                "ejercicio": ejercicio,
                "peso_promedio": round(sum(pesos) / len(pesos), 2)
            }
            for ejercicio, pesos in peso_por_ejercicio.items()
        ]

        # Ordenar de mayor a menor peso promedio
        estadisticas.sort(key=lambda x: x["peso_promedio"], reverse=True)

        return {
            "usuario": id_usuario,
            "grupo_muscular": id_grupo_muscular,
            "estadisticas": estadisticas
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {e}")

    finally:
        conn.close()

