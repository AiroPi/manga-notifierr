import asyncio
from pathlib import Path

from mediasub import MediaSub

from media_sources.fmteam import Chapter as FMTeamChapter, FMTeamSource, download_chapter as fmteam_download_chapter
from media_sources.mangamoins import (
    Chapter as MangaMoinsChapter,
    MangaMoinsSource,
    download_chapter as mangamoins_download_chapter,
)
from notifier import notify

from environment import DATABASE_PATH

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
    path = Path("./library") / chapter.manga / f"c{chapter.chapter}.cbz"

    if path.exists():
        print(f"Chapter {chapter.chapter} already exists in {path}. Skipping download.")
        return

    # await mangamoins_download_chapter(src.client, chapter, path=path)


if __name__ == "__main__":
    asyncio.run(media.start())
