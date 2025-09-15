import uuid
from typing import Annotated, List

from fastapi import Depends, APIRouter
from pydantic import BaseModel

import db
from db.bookmarks import find_short_url_by_bookmark_url, create_short_url
from db.tags import tag_document, is_document_tagged, create_tag_if_absent

router = APIRouter(prefix="/api/bookmark")
DependsGraphCursor = Annotated[db.GraphCursor, Depends(db.use_graph_cursor)]


class Bookmark(BaseModel):
    url: str
    tags: List[str] = []


class ShortUrl(BaseModel):
    url: str


@router.post("")
def register_bookmark(bookmark: Bookmark, cursor: DependsGraphCursor) -> ShortUrl:
    short_name = find_short_url_by_bookmark_url(cursor, bookmark.url)
    if not short_name:
        short_name = str(uuid.uuid4())
        create_short_url(cursor, short_name, bookmark.url)

    for tag in bookmark.tags:
        create_tag_if_absent(cursor, tag)
        if not is_document_tagged(cursor, bookmark.url, tag):
            tag_document(cursor, bookmark.url, tag)

    return ShortUrl(url=f"/{short_name}")
