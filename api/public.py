from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import RedirectResponse, FileResponse

import db
from db.bookmarks import find_bookmark_url_by_short_url

router = APIRouter()
DependsGraphCursor = Annotated[db.GraphCursor, Depends(db.use_graph_cursor)]


@router.get("/")
def root():
    return FileResponse("static/index.html")


@router.get("/{name}")
def short_url(name: str, cursor: DependsGraphCursor):
    target_url = find_bookmark_url_by_short_url(cursor, name)
    if not target_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=target_url, status_code=307)
