from __future__ import annotations

import os
import pathlib
from typing import Optional, Mapping, Any, Iterable

import tomllib
import psycopg


# Default locations to look for the configuration file.
# You can override via the environment variable APP_CONFIG_TOML.
_DEFAULT_CONFIG_PATHS: list[pathlib.Path] = [
    pathlib.Path(os.getenv("APP_CONFIG_TOML", "")).expanduser(),
    pathlib.Path("config.toml"),
    pathlib.Path.home() / ".config" / "rlinks-backend" / "config.toml",
]


def load_config(path: Optional[str | os.PathLike[str]] = None) -> dict:
    """
    Load application configuration from a TOML file.

    Search order (first existing wins):
      1) explicit 'path' argument
      2) $APP_CONFIG_TOML
      3) ./config.toml
      4) ~/.config/rlinks-backend/config.toml
    """
    candidates: list[pathlib.Path] = []
    if path is not None:
        candidates.append(pathlib.Path(path).expanduser())
    candidates.extend([p for p in _DEFAULT_CONFIG_PATHS if str(p)])

    tried: list[str] = []
    for p in candidates:
        if not p:
            continue
        tried.append(str(p))
        if p.exists() and p.is_file():
            with p.open("rb") as f:
                return tomllib.load(f)

    raise FileNotFoundError(
        "Configuration file not found. Looked in: " + ", ".join(tried)
    )


def _db_settings(cfg: Optional[dict] = None) -> dict:
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
    if cfg is None:
        cfg = load_config()

    db = dict(cfg.get("database") or {})
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


def connect(cfg: Optional[dict] = None) -> psycopg.Connection:
    """
    Create a new psycopg connection using settings from the configuration.
    """
    settings = _db_settings(cfg)
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

    return psycopg.connect(**kwargs)


def execute(sql: str, params: Optional[Mapping[str, Any] | Iterable[Any]] = None) -> int:
    """
    Execute a statement (INSERT/UPDATE/DELETE/DDL). Returns affected rowcount.
    """
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or None)
            conn.commit()
            return cur.rowcount or 0


def query(sql: str, params: Optional[Mapping[str, Any] | Iterable[Any]] = None) -> list[tuple]:
    """
    Execute a SELECT and return all rows as a list of tuples.
    """
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or None)
            if cur.description:
                return cur.fetchall()
            return []
