from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from schema.estanque_schema import EstanqueCreate, EstanqueRead, EstanqueUpdate
from services import estanque_service
from utils.dependencies import get_current_user, get_db


router = APIRouter(
    prefix="/estanques",
    tags=["estanques"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=EstanqueRead, status_code=status.HTTP_201_CREATED)
def crear_estanque(payload: EstanqueCreate, db: Session = Depends(get_db)) -> EstanqueRead:
    estanque = estanque_service.create_estanque(db, payload)
    return EstanqueRead.model_validate(estanque)


@router.get("/", response_model=list[EstanqueRead])
def listar_estanques(db: Session = Depends(get_db)) -> list[EstanqueRead]:
    estanques = estanque_service.list_estanques(db)
    return [EstanqueRead.model_validate(estanque) for estanque in estanques]


@router.get("/{estanque_id}", response_model=EstanqueRead)
def obtener_estanque(estanque_id: int, db: Session = Depends(get_db)) -> EstanqueRead:
    estanque = estanque_service.get_estanque_or_404(db, estanque_id)
    return EstanqueRead.model_validate(estanque)


@router.put("/{estanque_id}", response_model=EstanqueRead)
def actualizar_estanque(
    estanque_id: int,
    payload: EstanqueUpdate,
    db: Session = Depends(get_db),
) -> EstanqueRead:
    estanque = estanque_service.update_estanque(db, estanque_id, payload)
    return EstanqueRead.model_validate(estanque)


@router.delete("/{estanque_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_estanque(estanque_id: int, db: Session = Depends(get_db)) -> Response:
    estanque_service.delete_estanque(db, estanque_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
