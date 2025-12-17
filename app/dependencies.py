from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from supabase import create_client, Client
from typing import Optional
from datetime import datetime

from app.config import get_settings

settings = get_settings()

# Cliente de Supabase (singleton)
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Obtiene el cliente de Supabase"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    return _supabase_client


# Esquema de seguridad Bearer
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_supabase)
) -> dict:
    """
    Valida el token JWT y retorna la información del usuario actual.
    Esta función se integra con el módulo de autenticación.
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token JWT
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Verificar que el token no haya expirado
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except JWTError:
        raise credentials_exception
    
    # Obtener información del usuario desde Supabase
    try:
        response = db.table("users").select("*").eq("id", user_id).single().execute()
        user = response.data
        
        if user is None:
            raise credentials_exception
            
        return {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "role": user.get("role", "estudiante")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información del usuario: {str(e)}"
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Verifica que el usuario esté activo"""
    # Aquí podrías agregar validaciones adicionales
    # Por ejemplo, verificar si el usuario está bloqueado
    return current_user


async def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Requiere que el usuario sea administrador"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user


async def require_docente_or_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Requiere que el usuario sea docente o administrador"""
    if current_user.get("role") not in ["admin", "docente"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere permisos de docente o administrador"
        )
    return current_user
