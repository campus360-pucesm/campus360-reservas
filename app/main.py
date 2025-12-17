from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routers import health_router, recursos_router, reservas_router, checkin_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicacion"""
    # Startup
    print(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    print("Cerrando aplicacion...")


# Inicializar la aplicacion FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Modulo de Reservas de CAMPUS360
    
    Este microservicio permite a los usuarios autenticados:
    
    * **Consultar disponibilidad** de recursos del campus
    * **Reservar** salas de estudio, laboratorios, equipos, parqueaderos y cubiculos
    * **Gestionar** sus reservas (ver, cancelar)
    * **Realizar check-in** mediante codigos QR
    
    ### Tipos de Recursos
    - Salas de estudio
    - Laboratorios de computacion
    - Equipos (proyectores, laptops, camaras)
    - Estaciones de parqueadero
    - Cubiculos de biblioteca
    
    ### Autenticacion
    Todos los endpoints requieren autenticacion mediante JWT Bearer token.
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health_router)
app.include_router(recursos_router)
app.include_router(reservas_router)
app.include_router(checkin_router)


@app.get("/")
async def root():
    """Endpoint raiz - informacion del servicio"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/api/v1")
async def api_info():
    """Informacion de la API"""
    return {
        "name": "CAMPUS360 Reservas API",
        "version": "1.0.0",
        "endpoints": {
            "recursos": "/recursos",
            "reservas": "/reservas",
            "checkin": "/checkin",
            "health": "/health"
        }
    }


# Para ejecutar en desarrollo:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
