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
from media_sources.mangaplus import Chapter as MangaPlusChapter, MangaPlusSource
from notifier import notify_new_chapter

media = MediaSub(
    db_path=DATABASE_PATH,
)


@media.sub_to(FMTeamSource())
async def on_fmteam_chapter(src: FMTeamSource, chapter: FMTeamChapter):
    pings = {
        "Berserk": "1391138266685636679",
        "Kingdom": "1391138396872773632",
        "Vinland Saga": "1418756769718599740",
    }

    print(f"New chapter available: {chapter.manga} - {chapter.chapter} ({chapter.title})")
    await notify_new_chapter(
        manga=chapter.manga,
        chapter=f"{chapter.chapter} - {chapter.title}",
        url="https://fmteam.fr/",
        ping=[pings[chapter.manga]],
    )

    path = Path("./library") / chapter.manga / f"c{chapter.chapter}.cbz"

    if path.exists():
        print(f"Chapter {chapter.chapter} already exists in {path}. Skipping download.")
        return

    await fmteam_download_chapter(src.client, chapter, path=path)


@media.sub_to(MangaMoinsSource())
async def on_mangamoins_chapter(src: MangaMoinsSource, chapter: MangaMoinsChapter):
    pings = {
        "OP": "1391138368838172682",
    }

    print(f"New chapter available: {chapter.manga} - {chapter.chapter}")
    await notify_new_chapter(
        manga=chapter.manga,
        chapter=chapter.chapter,
        url=f"https://mangamoins.shaeishu.co/?scan={chapter.code}{chapter.chapter}",
        ping=[pings[chapter.code]],
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


@media.sub_to(
    MangaPlusSource(
        [
            700014,  # Boruto : TWO BLUE VORTEX
            700006,  # Black Clover
        ]
    )
)
async def on_mangaplus_chapter(src: MangaPlusSource, chapter: MangaPlusChapter):
    pings = {
        700014: "1418758598640668786",
        700006: "1418756725594390658",
    }

    print(f"New chapter available: {chapter.manga} - {chapter.title}")
    await notify_new_chapter(
        manga=chapter.manga,
        chapter=chapter.title,
        url=f"https://mangaplus.shueisha.co.jp/viewer/{chapter.chapter_id}",
        ping=[pings[chapter.manga_id]],
    )


if __name__ == "__main__":
    asyncio.run(media.start())
