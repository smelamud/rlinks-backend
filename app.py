import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api import public, bookmark

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(bookmark.router)
app.include_router(public.router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "8000")),
        log_level="info",
    )
