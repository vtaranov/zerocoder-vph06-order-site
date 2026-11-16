from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from app.core.database import Base, engine
from app.routes import services, applications, auth, metrics

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    yield
    engine.dispose()

app = FastAPI(title="Atelier - заявки и услуги", version="2.0.0", docs_url=None, redoc_url=None, openapi_url="/api/openapi.json", lifespan=lifespan)
app.include_router(services.router)
app.include_router(applications.router)
app.include_router(auth.router)
app.include_router(metrics.router)
if os.getenv("ENABLE_DOCS", "false").lower() == "true":
    app.mount("/api/static", StaticFiles(directory=Path(__file__).parent / "static"), name="swagger-static")
else:
    app.openapi_url = None
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != "/api/openapi.json"]

@app.get("/docs", include_in_schema=False)
def docs():
    if os.getenv("ENABLE_DOCS", "false").lower() != "true":
        from fastapi import HTTPException
        raise HTTPException(404)
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title, swagger_js_url="/api/static/swagger-ui-bundle.js", swagger_css_url="/api/static/swagger-ui.css", swagger_favicon_url="/favicon.svg")

@app.get("/api/health", tags=["Состояние"])
def health():
    with engine.connect() as conn: conn.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}

@app.exception_handler(SQLAlchemyError)
async def database_error(request, exc):
    logging.getLogger("uvicorn.error").error("Database unavailable", exc_info=exc)
    return JSONResponse(status_code=503, content={"detail": "База данных временно недоступна. Данные остались в форме - попробуйте ещё раз."})
