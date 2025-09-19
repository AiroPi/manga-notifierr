from os import environ

FLARESOLVERR_HOST = environ.get("FLARESOLVERR_HOST") or "flaresolverr"
FLARESOLVERR_PORT = environ.get("FLARESOLVERR_PORT") or 8191

LIBRARY_PATH = environ.get("LIBRARY_PATH") or "/data/library"
DOWNLOADS_PATH = environ.get("DOWNLOADS_PATH") or "/data/downloads"

DATABASE_PATH = environ.get("DATABASE_PATH") or "/data/db.sqlite"
