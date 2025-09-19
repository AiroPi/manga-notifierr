from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import aiofiles
from httpx import AsyncClient
from lxml import etree
from lxml.cssselect import CSSSelector
from mediasub import LastPullContext, PullSource

import flaresolverr_helper

if TYPE_CHECKING:
    from lxml.etree import _Element as Element  # pyright: ignore[reportPrivateUsage]

SCAN_REF_RE = re.compile(r"(\D+)(.+)")

# also used as filter
CODE2NAME = {
    "OP": "One Piece",
}


@dataclass
class Chapter:
    code: str
    chapter: str

    @property
    def manga(self) -> str:
        return CODE2NAME[self.code]

    @property
    def id(self) -> str:
        return f"mangamoins-{self.manga}-{self.chapter}"

    def __hash__(self) -> int:
        return hash(self.id)


class MangaMoinsSource(PullSource[Chapter]):
    name = "MangaMoins"
    default_timeout = 600

    def __init__(self, shared_client: bool = False, timeout: int | None = None):
        super().__init__(shared_client=shared_client, timeout=timeout)
        self.cookies: list[dict[str, Any]] = []
        self.user_agent: str | None = None

    async def pull(self, last_pull_ctx: LastPullContext | None = None) -> set[Chapter]:
        url = "https://mangamoins.shaeishu.co/"
        response = await flaresolverr_helper.get(url, "mangamoins", self.client)

        parsed = etree.fromstring(response["response"], parser=etree.HTMLParser())
        selector = CSSSelector(".sortie")
        selected = selector(parsed)

        if TYPE_CHECKING:
            selected = cast(list[Element], selected)

        chapters: set[Chapter] = set()
        for chapter_div in selected:
            a_element = chapter_div.find("a")
            if a_element is None:
                print("No <a> element found in chapter_div")
                continue
            href = a_element.attrib["href"]

            if TYPE_CHECKING:
                href = cast(str, href)
            scan_ref = href.split("=")[1]

            match = SCAN_REF_RE.match(scan_ref)
            if match is None:
                print(f"No match found for scan_ref: {scan_ref}")
                continue

            code, chapter = match.groups()
            if code not in CODE2NAME:
                continue

            chapter_obj = Chapter(code=code, chapter=chapter)

            chapters.add(chapter_obj)

        return chapters


async def download_chapter(
    client: AsyncClient,
    chapter: Chapter,
    path: Path,
) -> None:
    """
    Download the chapter and save it to a file.
    """
    print(f"Downloading {chapter.manga} ({chapter.code}) - Chapter {chapter.chapter}...")
    url = f"https://mangamoins.shaeishu.co/download/?scan={chapter.code}{chapter.chapter}"

    response = await client.get(url, timeout=60)
    if response.status_code != 200:
        raise ValueError(f"Failed to download chapter {chapter}: {response.status_code}")

    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path, "wb") as f:
        await f.write(response.content)

    print(f"Downloaded {path}")
