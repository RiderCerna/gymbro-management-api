from fastapi import FastAPI
from routes import usuarios
from routes import ejercicios
from routes import rutinas

app = FastAPI(
    title="API Gymbro",
    description="API",
    version="2.0.0"
)

origins = ["*"]

app.include_router(usuarios.router)
app.include_router(ejercicios.router)
app.include_router(rutinas.router)

