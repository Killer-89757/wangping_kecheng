from typing import Optional

from bald_spider import Response
import httpx
from bald_spider.core.downloader import DownloaderBase


class HttpxDownloader(DownloaderBase):
    def __init__(self, crawler):
        super().__init__(crawler)

        self._client: Optional[httpx.AsyncClient] = None
        self._timeout: Optional[httpx.Timeout] = None

    def open(self):
        super().open()
        request_time = self.crawler.settings.getint("REQUEST_TIMEOUT")
        self._timeout = httpx.Timeout(timeout=request_time)

    async def download(self, request) -> Optional[Response]:
        # 实际的下载
        try:
            proxies = request.proxy
            async with httpx.AsyncClient(timeout=self._timeout, proxies=proxies) as client:
                self.logger.debug(f"request downloading:{request.url}，method:{request.method}")
                response = await client.request(
                    request.method, request.url, headers=request.headers, cookies=request.cookies, data=request.body
                )
                body = await response.aread()
        except Exception as exc:
            self.logger.error(f"Error druing request:{exc}")
            return None
        return self.structure_response(request, response, body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=request.url,
            headers=dict(response.headers),
            status=response.status_code,
            body=body,
            request=request
        )
