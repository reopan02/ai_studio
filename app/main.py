from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1 import auth, image_proxy, images, product_recognition, storage, tasks, uploads, video
from app.config import get_settings
from app.core.static_files import CacheControlStaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


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

app.include_router(video.router, prefix="/api/v1", tags=["Video Generation"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Task Management"])
app.include_router(image_proxy.router, prefix="/api/v1", tags=["Images"])
app.include_router(product_recognition.router, prefix="/api/v1", tags=["Products"])
app.include_router(uploads.router, prefix="/api/v1", tags=["Uploads"])
app.include_router(images.router, prefix="/api/v1", tags=["User Images"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(storage.router, prefix="/api/v1", tags=["Storage"])

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
async def admin_page():
    from fastapi import HTTPException, status

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Admin UI removed. Use Supabase Studio instead.",
    )


@app.get("/image")
async def image_page():
    return FileResponse("app/static/image.html")


@app.get("/products")
async def products_page():
    return FileResponse("app/static/products.html")


@app.get("/ecommerce-image")
async def ecommerce_image_page():
    return FileResponse("app/static/ecommerce-image.html")


@app.get("/image-generate")
async def image_generate_page():
    return FileResponse("app/static/image-generate.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico", media_type="image/x-icon")
