from fastapi import APIRouter, Depends
from supabase import Client
from datetime import datetime

from app.dependencies import get_supabase
from app.config import get_settings

router = APIRouter(
    prefix="/health",
    tags=["health"]
)

settings = get_settings()


@router.get("/")
async def health_check():
    """Verifica que el servicio esté funcionando"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/db")
async def database_check(db: Client = Depends(get_supabase)):
    """Verifica la conexión a la base de datos"""
    try:
        # Intentar una consulta simple
        response = db.table("recursos").select("id").limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/ready")
async def readiness_check(db: Client = Depends(get_supabase)):
    """Verifica que el servicio esté listo para recibir peticiones"""
    checks = {
        "database": False,
        "config": True
    }
    
    try:
        db.table("recursos").select("id").limit(1).execute()
        checks["database"] = True
    except:
        pass
    
    all_healthy = all(checks.values())
    
    return {
        "ready": all_healthy,
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
