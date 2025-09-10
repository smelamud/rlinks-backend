import os

import uvicorn
from fastapi import FastAPI

import api

app = FastAPI()
app.include_router(api.router)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "8000")),
        log_level="info",
    )
