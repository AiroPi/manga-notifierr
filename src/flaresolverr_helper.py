from typing import TypedDict

import httpx

from environment import FLARESOLVERR_HOST, FLARESOLVERR_PORT


class FlaresolverrSolution(TypedDict):
    url: str
    status: int
    headers: dict[str, str]
    response: str
    cookies: list[dict[str, str | int]]
    userAgent: str


class FlareSolverrError(Exception):
    pass


async def get(url: str, session: str, client: httpx.AsyncClient | None = None) -> FlaresolverrSolution:
    if client is None:
        client = httpx.AsyncClient()

    headers = {"Content-Type": "application/json"}
    data = {"session": session, "cmd": "request.get", "url": url, "maxTimeout": 60000}
    raw_response = await client.post(
        f"http://{FLARESOLVERR_HOST}:{FLARESOLVERR_PORT}/v1", headers=headers, json=data, timeout=70
    )
    response = raw_response.json()
    if response["status"] != "ok":
        raise FlareSolverrError("Challenge not solved for some reasons")

    return response["solution"]
