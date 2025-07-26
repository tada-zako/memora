from contextlib import asynccontextmanager
from db import create_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.collection import router as collection_router, collections_router
from routers.attachment import router as attachment_router
from routers.category import router as category_router
from routers.auth import router as auth_router
from routers.static import mount_static_files


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan event handler.
    """
    await create_tables()
    yield


app = FastAPI(
    title="Memora API", description="Collection management API", lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许前端开发服务器访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(collection_router, prefix="/api/v1")
app.include_router(collections_router, prefix="/api/v1")
app.include_router(attachment_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")

# Mount static files for uploads
mount_static_files(app)


# Add root endpoint
@app.get("/api/v1/health")
async def root():
    """
    Root endpoint
    """
    return {"message": "Memora API", "status": "running", "version": "1.0.0"}


# Add health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy", "message": "Memora API is running"}
