import asyncio
from inspect import iscoroutine

from bald_spider.core.download import Downloader
from typing import Optional,Generator,Callable
from bald_spider.core.scheduler import Scheduler
from bald_spider.spider import Spider
from bald_spider.utils.spider import transform


class Engine:
    def __init__(self):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None
        # 初始化spider
        self.spider:Optional[Spider] = None

    async def start_spider(self, spider):
        # 得到spider
        self.spider = spider

        # 初始化调度器和下载器
        self.scheduler = Scheduler()
        if hasattr(self.scheduler,"open"):
            self.scheduler.open()
        self.downloader = Downloader()
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_request())
        await self._open_spider()

    async def _open_spider(self):
        crawling = asyncio.create_task(self.crawl())
        # 这个地方可以做其他事情
        await crawling

    async def crawl(self):
        """主逻辑"""
        while True:
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    # 使用next取出迭代器中的数据
                    start_request = next(self.start_requests)

                except StopIteration:
                    self.start_requests = None
                except Exception:
                    break
                else:
                    # 入队
                    await self.enqueue_request(start_request)

    async def enqueue_request(self,request):
        await self._scheduler_request(request)

    async def _scheduler_request(self,request):
        # 为什么不在上面直接写await self.scheduler.enqueue_request(request)
        # 因为我们需要进行去重操作，而不是直接进行入队操作
        # todo 去重
        await self.scheduler.enqueue_request(request)

    async def _get_next_request(self):
        return await self.scheduler.next_request()

    async def _crawl(self,request):
        # todo 实现并发
        outputs = await self._fetch(request)
        # todo 处理output
        if outputs:
            async for output in outputs:
                print(output)


    async def _fetch(self,request):
        async def _success(_response):
            callback: Callable = request.callback or self.spider.parse
            # 得到的数据类型可能是异步生成器，同步生成器，无类型数据，需要兼容
            # 当callback(_response)是None,直接跳出，默认直接返回None(就是无数据类型)
            if _outputs := callback(_response):
                # 是协程类型，等待执行即可
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    # 是生成器类型，就都转化成异步生成器
                    return transform(_outputs)

        _response = await self.downloader.fetch(request)
        # 能够得到结果调用到callback，说明上面的downloader下载成功了，但是实际网络请求中并不一定能成功
        # 这个地方暂时只处理成功的代码
        outputs = await _success(_response)
        return outputs
