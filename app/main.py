import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1 import admin, auth, categories, images, logs, products, storage, tasks, video, videos
from app.api.deps import get_current_user
from app.config import get_settings
from app.models.database import User
from app.core.backup import backup_loop
from app.core.static_files import CacheControlStaticFiles
from app.db.init import init_db
from app.db.session import init_engine
from app.middleware.csrf import CSRFMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.web_auth_redirect import WebAuthRedirectMiddleware
from app.core.product_storage import get_products_upload_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = init_engine()
    backup_stop: asyncio.Event | None = None
    backup_task: asyncio.Task | None = None
    if engine:
        await init_db(engine)

    # Ensure upload directories exist before mounting static routes.
    get_products_upload_dir()

    settings = get_settings()
    if engine and settings.BACKUP_ENABLED:
        backup_stop = asyncio.Event()
        backup_task = asyncio.create_task(backup_loop(backup_stop))
    yield
    if backup_stop:
        backup_stop.set()
    if backup_task:
        backup_task.cancel()
        with suppress(asyncio.CancelledError):
            await backup_task
    if engine:
        await engine.dispose()


app = FastAPI(
    title="AI Video Generator API",
    description="统一的AI视频生成接口，支持Sora2、Veo、Seedance等模型",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CSRFMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(WebAuthRedirectMiddleware)

app.include_router(video.router, prefix="/api/v1", tags=["Video Generation"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Task Management"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(categories.router, prefix="/api/v1", tags=["Data"])
app.include_router(logs.router, prefix="/api/v1", tags=["Data"])
app.include_router(videos.router, prefix="/api/v1", tags=["Videos"])
app.include_router(images.router, prefix="/api/v1", tags=["Images"])
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(storage.router, prefix="/api/v1", tags=["Storage"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])

# Mount static files
app.mount("/static", CacheControlStaticFiles(directory="app/static"), name="static")
app.mount("/uploads", CacheControlStaticFiles(directory="app/static/uploads", check_dir=False), name="uploads")


@app.get("/")
async def root():
    return FileResponse("app/static/app.html")


@app.get("/login")
async def login_page():
    return FileResponse("app/static/login.html")


@app.get("/storage")
async def storage_page():
    return FileResponse("app/static/storage.html")


@app.get("/video")
async def video_page():
    return FileResponse("app/static/video.html")


@app.get("/dashboard")
async def dashboard_redirect():
    from starlette.responses import RedirectResponse
    return RedirectResponse(url="/video")


@app.get("/admin")
async def admin_page(user: User = Depends(get_current_user)):
    if not user.is_admin:
        from starlette.responses import RedirectResponse

        return RedirectResponse(url="/?error=Admin%20access%20required", status_code=303)
    return FileResponse("app/static/admin.html")


@app.get("/image")
async def image_page(user: User = Depends(get_current_user)):
    return FileResponse("app/static/image.html")


@app.get("/products")
async def products_page(user: User = Depends(get_current_user)):
    return FileResponse("app/static/products.html")


@app.get("/ecommerce-image")
async def ecommerce_image_page(user: User = Depends(get_current_user)):
    return FileResponse("app/static/ecommerce-image.html")


@app.get("/image-generate")
async def image_generate_page(user: User = Depends(get_current_user)):
    return FileResponse("app/static/image-generate.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico", media_type="image/x-icon")
