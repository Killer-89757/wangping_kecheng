from bald_spider.core.download import Downloader
from typing import Optional,Generator
from bald_spider.core.scheduler import Scheduler


class Engine:
    def __init__(self):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None

    async def start_spider(self, spider):
        # 初始化调度器和下载器
        self.scheduler = Scheduler()
        if hasattr(self.scheduler,"open"):
            self.scheduler.open()
        self.downloader = Downloader()
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_request())
        await self.crawl()

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
        await self.downloader.download(request)