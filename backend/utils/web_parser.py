import aiohttp
import asyncio
from typing_extensions import override
from .markdownit_content import MarkdownitContentMixin


class WebParser(MarkdownitContentMixin):
    async def fetch(self, url: str) -> str: ...
    async def close(self): ...


class AIOHTTPWebParser(WebParser):
    def __init__(self):
        self._session = None

    async def initialize(self):
        self._session = aiohttp.ClientSession(trust_env=True)

    @override
    async def fetch(self, url: str, timeout: float = 10) -> str:
        if not self._session:
            raise RuntimeError("Web parser not initialized. Call 'initialize' first.")
        async with self._session.get(url, timeout=timeout) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to fetch {url}, status code: {response.status}"
                )
            result = await response.text()
            markdownit_result = await asyncio.to_thread(, result)
            return markdownit_result

    @override
    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None


# global
aiohttp_web_parser = AIOHTTPWebParser()
