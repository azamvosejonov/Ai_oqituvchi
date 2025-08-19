import sys
from pathlib import Path
import inspect
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent
# sys.path.append(str(ROOT_DIR)) # This is redundant and causes issues with uvicorn

import uvicorn
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from pathlib import Path
import os
from fastapi.routing import APIRoute
import redis.asyncio as redis
from contextlib import asynccontextmanager

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.limiter import limiter
from app.db.session import SessionLocal
from app.db.initial_data import init_db
from app import schemas

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager. Runs startup and shutdown events.
    """
    logger.info("Starting up...")

    # Seed DB in a background thread to avoid blocking startup
    if not settings.TESTING:
        def _seed_db():
            try:
                logger.info("DB seeding started...")
                db = SessionLocal()
                init_db(db)
                logger.info("DB seeding finished.")
            except Exception as e:
                logger.exception(f"DB seeding error: {e}")

        try:
            from threading import Thread
            Thread(target=_seed_db, daemon=True).start()
        except Exception as e:
            logger.exception(f"Failed to start DB seeding thread: {e}")
    else:
        logger.info("TESTING mode detected - skipping DB seeding.")

    # Resolve forward references in Pydantic models
    try:
        schemas.User.model_rebuild()
        schemas.Course.model_rebuild()
        schemas.Lesson.model_rebuild()
        logger.info("Models rebuilt.")
    except Exception as e:
        logger.exception(f"Model rebuild error: {e}")

    logger.info("Startup complete.")
    yield
    logger.info("Shutting down...")

# Conditionally add rate limiting middleware if not in testing mode
if not settings.TESTING:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="""
        # O'quv Platformasi API
        
        Ushbu API orqali quyidagi imkoniyatlardan foydalanishingiz mumkin:
        
        - **AI yordamchisi** bilan suhbatlashing
        - **Ovozli suhbat** orqali talaffuzingizni yaxshilang
        - **Darsliklar** va **mashqlar** bilan shug'ulling
        - **Obuna** va profilni boshqaring
        
        ## Avtorizatsiya
        
        API dan foydalanish uchun avtorizatsiyadan o'tishingiz kerak. Buning uchun:
        
        1. `/api/v1/login/access-token` endpoint'iga POST so'rovi yuboring:
           ```json
           {
               "username": "foydalanuvchi",
               "password": "parol"
           }
           ```
        2. Qaytgan `access_token` ni `Authorization` sarlavhasida ishlating:
           ```
           Authorization: Bearer <access_token>
           ```
        
        ## Xatolik Kodlari
        
        - `400` - Noto'g'ri so'rov
        - `401` - Avtorizatsiyadan o'tilmagan
        - `403` - Ruxsat etilmagan
        - `404` - Topilmadi
        - `422` - Validatsiya xatosi
        - `429` - Juda ko'p so'rovlar
        - `500` - Server xatosi
        """,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=None,  # Disable default docs
        redoc_url=None,  # Disable default redoc
        contact={
            "name": "O'quv Platformasi Yordam",
            "url": "https://oquv-platforma.uz/contact",
            "email": "support@oquv-platforma.uz",
        },
        license_info={
            "name": "Proprietary",
            "url": "https://oquv-platforma.uz/license",
        },
        lifespan=lifespan,
    )
else:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="""
        # O'quv Platformasi API
        
        Ushbu API orqali quyidagi imkoniyatlardan foydalanishingiz mumkin:
        
        - **AI yordamchisi** bilan suhbatlashing
        - **Ovozli suhbat** orqali talaffuzingizni yaxshilang
        - **Darsliklar** va **mashqlar** bilan shug'ulling
        - **Obuna** va profilni boshqaring
        
        ## Avtorizatsiya
        
        API dan foydalanish uchun avtorizatsiyadan o'tishingiz kerak. Buning uchun:
        
        1. `/api/v1/login/access-token` endpoint'iga POST so'rovi yuboring:
           ```json
           {
               "username": "foydalanuvchi",
               "password": "parol"
           }
           ```
        2. Qaytgan `access_token` ni `Authorization` sarlavhasida ishlating:
           ```
           Authorization: Bearer <access_token>
           ```
        
        ## Xatolik Kodlari
        
        - `400` - Noto'g'ri so'rov
        - `401` - Avtorizatsiyadan o'tilmagan
        - `403` - Ruxsat etilmagan
        - `404` - Topilmadi
        - `422` - Validatsiya xatosi
        - `429` - Juda ko'p so'rovlar
        - `500` - Server xatosi
        """,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=None,  # Disable default docs
        redoc_url=None,  # Disable default redoc
        contact={
            "name": "O'quv Platformasi Yordam",
            "url": "https://oquv-platforma.uz/contact",
            "email": "support@oquv-platforma.uz",
        },
        license_info={
            "name": "Proprietary",
            "url": "https://oquv-platforma.uz/license",
        },
        lifespan=lifespan,
    )

# Create static directory if it doesn't exist
static_dir = Path("app/static")
static_dir.mkdir(exist_ok=True, parents=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "app/static")), name="static")

# Mount uploads (for user-uploaded files like profile images)
uploads_dir = Path(settings.UPLOAD_DIR)
uploads_dir.mkdir(exist_ok=True, parents=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_rate_limiter(app: FastAPI):
    """Add rate limiting middleware to the application."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)


