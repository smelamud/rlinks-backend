from typing import List

import db


def create_short_url(cursor: db.GraphCursor, name: str, url: str):
    cursor.execute(
        """
        MERGE (:ShortUrl {name: $name})-[:REFERS]->(:Document)
              <-[:POINTS_TO]-(:Bookmark {url: $url})
        """,
        {
            "name": name,
            "url": url,
        }
    )


def find_short_url_by_bookmark_url(cursor: db.GraphCursor, url: str) -> str | None:
    existing_names = cursor.query(
        """
        MATCH (s:ShortUrl)-[:REFERS]->(:Document)<-[:POINTS_TO]-(:Bookmark {url: $url})
        RETURN s.name
        """,
        {
            "url": url,
        }
    )
    existing_name = existing_names[0] if existing_names else None
    return existing_name


def find_bookmark_url_by_short_url(cursor: db.GraphCursor, name: str) -> str | None:
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
    return target_url


def delete_bookmark_by_url(cursor: db.GraphCursor, url: str):
    cursor.execute(
        """
        MATCH (b:Bookmark {url: $url})
        DETACH DELETE b
        """,
        {
            "url": url,
        }
    )


def find_alternative_bookmark_urls_by_short_url(
        cursor: db.GraphCursor, name: str
) -> List[str]:
    return cursor.query(
        """
        MATCH (:ShortUrl {name: $name})-[:REFERS]->(d:Document)-[:TAGGED_BY]->(:Tag)
              <-[:TAGGED_BY]-(ad:Document)<-[:POINTS_TO]-(b:Bookmark)
        RETURN b.url
        """,
        {
            "name": name,
        }
    )
