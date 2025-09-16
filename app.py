import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api import public, bookmark
from config import config

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(bookmark.router)
app.include_router(public.router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.http_host,
        port=config.http_port,
        log_level="info",
    )
