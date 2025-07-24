from fastapi import FastAPI

from routers.event import router as event_router, user_events_router
from routers.attachment import router as attachment_router
from routers.static import mount_static_files

app = FastAPI(title="Memora API", description="Event management API")

# Include routers
app.include_router(event_router)
app.include_router(user_events_router)
app.include_router(attachment_router)

# Mount static files for uploads
mount_static_files(app)

# Add health check endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy", "message": "Memora API is running"}
