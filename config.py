import os
import pathlib
import tomllib
from typing import Optional

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


config = load_config()
