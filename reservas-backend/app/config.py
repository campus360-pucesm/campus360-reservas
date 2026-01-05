"""
Configuracion del microservicio
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuracion de la aplicacion"""
    
    # Informacion del servicio
    APP_NAME: str = "CAMPUS360 - Sistema de Reservas"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # JWT (para integracion con modulo de autenticacion)
    JWT_SECRET_KEY: str = "clave_secreta_temporal"
    JWT_ALGORITHM: str = "HS256"
    
    # Configuracion de reservas
    MAX_RESERVAS_POR_DIA: int = 5
    ANTICIPACION_MINIMA_MINUTOS: int = 15
    ANTICIPACION_MAXIMA_DIAS: int = 30
    
    # Check-in
    VENTANA_CHECKIN_MINUTOS: int = 15
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()