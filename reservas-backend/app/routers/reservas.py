from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.get("/")
def listar_reservas():
    return [
        {
            "id": 1,
            "usuario": 10,
            "recurso": "Sala 101",
            "fecha": datetime.now().isoformat(),
            "estado": "VIGENTE"
        }
    ]
