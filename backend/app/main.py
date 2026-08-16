from fastapi import FastAPI

from app.modules.crm.router import router as crm_router
from app.modules.hrm.router import router as hrm_router
from app.modules.marketing.router import router as marketing_router
from app.modules.payments.router import router as payments_router
from app.modules.training.router import router as training_router
from app.modules.travel.router import router as travel_router
from app.modules.visa.router import router as visa_router

app = FastAPI(title="ZACMA Platform API")

for router in [
    crm_router,
    hrm_router,
    marketing_router,
    payments_router,
    training_router,
    travel_router,
    visa_router,
]:
    app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
