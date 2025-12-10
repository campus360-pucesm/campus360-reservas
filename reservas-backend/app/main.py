from fastapi import FastAPI
from app.routers import health, reservas
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Campus360 Reservas API")

# CORS para permitir acceso del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego lo restringimos si quieres
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(health.router)
app.include_router(reservas.router)

@app.get("/")
def root():
    return {"message": "API de Reservas funcionando"}
