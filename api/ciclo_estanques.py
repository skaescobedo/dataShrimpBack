from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from schema.ciclo_estanque_schema import (
    CicloEstanqueCreate,
    CicloEstanqueRead,
    CicloEstanqueUpdate,
)
from services import ciclo_estanque_service
from utils.dependencies import get_current_user, get_db


router = APIRouter(
    prefix="/ciclo-estanques",
    tags=["ciclo_estanques"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=CicloEstanqueRead, status_code=status.HTTP_201_CREATED)
def asociar_estanque_a_ciclo(
    payload: CicloEstanqueCreate, db: Session = Depends(get_db)
) -> CicloEstanqueRead:
    ciclo_estanque = ciclo_estanque_service.create_ciclo_estanque(db, payload)
    return CicloEstanqueRead.model_validate(ciclo_estanque)


@router.get("/ciclo/{ciclo_id}", response_model=list[CicloEstanqueRead])
def listar_estanques_por_ciclo(ciclo_id: int, db: Session = Depends(get_db)) -> list[CicloEstanqueRead]:
    asociaciones = ciclo_estanque_service.list_by_ciclo(db, ciclo_id)
    return [CicloEstanqueRead.model_validate(item) for item in asociaciones]


@router.get("/estanque/{estanque_id}", response_model=list[CicloEstanqueRead])
def listar_ciclos_por_estanque(
    estanque_id: int, db: Session = Depends(get_db)
) -> list[CicloEstanqueRead]:
    asociaciones = ciclo_estanque_service.list_by_estanque(db, estanque_id)
    return [CicloEstanqueRead.model_validate(item) for item in asociaciones]


@router.get("/{ciclo_estanque_id}", response_model=CicloEstanqueRead)
def obtener_ciclo_estanque(ciclo_estanque_id: int, db: Session = Depends(get_db)) -> CicloEstanqueRead:
    ciclo_estanque = ciclo_estanque_service.get_ciclo_estanque_or_404(db, ciclo_estanque_id)
    return CicloEstanqueRead.model_validate(ciclo_estanque)


@router.put("/{ciclo_estanque_id}", response_model=CicloEstanqueRead)
def actualizar_ciclo_estanque(
    ciclo_estanque_id: int,
    payload: CicloEstanqueUpdate,
    db: Session = Depends(get_db),
) -> CicloEstanqueRead:
    ciclo_estanque = ciclo_estanque_service.update_ciclo_estanque(db, ciclo_estanque_id, payload)
    return CicloEstanqueRead.model_validate(ciclo_estanque)


@router.patch("/{ciclo_estanque_id}/finalizar", response_model=CicloEstanqueRead)
def finalizar_ciclo_estanque(ciclo_estanque_id: int, db: Session = Depends(get_db)) -> CicloEstanqueRead:
    ciclo_estanque = ciclo_estanque_service.finalizar_ciclo_estanque(db, ciclo_estanque_id)
    return CicloEstanqueRead.model_validate(ciclo_estanque)


@router.delete("/{ciclo_estanque_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ciclo_estanque(ciclo_estanque_id: int, db: Session = Depends(get_db)) -> Response:
    ciclo_estanque_service.delete_ciclo_estanque(db, ciclo_estanque_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
