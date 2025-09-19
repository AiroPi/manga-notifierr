import asyncio
from pathlib import Path

import httpx
from mediasub import MediaSub

from environment import DATABASE_PATH, LIBRARY_PATH
from media_sources.fmteam import Chapter as FMTeamChapter, FMTeamSource, download_chapter as fmteam_download_chapter
from media_sources.mangamoins import (
    Chapter as MangaMoinsChapter,
    MangaMoinsSource,
    download_chapter as mangamoins_download_chapter,
)
from notifier import notify

media = MediaSub(
    db_path=DATABASE_PATH,
)


@media.sub_to(FMTeamSource())
async def on_fmteam_chapter(src: FMTeamSource, chapter: FMTeamChapter):
    print(f"New chapter available: {chapter.manga} - {chapter.chapter} ({chapter.title})")
    await notify(
        f"Nouveau chapitre de {chapter.manga} : {chapter.chapter} - {chapter.title}\nLisez-le sur https://fmteam.fr"
    )

    path = Path("./library") / chapter.manga / f"c{chapter.chapter}.cbz"

    if path.exists():
        print(f"Chapter {chapter.chapter} already exists in {path}. Skipping download.")
        return

    await fmteam_download_chapter(src.client, chapter, path=path)


@media.sub_to(MangaMoinsSource())
async def on_chapter(src: MangaMoinsSource, chapter: MangaMoinsChapter):
    print(f"New chapter available: {chapter.manga} - {chapter.chapter}")
    await notify(
        f"Nouveau chapitre de {chapter.manga} : {chapter.chapter}\nLisez-le sur https://mangamoins.shaeishu.co/"
    )
    path = LIBRARY_PATH / chapter.manga / f"c{chapter.chapter}.cbz"

    if path.exists():
        print(f"Chapter {chapter.chapter} already exists in {path}. Skipping download.")
        return

    client = httpx.AsyncClient()
    if src.cookies:
        client.cookies = {c["name"]: c["value"] for c in src.cookies}
    if src.user_agent:
        client.headers["user-agent"] = src.user_agent

    await mangamoins_download_chapter(client, chapter, path=path)


if __name__ == "__main__":
    asyncio.run(media.start())
