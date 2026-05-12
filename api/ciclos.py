from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from schema.ciclo_schema import CicloCreate, CicloFinalizar, CicloRead, CicloUpdate
from services import ciclo_service
from utils.dependencies import get_current_user, get_db


router = APIRouter(
    prefix="/ciclos",
    tags=["ciclos"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=CicloRead, status_code=status.HTTP_201_CREATED)
def crear_ciclo(payload: CicloCreate, db: Session = Depends(get_db)) -> CicloRead:
    ciclo = ciclo_service.create_ciclo(db, payload)
    return CicloRead.model_validate(ciclo)


@router.get("/", response_model=list[CicloRead])
def listar_ciclos(db: Session = Depends(get_db)) -> list[CicloRead]:
    ciclos = ciclo_service.list_ciclos(db)
    return [CicloRead.model_validate(ciclo) for ciclo in ciclos]


@router.get("/{ciclo_id}", response_model=CicloRead)
def obtener_ciclo(ciclo_id: int, db: Session = Depends(get_db)) -> CicloRead:
    ciclo = ciclo_service.get_ciclo_or_404(db, ciclo_id)
    return CicloRead.model_validate(ciclo)


@router.put("/{ciclo_id}", response_model=CicloRead)
def actualizar_ciclo(ciclo_id: int, payload: CicloUpdate, db: Session = Depends(get_db)) -> CicloRead:
    ciclo = ciclo_service.update_ciclo(db, ciclo_id, payload)
    return CicloRead.model_validate(ciclo)


@router.patch("/{ciclo_id}/finalizar", response_model=CicloRead)
def finalizar_ciclo(ciclo_id: int, payload: CicloFinalizar, db: Session = Depends(get_db)) -> CicloRead:
    ciclo = ciclo_service.finalizar_ciclo(db, ciclo_id, payload.fecha_fin)
    return CicloRead.model_validate(ciclo)


@router.delete("/{ciclo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ciclo(ciclo_id: int, db: Session = Depends(get_db)) -> Response:
    ciclo_service.delete_ciclo(db, ciclo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
