from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import api_router
from utils.database import Base, engine

# Importación necesaria para registrar los modelos en metadata.
import models.biometria  # noqa: F401
import models.ciclo  # noqa: F401
import models.ciclo_estanque  # noqa: F401
import models.estanque  # noqa: F401
import models.usuario  # noqa: F401


app = FastAPI(title="Sistema de Control de Cultivo de Camarón")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(api_router)
