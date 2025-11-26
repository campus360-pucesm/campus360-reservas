from fastapi import FastAPI
from app.routers import health, reservas

app = FastAPI(
    title="CAMPUS360 - Reservas",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(reservas.router)

@app.get("/")
def root():
    return {"message": "CAMPUS360 microservice running"}
