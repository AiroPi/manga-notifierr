from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

import aiofiles
from httpx import AsyncClient
from mediasub import LastPullContext, PullSource

logger = getLogger(__name__)

FILTER = {"Berserk", "Kingdom", "Vinland Saga"}
BASE_URL = "https://fmteam.fr"


@dataclass
class Chapter:
    chapter: str
    title: str
    manga: str
    chapter_download: str

    @property
    def id(self) -> str:
        return f"fmteam-{self.manga}-{self.chapter}"

    def __hash__(self) -> int:
        return hash(self.id)


class FMTeamSource(PullSource[Chapter]):
    name = "FMTeam"

    async def pull(self, last_pull_ctx: LastPullContext | None = None) -> set[Chapter]:
        response = await self.client.get(f"{BASE_URL}/api/comics")

        if response.status_code != 200:
            raise RuntimeError(f"Request failed, status code: {response.status_code}")

        content = response.json()

        chapters: set[Chapter] = set()
        for manga in content["comics"]:
            if manga["title"] not in FILTER:
                logger.debug(f"Skipped manga {manga['title']}.")
                continue

            last_chapter = manga["last_chapter"]
            if last_chapter is None:
                logger.warning(f"No last chapter found for {manga['name']}")
                continue

            chapter_nb = last_chapter["chapter"]
            if last_chapter.get("subchapter"):
                chapter_nb += f".{last_chapter['subchapter']}"

            chapter = Chapter(
                chapter=chapter_nb,
                title=last_chapter["title"],
                manga=manga["title"],
                chapter_download=last_chapter["chapter_download"],
            )

            chapters.add(chapter)

        _log_chapters = "\n - ".join(f"{chapter.manga} : #{chapter.chapter} {chapter.title}" for chapter in chapters)
        logger.info(f"Found {len(chapters)} chapters:\n - {_log_chapters}")

        return chapters


async def download_chapter(client: AsyncClient, chapter: Chapter, path: Path | None = None):
    logger.info(f"Downloading {chapter.manga} : #{chapter.chapter} {chapter.title} in {path}...")
    url = f"{BASE_URL}/api{chapter.chapter_download}"

    response = await client.get(url, timeout=60)
    if response.status_code != 200:
        raise ValueError(f"Failed to download chapter {chapter.chapter}: {response.status_code}")

    if path is None:
        path = Path(".") / "downloads" / chapter.manga / f"c{chapter.chapter}.cbz"
    path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(path, "wb") as f:
        await f.write(response.content)
    logger.info(f"{chapter.manga} : #{chapter.chapter} {chapter.title} downloaded in {path} successfully !")
