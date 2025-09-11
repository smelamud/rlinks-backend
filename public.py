from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import RedirectResponse

import db

router = APIRouter()
DependsGraphCursor = Annotated[db.GraphCursor, Depends(db.use_graph_cursor)]


@router.get("/{name}")
def short_url(name: str, cursor: DependsGraphCursor):
    urls = cursor.query(
        """
        MATCH (:ShortUrl {name: $name})-[:REFERS]->(:Document)
              <-[:POINTS_TO]-(b:Bookmark)
        RETURN b.url
        LIMIT 1
        """,
        {
            "name": name,
        }
    )
    target_url = urls[0] if urls else None
    if not target_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=target_url, status_code=307)
