from contextlib import asynccontextmanager
from db import create_tables
from fastapi import FastAPI

from routers.collection import router as collection_router, user_events_router
from routers.attachment import router as attachment_router
from routers.category import router as category_router
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

# Include routers
app.include_router(collection_router)
app.include_router(user_events_router)
app.include_router(attachment_router)
app.include_router(category_router)

# Mount static files for uploads
mount_static_files(app)


# Add health check endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy", "message": "Memora API is running"}
