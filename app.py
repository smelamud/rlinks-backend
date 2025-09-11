import os

import uvicorn
from fastapi import FastAPI

from api import public, bookmark

app = FastAPI()
app.include_router(bookmark.router)
app.include_router(public.router)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "8000")),
        log_level="info",
    )
