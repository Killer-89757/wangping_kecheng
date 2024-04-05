import asyncio
from typing import Final, Set, Optional
import httpx
import random
# 下上文管理器的包
from contextlib import asynccontextmanager
from bald_spider import Response
from aiohttp import ClientSession, TCPConnector, BaseConnector, ClientTimeout, ClientResponse,TraceConfig
from bald_spider.utils.log import get_logger


# aiohttp httpx 插件化：插拔器，即插即用
# 思路：
# 1.在Engine中需要用到fetch、idle方法，需要分别实现
# 2.我们生成的response是不同的，所以我们需要进行兼容
# 3.我们根据配置文件实现动态加载

class ActiveRequestManager:
    def __init__(self):
        self._active: Final[Set] = set()

    def add(self, request):
        # print("add", request)
        self._active.add(request)

    def remove(self, request):
        # print("remove", request)
        self._active.remove(request)

    @asynccontextmanager
    async def __call__(self, request):
        try:
            yield self.add(request)
        finally:
            self.remove(request)

    def __len__(self):
        return len(self._active)


class AioDownloader:
    def __init__(self, crawler):
        self._active = ActiveRequestManager()
        self.session: Optional[ClientSession] = None
        self.connector: Optional[BaseConnector] = None
        self._verify_ssl: Optional[bool] = None
        self._timeout: Optional[ClientTimeout] = None
        self.trace_config:Optional[TraceConfig] = None
        self.crawler = crawler
        self.request_method = {
            "get": self._get,
            "post": self._post,
        }
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get("LOG_LEVEL"))
        self._use_session:Optional[bool] = None

    def open(self):
        self.logger.info(f"{self.crawler.spider} <downloader class:{type(self).__name__}>"
                         f"<concurrency:{self.crawler.settings.getint('CONCURRENCY')}>")
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

    async def fetch(self, request) -> Optional[Response]:
        # 其实在这个地方，请求来的时候我们加入到队列中，当请求结束后，我们从队列中删除，可以使用上下文管理器来进行操作
        async with self._active(request):
            response = await self.download(request)
            return response

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


    def idle(self):
        return len(self) == 0

    def __len__(self):
        return len(self._active)

    async def close(self):
        if self.connector:
            await self.connector.close()
        if self.session:
            await self.session.close()

class HttpxDownloader:
    def __init__(self, crawler):
        self.crawler = crawler
        self._active = ActiveRequestManager()
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get("LOG_LEVEL"))

        self._client:Optional[httpx.AsyncClient] = None
        self._timeout:Optional[httpx.Timeout]= None

    def open(self):
        self.logger.info(f"{self.crawler.spider} <downloader class:{type(self).__name__}>"
                         f"<concurrency:{self.crawler.settings.getint('CONCURRENCY')}>")
        request_time = self.crawler.settings.getint("REQUEST_TIMEOUT")
        self._timeout = httpx.Timeout(timeout=request_time)

    async def fetch(self, request) -> Optional[Response]:
        # 其实在这个地方，请求来的时候我们加入到队列中，当请求结束后，我们从队列中删除，可以使用上下文管理器来进行操作
        async with self._active(request):
            response = await self.download(request)
            return response

    async def download(self, request) -> Optional[Response]:
        # 实际的下载
        try:
            proxies = request.proxy
            async with httpx.AsyncClient(timeout=self._timeout,proxies=proxies) as client:
                self.logger.debug(f"request downloading:{request.url}，method:{request.method}")
                response = await client.request(
                    request.method,request.url,headers=request.headers,cookies=request.cookies,data=request.body
                )
                body = await response.aread()
        except Exception as exc:
            self.logger.error(f"Error druing request:{exc}")
            return None
        return self.structure_response(request,response,body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=request.url,
            headers=dict(response.headers),
            status=response.status_code,
            body=body,
            request=request
        )

    def idle(self):
        return len(self) == 0

    def __len__(self):
        return len(self._active)

    async def close(self):
        pass

