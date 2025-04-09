from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn 
import os 
from endpoints import files

def create_app() -> FastAPI:
    app = FastAPI(
        title="File Processor API",
        description="API for processing files",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True, 
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(files.router, prefix="/files", tags=["files"])

    @app.get('/health')
    async def health_check():
        from core.db import get_db
        db = get_db()
        db_status = "connected" if db else "not connected"
        return {
            "status": "healthy" if db is not None else "unhealthy",
            "database": db_status,
        }
    

    return app



app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)