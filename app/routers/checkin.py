from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
import math

from app.dependencies import get_supabase, get_current_user, require_admin
from app.services import CheckinService, QRService
from app.schemas import (
    CheckinCreate,
    CheckinResponse,
    CheckinValidacion,
    RecursoQRCreate,
    RecursoQRResponse,
    MensajeResponse
)

router = APIRouter(
    prefix="/checkin",
    tags=["check-in"]
)


@router.post("/", response_model=dict)
async def realizar_checkin(
    datos: CheckinCreate,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Realiza el check-in de una reserva mediante codigo QR.
    
    RF3.1 - Permite realizar check-in escaneando un codigo QR.
    RF3.2 - Valida la identidad del usuario.
    RF3.3 - Verifica que exista una reserva activa.
    RF3.4 - Registra la hora y validez del check-in.
    RF3.6 - Impide check-ins duplicados.
    """
    service = CheckinService(db)
    
    checkin, error = await service.realizar_checkin(
        reserva_id=datos.reserva_id,
        usuario_id=current_user["id"],
        qr_token=datos.qr_token,
        dispositivo_info=datos.dispositivo_info
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return {
        "message": "Check-in realizado exitosamente",
        "checkin": checkin
    }


@router.get("/validar/{reserva_id}")
async def validar_checkin(
    reserva_id: str,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Valida si se puede realizar check-in sin ejecutarlo.
    
    RF3.5 - Muestra mensajes de error cuando no se puede realizar check-in.
    """
    service = CheckinService(db)
    resultado = await service.validar_checkin(reserva_id, current_user["id"])
    
    return resultado


@router.get("/historial")
async def obtener_historial_checkins(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene el historial de check-ins del usuario.
    """
    service = CheckinService(db)
    checkins, total = await service.obtener_historial_checkins(
        current_user["id"],
        page,
        page_size
    )
    
    return {
        "items": checkins,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0
    }


# ============================================
# ENDPOINTS DE QR (ADMINISTRATIVOS)
# ============================================

@router.post("/qr/generar", response_model=dict)
async def generar_qr_recurso(
    datos: RecursoQRCreate,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(require_admin)
):
    """
    Genera un codigo QR para un recurso (solo admin).
    
    RNF1.2 - Los QR contienen informacion encriptada/tokens temporales.
    """
    service = QRService(db)
    qr, error = await service.generar_qr_recurso(
        datos.recurso_id,
        datos.duracion_horas
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return {
        "message": "Codigo QR generado exitosamente",
        "qr": qr
    }


@router.get("/qr/recurso/{recurso_id}")
async def obtener_qr_recurso(
    recurso_id: str,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(require_admin)
):
    """
    Obtiene el codigo QR activo de un recurso (solo admin).
    """
    try:
        response = db.table("recursos_qr").select("*")\
            .eq("recurso_id", recurso_id)\
            .eq("activo", True)\
            .single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay QR activo para este recurso"
            )
        
        return response.data
        
    except Exception as e:
        if "404" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay QR activo para este recurso"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
