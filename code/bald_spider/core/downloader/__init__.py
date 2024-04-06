from typing import Final, Set, Optional
from contextlib import asynccontextmanager
from abc import abstractmethod, ABCMeta
from typing_extensions import Self
from bald_spider import Response, Request
from bald_spider.utils.log import get_logger
from bald_spider.middleware.middleware_manager import MiddlewareManager


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

class DownloaderMeta(ABCMeta):
    """
    解决一个问题：就是我没有继承基类，但是我实现了你基类所有的方法，这个时候其实也是可行的
    """
    # 当我们调用issubclass的时候，默认调用的方法是__subclasscheck__
    def __subclasscheck__(self, subclass):
        required_method = ("fetch","download","create_instance","close","idle")
        # 当四个方法同时存在且都调用的情况下，才算是子类
        is_subclass = all(
            hasattr(subclass,method) and callable(getattr(subclass,method,None)) for method in required_method
        )
        return is_subclass

class DownloaderBase(metaclass=DownloaderMeta):
    def __init__(self,crawler):
        self.crawler = crawler
        self._active = ActiveRequestManager()
        self.middleware:Optional[MiddlewareManager] = None
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get("LOG_LEVEL"))

    @classmethod
    def create_instance(cls,*args,**kwargs) -> Self:
        return cls(*args,**kwargs)

    def open(self) -> None:
        self.logger.info(f"{self.crawler.spider} <downloader class:{type(self).__name__}>"
                         f"<concurrency:{self.crawler.settings.getint('CONCURRENCY')}>")
        self.middleware = MiddlewareManager.create_instance(self.crawler)

    async def fetch(self, request) -> Optional[Response]:
        # 其实在这个地方，请求来的时候我们加入到队列中，当请求结束后，我们从队列中删除，可以使用上下文管理器来进行操作
        async with self._active(request):
            response = await self.download(request)
            return response

    @abstractmethod
    async def download(self,request:Request) -> Response:
        pass

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self) -> int:
        return len(self._active)

    async def close(self) -> None:
        pass



