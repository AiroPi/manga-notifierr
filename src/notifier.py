import os

from httpx import AsyncClient

from environment import PING_ALL

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


async def notify_new_chapter(manga: str, chapter: str, url: str, extra_pings: str | list[str] | None = None):
    pings = [PING_ALL]
    if extra_pings:
        if isinstance(extra_pings, list):
            pings.extend(extra_pings)
        else:
            pings.append(extra_pings)

    message = (
        "**Un nouveau chapitre est disponible !**\n\n"
        f"__Manga__: {manga}\n"
        f"__Chapitre__: {chapter}\n\n"
        f"Lisez le dès à présent ici : <{url}>\n"
        f"<@&{'> <@&'.join(pings)}>"
    )

    await notify(message)


async def notify(message: str) -> None:
    """Send a notification to Discord using Webhook"""
    async with AsyncClient() as client:
        await client.post(WEBHOOK_URL, json={"content": message})
