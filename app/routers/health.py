"""
Router de Health Check
"""
from fastapi import APIRouter, Depends
from supabase import Client
from datetime import datetime

from app.dependencies import get_supabase
from app.config import get_settings

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

settings = get_settings()


@router.get("/")
async def health_check():
    """Verifica que el servicio este funcionando"""
    return {
        "status": "ok",
        "servicio": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/db")
async def database_check(db: Client = Depends(get_supabase)):
    """Verifica la conexion a la base de datos"""
    try:
        response = db.table("recursos").select("id").limit(1).execute()
        return {
            "status": "ok",
            "database": "conectada",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "desconectada",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
