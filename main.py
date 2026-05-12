from fastapi import FastAPI

from routers import api_router
from utils.database import Base, engine

# Importación necesaria para registrar los modelos en metadata.
import models.biometria  # noqa: F401
import models.ciclo  # noqa: F401
import models.ciclo_estanque  # noqa: F401
import models.estanque  # noqa: F401
import models.usuario  # noqa: F401


app = FastAPI(title="Sistema de Control de Cultivo de Camarón")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(api_router)
