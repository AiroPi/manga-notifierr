from os import environ
from pathlib import Path

FLARESOLVERR_HOST = environ.get("FLARESOLVERR_HOST") or "localhost"
FLARESOLVERR_PORT = environ.get("FLARESOLVERR_PORT") or 8191

DOWNLOAD_PATH = Path(environ.get("DOWNLOAD_PATH") or "./data/download")
LIBRARY_PATH = Path(environ.get("LIBRARY_PATH") or "./data/library")

DATABASE_PATH = environ.get("DATABASE_PATH") or "./data/db.sqlite"

PING_ALL = "1418756697777901620"
