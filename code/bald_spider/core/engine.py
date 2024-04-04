import asyncio
from inspect import iscoroutine

from bald_spider.core.download import Downloader
from typing import Optional,Generator,Callable,Final,Set
from bald_spider.core.scheduler import Scheduler
from bald_spider.spider import Spider
from bald_spider.utils.spider import transform
from bald_spider.execptions import OutputError
from bald_spider.http.request import Request
from bald_spider.task_manager import TaskManager

class Engine:
    def __init__(self,crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None
        # 初始化spider
        self.spider:Optional[Spider] = None
        # 控制爬虫进行的开关
        self.running = False
        # 初始化task管理器
        print("当前的并发数是：",self.settings.getint("CONCURRENCY"))
        self.task_manager:TaskManager= TaskManager(self.settings.getint("CONCURRENCY"))

    async def start_spider(self, spider):
        # 打开开关
        self.running = True

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
        while self.running:
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    # 使用next取出迭代器中的数据
                    start_request = next(self.start_requests)

                except StopIteration:
                    self.start_requests = None
                except Exception:
                    # 1.发起请求的task要运行完毕
                    # 2.调度器是否空闲
                    # 3.下载器是否空闲
                    if not await self._exit():
                        continue
                    self.running = False
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
        async def crawl_task():
            outputs = await self._fetch(request)
            # todo 处理output
            if outputs:
                await self._handle_spider_output(outputs)
        await self.task_manager.semaphore.acquire()
        self.task_manager.create_task(crawl_task())

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
    async def _handle_spider_output(self,outputs):
        """
        在这个地方对输出的结果进行判断，数据走管道，请求重新回到spider
        """
        async for spider_output in outputs:
            if isinstance(spider_output,Request):
                await self.enqueue_request(spider_output)
            # todo 判断是不是数据,暂定为Item
            else:
                raise OutputError(f"{type(self.spider)} must return Request or Item")

    async def _exit(self):
        """
        其实在这个地方有一点错误就是我们先判断调度器和下载器，为空直接返回结束，但是任务可能还在运行
        三者应该是共同决定是否结束的条件
        """
        # 调度器是否空闲
        # 下载器是否空闲
        # 任务列表中是否为空
        if self.scheduler.idle() and self.downloader.idle() and self.task_manager.all_done():
            return True
        return False