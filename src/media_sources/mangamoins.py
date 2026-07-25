from __future__ import annotations

import zipfile
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

from mediasub import LastPullContext, PullSource

import flaresolverr_helper

if TYPE_CHECKING:
    pass  # pyright: ignore[reportPrivateUsage]

logger = getLogger(__name__)


@dataclass
class Chapter:
    code: str
    chapter: str
    manga: str
    slug: str

    @property
    def id(self) -> str:
        return f"mangamoins-{self.code}-{self.chapter}"

    def __hash__(self) -> int:
        return hash(self.id)


class MangaMoinsSource(PullSource[Chapter]):
    name = "MangaMoins"
    default_timeout = 1200

    def __init__(self, manga_slugs: list[str], shared_client: bool = False, timeout: int | None = None):
        super().__init__(shared_client=shared_client, timeout=timeout)
        self.cookies: list[dict[str, Any]] = []
        self.user_agent: str | None = None
        self.manga_slugs = manga_slugs

    async def pull(self, last_pull_ctx: LastPullContext | None = None) -> set[Chapter]:
        url = "https://mangamoins.com/"
        await self.client.get(url)  # get a cookie
        print(self.client.cookies)
        response = await self.client.get(f"{url}api/v1/mangas?limit=5", headers={"Referer": "https://mangamoins.com/"})
        values = response.json()
        print(values)
        return {
            Chapter(code=manga["mangaSlug"], chapter=manga["chapitre"], manga=manga["title"], slug=manga["slug"])
            for manga in values["data"]
            if manga["mangaSlug"] in self.manga_slugs
        }

    async def post_callback(self):
        await flaresolverr_helper.destroy_session("mangamoins", self.client)

    async def download_chapter(
        self,
        chapter: Chapter,
        path: Path,
        cookies: dict[str, str] | None = None,
        user_agent: str | None = None,
    ) -> None:
        print("TODO")
        """
        Download the chapter and save it to a file.
        """
        logger.info(f"Downloading {chapter.manga} #{chapter.chapter} in {path}...")
        url = f"https://mangamoins.com/api/v1/scan?slug={chapter.slug}"
        response = await self.client.get(url, headers={"Referer": "https://mangamoins.com"})
        infos = response.json()
        page_base_url = infos["pagesBaseUrl"].replace("bztmrkeiyoushi", "")
        page_number = infos["pageNumbers"]

        # not asyncio but I don't care
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(page_number):
                img = await self.client.get(f"{page_base_url}{i + 1:02d}.webp")
                zip_file.writestr(f"{i + 1:02d}.webp", img.content)

        logger.info(f"{chapter.manga} #{chapter.chapter} downloaded in {path} successfully !")
