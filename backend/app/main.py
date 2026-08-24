"""ZACMA Platform API — FastAPI application entry point.

Registers all core shared engines, domain routers, dynamic module system,
middleware, CORS, and storage upload pipeline.
"""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.middleware import AuthMiddleware, AuditLoggingMiddleware

# Shared Core & Domain Routers
from app.modules.admin.router import router as admin_router
from app.modules.admin.reviews_router import router as reviews_router
from app.modules.auth.router import router as auth_router
from app.modules.client_portal.router import router as client_portal_router
from app.modules.crm.router import router as crm_router
from app.modules.people.router import router as people_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.dynamic.router import router as dynamic_router
from app.modules.payments.router import router as payments_router
from app.modules.storage.router import router as storage_router
from app.modules.students.router import router as students_router
from app.modules.support.router import router as support_router
from app.modules.travel.router import router as travel_router
from app.modules.visa.router import router as visa_router
from app.modules.software.router import router as software_router
from app.modules.automation.router import router as automation_router

# Legacy Routers for backwards compatibility
from app.modules.hrm.router import router as hrm_router
from app.modules.marketing.router import router as marketing_router
from app.modules.training.router import router as training_router

# Optional AI Gateway Router
try:
    from ai.gateway import router as ai_router
    _ai_available = True
except Exception:
    _ai_available = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("zacma.api")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Zacma Multi-Tenant Business Management Platform for Training, Visa, Travel, and Customer Support.",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuditLoggingMiddleware)
app.add_middleware(AuthMiddleware)

# ---------------------------------------------------------------------------
# Static Uploads Mount
# ---------------------------------------------------------------------------

try:
    from pathlib import Path
    upload_path = Path(settings.storage_upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")
except Exception as e:
    logger.warning("Could not mount static uploads directory: %s", e)

# ---------------------------------------------------------------------------
# Routers Registration
# ---------------------------------------------------------------------------

ROUTERS = [
    auth_router,
    client_portal_router,
    admin_router,
    reviews_router,
    people_router,
    crm_router,
    payments_router,
    students_router,
    visa_router,
    travel_router,
    software_router,
    support_router,
    dynamic_router,
    storage_router,
    dashboard_router,
    training_router,
    hrm_router,
    marketing_router,
    automation_router,
]

for router in ROUTERS:
    app.include_router(router, prefix="/api/v1")

if _ai_available:
    app.include_router(ai_router, prefix="/api/v1")
    logger.info("AI gateway router mounted at /api/v1/ai")


# ---------------------------------------------------------------------------
# Background Telegram Bot Polling Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Verify live Telegram bot and register Google Pub/Sub listeners on startup."""
    try:
        from app.services.event_bus import event_bus
        from app.services.pubsub_service import PubSubService
        event_bus.subscribe("*", PubSubService.event_bus_listener)
        logger.info("PubSubService registered to EventBus for cloud event orchestration.")
    except Exception as ps_err:
        logger.debug("PubSub registration notice: %s", ps_err)

    if not os.getenv("PYTEST_CURRENT_TEST") and not os.getenv("TESTING"):
        try:
            from app.services.telegram_bot_service import TelegramPaymentBotService
            if settings.telegram_bot_token:
                bot_info = TelegramPaymentBotService.get_bot_info()
                if bot_info.get("ok"):
                    logger.info("Telegram Bot verified: @%s", bot_info.get("result", {}).get("username"))
                else:
                    logger.info("Telegram Bot service ready for @ZacmaBusinessSupportAI_bot.")
        except Exception as e:
            logger.warning("Telegram bot startup notice: %s", e)


# ---------------------------------------------------------------------------
# Health & Status
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": "Zacma Business Management Platform",
        "telegram_bot": "@ZacmaBusinessSupportAI_bot",
    }

