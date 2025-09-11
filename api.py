import uuid
from typing import Annotated

from fastapi import Depends, APIRouter
from pydantic import BaseModel

import db

router = APIRouter(prefix="/api")
DependsGraphCursor = Annotated[db.GraphCursor, Depends(db.use_graph_cursor)]


class Bookmark(BaseModel):
    url: str


class ShortUrl(BaseModel):
    url: str


@router.post("/bookmark")
def register_bookmark(bookmark: Bookmark, cursor: DependsGraphCursor) -> ShortUrl:
    existing_names = cursor.query(
        """
        MATCH (s:ShortUrl)-[:REFERS]->(:Document)<-[:POINTS_TO]-(:Bookmark {url: $url})
        RETURN s.name
        """,
        {
            "url": bookmark.url,
        }
    )
    existing_name = existing_names[0] if existing_names else None
    if existing_name:
        return ShortUrl(url=f"/{existing_name}")

    name = str(uuid.uuid4())
    cursor.execute(
        """
        MERGE (:ShortUrl {name: $name})-[:REFERS]->(:Document)
              <-[:POINTS_TO]-(:Bookmark {url: $url})
        """,
        {
            "name": name,
            "url": bookmark.url,
        }
    )

    return ShortUrl(url=f"/{name}")
