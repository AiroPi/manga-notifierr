import os

from httpx import AsyncClient

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


async def notify(message: str) -> None:
    """Send a notification to Discord using Webhook"""
    async with AsyncClient() as client:
        await client.post(WEBHOOK_URL, json={"content": message})
