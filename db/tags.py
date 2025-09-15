import db


def create_tag_if_absent(cursor: db.GraphCursor, name: str):
    cursor.execute(
        """
        MERGE (:Tag {name: $name})
        """,
        {
            "name": name,
        }
    )


def tag_document(cursor: db.GraphCursor, url: str, tag_name: str):
    cursor.execute(
        """
        MATCH (t:Tag {name: $tag_name}),
              (d:Document)<-[:POINTS_TO]-(:Bookmark {url: $url})
        CREATE (d)-[:TAGGED_BY]->(t)
        """,
        {
            "tag_name": tag_name,
            "url": url,
        }
    )


def is_document_tagged(cursor: db.GraphCursor, url: str, tag_name: str) -> bool:
    results = cursor.query(
        """
        MATCH (t:Tag {name: $tag_name})<-[:TAGGED_BY]-(d:Document)
              <-[:POINTS_TO]-(:Bookmark {url: $url})
        RETURN count(t) > 0
        """,
        {
            "tag_name": tag_name,
            "url": url,
        }
    )
    return results[0] if results else False
