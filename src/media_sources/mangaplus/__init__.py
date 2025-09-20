# heavily inspired by https://github.com/hurlenko/mloader

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from mediasub import LastPullContext, PullSource

from .response_pb2 import Response

if TYPE_CHECKING:
    Response: Any

BASE_URL = "https://jumpg-webapi.tokyo-cdn.com"


@dataclass
class Chapter:
    title: str
    manga: str
    chapter_id: int
    manga_id: int

    @property
    def id(self) -> str:
        return f"mangaplus-{self.manga_id}-{self.chapter_id}"

    def __hash__(self) -> int:
        return hash(self.id)


class MangaPlusSource(PullSource[Chapter]):
    name = "MangaPlus"

    def __init__(self, titles_ids: list[int], shared_client: bool = False, timeout: int | None = None):
        super().__init__(shared_client=shared_client, timeout=timeout)
        self.titles_ids = titles_ids

    async def pull(self, last_pull_ctx: LastPullContext | None = None) -> set[Chapter]:
        chapters: set[Chapter] = set()
        for title_id in self.titles_ids:
            response = await self.client.get(f"{BASE_URL}/api/title_detailV3", params={"title_id": title_id})
            manga = Response.FromString(response.content).success.title_detail_view
            for group in manga.chapter_list_group:
                for chapter in group.last_chapter_list:
                    print(chapter)
                    chapter = Chapter(
                        title=chapter.sub_title,
                        manga=manga.title.name,
                        manga_id=manga.title.title_id,
                        chapter_id=chapter.chapter_id,
                    )
                    chapters.add(chapter)

        return chapters


# async def download_chapter(client: AsyncClient, chapter: Chapter, path: Path | None = None):
#     url = f"{BASE_URL}/api{chapter.chapter_download}"

#     response = await client.get(url, timeout=60)
#     if response.status_code != 200:
#         raise ValueError(f"Failed to download chapter {chapter.chapter}: {response.status_code}")

#     if path is None:
#         path = Path(".") / "downloads" / chapter.manga / f"c{chapter.chapter}.cbz"
#     path.parent.mkdir(parents=True, exist_ok=True)

#     async with aiofiles.open(path, "wb") as f:
#         await f.write(response.content)
