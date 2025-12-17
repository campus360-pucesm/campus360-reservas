from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Información del servicio
    APP_NAME: str = "CAMPUS360 - Módulo de Reservas"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str  # anon/public key
    SUPABASE_SERVICE_KEY: str = ""  # service role key (opcional, para operaciones admin)
    
    # JWT (debe coincidir con el módulo de autenticación)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    
    # Configuración de reservas
    MAX_RESERVAS_POR_DIA: int = 3  # Máximo de reservas por usuario por día
    TIEMPO_MINIMO_RESERVA_MINUTOS: int = 30
    TIEMPO_MAXIMO_RESERVA_HORAS: int = 4
    ANTICIPACION_MINIMA_MINUTOS: int = 15  # Mínimo tiempo de anticipación para reservar
    ANTICIPACION_MAXIMA_DIAS: int = 30  # Máximo días de anticipación
    
    # Check-in
    VENTANA_CHECKIN_MINUTOS: int = 15  # Minutos antes/después de la hora de reserva
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración cacheada"""
    return Settings()
