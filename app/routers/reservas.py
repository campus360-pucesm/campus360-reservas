from fastapi import APIRouter

router = APIRouter(
    prefix="/reservas",
    tags=["reservas"]
)

@router.get("/")
def listar_reservas():
    return {"message": "Lista de reservas"}

@router.post("/")
def crear_reserva():
    return {"message": "Reserva creada"}
