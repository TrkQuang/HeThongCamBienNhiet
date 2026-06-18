import logging, os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth_routes import router as auth_router
from .device_routes import router as device_router
from .routes import router
from .settings_routes import router as settings_router

def _cau_hinh_logging():
    dd = os.getenv("LOG_CONFIG", "config/logging.yaml")
    try:
        import yaml
        from logging.config import dictConfig
        dictConfig(yaml.safe_load(open(dd, "r", encoding="utf-8")))
    except: logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

def create_app() -> FastAPI:
    load_dotenv()
    _cau_hinh_logging()
    app = FastAPI(title="HeThongCamBienNhiet API")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(router)
    app.include_router(auth_router)
    app.include_router(device_router)
    app.include_router(settings_router)
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("api.app:app", host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", "5000")), reload=os.getenv("API_DEBUG", "true").lower() == "true")