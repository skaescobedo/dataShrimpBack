from fastapi import APIRouter, Depends, Response, status, Query
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
from models.usuario import Usuario
from schema.biometria_schema import BiometriaCreate, BiometriaRead, BiometriaUpdate, BiometriaPredictionResponse
from services import biometria_service
from utils.dependencies import get_current_user, get_db


router = APIRouter(
    prefix="/biometrias",
    tags=["biometrias"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=BiometriaRead, status_code=status.HTTP_201_CREATED)
def crear_biometria(
    payload: BiometriaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> BiometriaRead:
    biometria = biometria_service.create_biometria(db, payload, current_user.id_usuario)
    return BiometriaRead.model_validate(biometria)


@router.get("/", response_model=list[BiometriaRead])
def listar_biometrias(db: Session = Depends(get_db)) -> list[BiometriaRead]:
    biometrias = biometria_service.list_biometrias(db)
    return [BiometriaRead.model_validate(item) for item in biometrias]


@router.get("/ciclo-estanque/{ciclo_estanque_id}", response_model=list[BiometriaRead])
def listar_biometrias_por_ciclo_estanque(
    ciclo_estanque_id: int, db: Session = Depends(get_db)
) -> list[BiometriaRead]:
    biometrias = biometria_service.list_biometrias_by_ciclo_estanque(db, ciclo_estanque_id)
    return [BiometriaRead.model_validate(item) for item in biometrias]


@router.get("/predecir/{ciclo_estanque_id}", response_model=BiometriaPredictionResponse)
def predecir_biometria(
    ciclo_estanque_id: int,
    semanas: int = Query(4, description="Número de semanas a proyectar"),
    db: Session = Depends(get_db)
) -> BiometriaPredictionResponse:
    resultado = biometria_service.predict_biometria_global(db, ciclo_estanque_id, semanas)
    return BiometriaPredictionResponse(**resultado)


@router.get("/{biometria_id}", response_model=BiometriaRead)
def obtener_biometria(biometria_id: int, db: Session = Depends(get_db)) -> BiometriaRead:
    biometria = biometria_service.get_biometria_or_404(db, biometria_id)
    return BiometriaRead.model_validate(biometria)


@router.put("/{biometria_id}", response_model=BiometriaRead)
def actualizar_biometria(
    biometria_id: int, payload: BiometriaUpdate, db: Session = Depends(get_db)
) -> BiometriaRead:
    biometria = biometria_service.update_biometria(db, biometria_id, payload)
    return BiometriaRead.model_validate(biometria)


@router.delete("/{biometria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_biometria(biometria_id: int, db: Session = Depends(get_db)) -> Response:
    biometria_service.delete_biometria(db, biometria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/import", status_code=status.HTTP_201_CREATED)
async def importar_biometrias(archive:UploadFile = File(...), db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)) -> Response:
    print("Archivo recibido:", archive.filename)
    biometrias = await biometria_service.processBiometriaFromExcel(db, archive)
    created_biometrias = []
    for biometria in biometrias:
        created_biometria = biometria_service.create_biometria(db, biometria, current_user.id_usuario)
        created_biometrias.append(created_biometria)
    return created_biometrias
