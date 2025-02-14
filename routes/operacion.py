from fastapi import APIRouter

router = APIRouter()


@router.get("/test", tags=["TEST"])
def ingrese_nombre(nombre: str):
    saludo = f"Hola {nombre} este es un endpoint de prueba"
    return {"respuesta":saludo}