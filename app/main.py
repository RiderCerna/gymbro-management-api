from fastapi import FastAPI
from routes import operacion
from routes import ejemplo

app = FastAPI(
    title="Titulo API",
    description="API",
    version="2.0.0"
)

origins = ["*"]

app.include_router(operacion.router)
app.include_router(ejemplo.router)
