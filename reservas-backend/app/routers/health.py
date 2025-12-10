from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def check():
    return {"status": "ok", "module": "reservas"}
