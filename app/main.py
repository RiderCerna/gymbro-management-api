from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import usuarios, ejercicios,rutinas,statistics 

app = FastAPI(
    title="API Gymbro",
    description="API",
    version="2.0.0"
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(usuarios.router)
app.include_router(ejercicios.router)
app.include_router(rutinas.router)
app.include_router(statistics.router)

