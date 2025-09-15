from __future__ import annotations

import json
from typing import Optional, Mapping, Any, LiteralString

import psycopg
from psycopg import sql

from config import config


def _db_settings(config: dict) -> dict:
    """
    Extract database settings from the loaded configuration.

    Required:
      - database.name (or database.dbname)
    Optional:
      - database.host (default: localhost)
      - database.port (default: 5432)
      - database.user
      - database.password
    """
    db = config.get("database", {})
    name = db.get("name") or db.get("dbname") or db.get("database")
    if not name:
        raise ValueError(
            "Missing database name. Provide [database].name in your configuration."
        )

    host = db.get("host", "localhost")
    port = int(db.get("port", 5432))
    user = db.get("user")
    password = db.get("password")

    return {
        "host": host,
        "port": port,
        "dbname": name,
        "user": user,
        "password": password,
    }


def _connect(config: dict) -> psycopg.Connection:
    """
    Create a new psycopg connection using settings from the configuration.
    """
    settings = _db_settings(config)
    kwargs = {
        "host": settings["host"],
        "port": settings["port"],
        "dbname": settings["dbname"],
    }
    # Only include optional keys if provided
    if settings.get("user"):
        kwargs["user"] = settings["user"]
    if settings.get("password"):
        kwargs["password"] = settings["password"]

    connection = psycopg.connect(**kwargs)
    with connection.cursor() as cur:
        cur.execute("LOAD 'age'")
        cur.execute('SET search_path = ag_catalog, "$user", public')

    return connection

class GraphCursor:
    """
    A simple wrapper around psycopg.Cursor that:
      - supports 'with' statement,
      - provides convenience execute() and query() methods,
      - delegates other attributes to the underlying cursor.
    """

    def __init__(self, graph_name: str, cursor: psycopg.Cursor) -> None:
        self.graph_name = graph_name
        self._cursor = cursor

    def __enter__(self) -> "GraphCursor":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        # Always close the cursor; do not handle commit/rollback here.
        try:
            self._cursor.close()
        except Exception:
            # Avoid masking the original exception
            pass
        # Do not suppress exceptions.
        return False

    def _to_sql(self, query: LiteralString) -> sql.Composed:
        return sql.SQL(
            """
            SELECT * FROM cypher({}, $${}$$, %s::agtype)
                AS (result agtype);
            """
        ).format(self.graph_name, sql.SQL(query))

    def execute(
        self,
        query: LiteralString,
        params: Optional[Mapping[str, Any]] = None,
    ) -> int:
        """
        Execute a Cypher statement. Returns affected rowcount.
        """
        encoded_params = json.dumps(params) if params else "{}"
        self._cursor.execute(self._to_sql(query), (encoded_params,))
        return self._cursor.rowcount or 0

    def _parse_agtype(self, value: str) -> Any:
        """
        Parse AGE query result by removing type suffix and converting from JSON.
        Example: '{"name": "test"}::vertex' -> {"name": "test"}
        """
        if not value:
            return None
        # Remove type suffix if present (e.g. '::vertex', '::edge')
        if "::" in value:
            value = value.split("::", 1)[0]
        return json.loads(value)

    def query(
            self,
            query: LiteralString,
            params: Optional[Mapping[str, Any]] = None,
    ) -> list[Any]:
        """
        Execute a SELECT and return all rows as parsed Python objects.
        """
        encoded_params = json.dumps(params) if params else "{}"
        self._cursor.execute(self._to_sql(query), (encoded_params,))
        if self._cursor.description:
            return [self._parse_agtype(r[0]) for r in self._cursor.fetchall()]
        return []

    def close(self) -> None:
        """Close the underlying cursor."""
        self._cursor.close()

    def __getattr__(self, item):
        """
        Delegate unknown attributes to the underlying cursor.
        This allows access to methods like fetchone(), fetchmany(), mogrify(), etc.
        """
        return getattr(self._cursor, item)



class Graph:
    """
    A lightweight wrapper around psycopg.Connection that works with 'with' statement.

    Usage:
        with Graph(config) as g:
            rows = g.query("SELECT 1")

    The connection is always created and owned by this class.

    Configuration requirements:
      - graph_name: the name of the graph to work with (required).
    """

    def __init__(
        self,
        config: dict,
        *,
        commit_on_exit: bool = True,
    ) -> None:
        """
        Initialize Graph by creating a new connection from the provided config.
        Requires 'graph_name' to be set in the configuration.
        """
        graph_name = config.get("database", {}).get("graph_name")
        if not graph_name or not str(graph_name).strip():
            raise ValueError("Missing 'graph_name' in configuration.")
        self.graph_name: str = str(graph_name)

        self._connection: psycopg.Connection = _connect(config)
        self._commit_on_exit = commit_on_exit

    def __enter__(self) -> "Graph":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        # If an exception occurred, rollback; otherwise optionally commit.
        try:
            if exc_type is not None:
                self._connection.rollback()
            elif self._commit_on_exit:
                self._connection.commit()
        finally:
            try:
                self._connection.close()
            except Exception:
                # Ensure we don't mask the original exception during close.
                pass
        # Do not suppress exceptions.
        return False

    @property
    def connection(self) -> psycopg.Connection:
        """Access the underlying psycopg connection."""
        return self._connection

    # Common convenience methods
    def cursor(self, *args, **kwargs):
        """Return a wrapped cursor that supports query() and execute() and works with 'with'."""
        return GraphCursor(self.graph_name, self._connection.cursor(*args, **kwargs))

    def close(self) -> None:
        """Close the underlying connection."""
        self._connection.close()

    def __getattr__(self, item):
        """
        Delegate unknown attributes to the underlying connection.
        This allows access to connection attributes like .autocommit, .status, etc.
        """
        return getattr(self._connection, item)


def use_graph_cursor():
    with Graph(config) as graph:
        with graph.cursor() as cursor:
            yield cursor
