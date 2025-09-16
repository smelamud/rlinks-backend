from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse, FileResponse

import db
from db.bookmarks import find_bookmark_url_by_short_url, \
    find_alternative_bookmark_urls_by_short_url

router = APIRouter()
templates = Jinja2Templates(directory="templates")
DependsGraphCursor = Annotated[db.GraphCursor, Depends(db.use_graph_cursor)]


@router.get("/")
def root():
    return FileResponse("static/index.html")


@router.get("/{name}")
def short_url(name: str, request: Request, cursor: DependsGraphCursor):
    target_url = find_bookmark_url_by_short_url(cursor, name)
    if not target_url:
        alternatives = find_alternative_bookmark_urls_by_short_url(cursor, name)
        return templates.TemplateResponse(
            "alternatives.html",
            {
                "request": request,
                "name": name,
                "alternatives": alternatives,
            },
            status_code=200,
        )
    return RedirectResponse(url=target_url, status_code=307)
