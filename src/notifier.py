import os

from httpx import AsyncClient

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


async def notify_new_chapter(manga: str, chapter: str, url: str, ping: list[str]):
    message = (
        "**Un nouveau chapitre est disponible !**\n\n"
        f"__Manga__: {manga}\n"
        f"__Chapitre__: {chapter}\n\n"
        f"Lisez le dès à présent ici : <{url}>\n"
        f"<@&{'> <@&'.join(['1418756697777901620', *ping])}"
    )

    await notify(message)


async def notify(message: str) -> None:
    """Send a notification to Discord using Webhook"""
    async with AsyncClient() as client:
        await client.post(WEBHOOK_URL, json={"content": message})
