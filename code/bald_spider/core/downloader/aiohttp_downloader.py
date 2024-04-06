
from typing import Optional

from bald_spider import Response
from aiohttp import ClientSession, TCPConnector, BaseConnector, ClientTimeout, ClientResponse,TraceConfig
from bald_spider.utils.log import get_logger
from bald_spider.core.downloader import DownloaderBase

class AioDownloader(DownloaderBase):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.session: Optional[ClientSession] = None
        self.connector: Optional[BaseConnector] = None
        self._verify_ssl: Optional[bool] = None
        self._timeout: Optional[ClientTimeout] = None
        self.trace_config:Optional[TraceConfig] = None
        self.request_method = {
            "get": self._get,
            "post": self._post,
        }

        self._use_session:Optional[bool] = None

    def open(self):
        super().open()
        request_time = self.crawler.settings.getint("REQUEST_TIMEOUT")
        self._timeout = ClientTimeout(total=request_time)
        self._verify_ssl = self.crawler.settings.getbool("VERIFY_SSL")
        self._use_session = self.crawler.settings.getbool("USE_SESSION")
        self.trace_config = TraceConfig()
        self.trace_config.on_request_start.append(self.request_start)
        if self._use_session:
            self.connector = TCPConnector(verify_ssl=self._verify_ssl)
            # 存在一个待解决的问题：当前我们的下载使用的都是同一个session,在一些场景中，需要重启新session下载
            self.session = ClientSession(connector=self.connector, timeout=self._timeout,trace_configs=[self.trace_config])

    async def download(self, request) -> Optional[Response]:
        # 实际的下载
        try:
            # 配置参数中使用统一个session的话，使用self.session
            if self._use_session:
                response = await self.send_request(self.session,request)
                body = await response.content.read()
            # 不是的话，我们需要按照上面的方式进行创建session
            else:
                connector = TCPConnector(verify_ssl=self._verify_ssl)
                async with ClientSession(
                        connector=connector, timeout=self._timeout,trace_configs=[self.trace_config]
                ) as session:
                    response = await self.send_request(session,request)
                    body = await response.content.read()
        except Exception as exc:
            self.logger.error(f"Error druing request:{exc}")
            return None
        else:
            # 临时性代码
            self.crawler.stats.inc_value("response_received_count")
        return self.structure_response(request,response,body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=request.url,
            headers=dict(response.headers),
            status=response.status,
            body=body,
            request=request
        )

    async def send_request(self,session,request) -> ClientResponse:
        return await self.request_method[request.method.lower()](session,request)

    @staticmethod
    async def _get(session,request) -> ClientResponse:
        response = await session.get(
            request.url, headers=request.headers,
            cookies=request.cookies, proxy=request.proxy
        )
        return response

    @staticmethod
    async def _post(session,request) -> ClientResponse:
        response = await session.post(
            request.url, data=request.body, headers=request.headers,
            cookies=request.cookies, proxy=request.proxy
        )
        return response

    async def request_start(self,_session,_trace_config_ctx,params):
        # 在trace_config中进行设置，我们在请求开始之前就会调用当前的方法
        self.logger.debug(f"request downloading:{params.url}，method:{params.method}")

    async def close(self):
        if self.connector:
            await self.connector.close()
        if self.session:
            await self.session.close()