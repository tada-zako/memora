from db import create_tables
from router import app

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables when the application starts.
    """
    create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