app.include_router(api_router, prefix=settings.API_V1_STR)


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Clean up the login form in the schema by finding the correct component schema
    path = "/api/v1/login/access-token"
    if path in openapi_schema["paths"]:
        try:
            # Get the reference to the actual schema
            ref = openapi_schema["paths"][path]["post"]["requestBody"]["content"]["application/x-www-form-urlencoded"]["schema"]["$ref"]
            schema_name = ref.split('/')[-1]
            
            # Modify the component schema
            component_schema = openapi_schema["components"]["schemas"][schema_name]
            component_schema['properties'] = {
                'username': component_schema['properties']['username'],
                'password': component_schema['properties']['password'],
            }
            component_schema['required'] = ['username', 'password']
        except KeyError as e:
            print(f"Could not clean up login form, schema structure might have changed: {e}")

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# PWA routes
@app.get("/service-worker.js", include_in_schema=False)
async def get_service_worker():
    return FileResponse(
        "app/static/sw.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )

@app.get("/offline", response_class=HTMLResponse, include_in_schema=False)
async def offline_page():
    return FileResponse("app/static/offline.html")

@app.get("/manifest.json", include_in_schema=False)
async def get_manifest():
    return FileResponse("app/static/manifest.json", media_type="application/manifest+json")

@app.get("/", include_in_schema=False)
async def read_root(request: Request):
    # Check if the request is from a browser (not API)
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        # Serve the PWA entry point if exists, else return JSON fallback
        index_path = Path("app/static/index.html")
        if index_path.exists():
            return FileResponse(str(index_path))
        # Fallback to API response if index.html doesn't exist
        return JSONResponse({"message": "O'quv Platformasiga xush kelibsiz!"})
    
    return {"message": "O'quv Platformasiga xush kelibsiz!"}

from fastapi.openapi.docs import get_swagger_ui_html

# Custom Swagger UI with auto-authorization
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = f"{root_path}{app.openapi_url}"
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <title>{app.title} - Swagger UI</title>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            const ui = SwaggerUIBundle({{
                url: '{openapi_url}',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                requestInterceptor: (req) => {{
                    return req;
                }},
                responseInterceptor: (res) => {{
                    if (res.url.includes("/api/v1/login/access-token") && res.ok) {{
                        try {{
                            const token = JSON.parse(res.text).access_token;
                            if (token) {{
                                console.log("Access token found, auto-authorizing...");
                                ui.preauthorizeApiKey("Bearer", `Bearer ${{token}}`);
                                console.log("Authorization completed.");
                            }}
                        }} catch (e) {{
                            console.error("Failed to parse token or authorize:", e);
                        }}
                    }}
                    return res;
                }}
            }})
        </script>
    </body>
    </html>
    """)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "message": "Service is running"}

# Version endpoint
@app.get("/version", tags=["info"])
async def get_version():
    return {"version": "1.0.0", "status": "ok"}

if __name__ == "__main__":
    # Add rate limiter only when running the app directly
    add_rate_limiter(app)
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
