import uuid
from typing import Annotated

from fastapi import Depends, APIRouter
from pydantic import BaseModel

import db
from db.bookmarks import find_short_url_by_bookmark_url, create_short_url

router = APIRouter(prefix="/api/bookmark")
DependsGraphCursor = Annotated[db.GraphCursor, Depends(db.use_graph_cursor)]


class Bookmark(BaseModel):
    url: str


class ShortUrl(BaseModel):
    url: str


@router.post("")
def register_bookmark(bookmark: Bookmark, cursor: DependsGraphCursor) -> ShortUrl:
    existing_name = find_short_url_by_bookmark_url(cursor, bookmark.url)
    if existing_name:
        return ShortUrl(url=f"/{existing_name}")

    name = str(uuid.uuid4())
    create_short_url(cursor, name, bookmark.url)

    return ShortUrl(url=f"/{name}")
