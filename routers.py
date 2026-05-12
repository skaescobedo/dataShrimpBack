from fastapi import APIRouter

from api import auth, biometrias, ciclo_estanques, ciclos, estanques, usuarios


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(estanques.router)
api_router.include_router(ciclos.router)
api_router.include_router(ciclo_estanques.router)
api_router.include_router(biometrias.router)
