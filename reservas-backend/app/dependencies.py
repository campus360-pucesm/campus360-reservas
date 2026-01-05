"""
Dependencias del microservicio
Conexion a Supabase
"""
from supabase import create_client, Client
from typing import Optional

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