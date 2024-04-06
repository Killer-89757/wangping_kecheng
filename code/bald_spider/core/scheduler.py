import asyncio
from asyncio import PriorityQueue
from typing import Optional
from bald_spider.utils.pqueue import SpiderPriorityQueue
from bald_spider.utils.log import get_logger
class Scheduler:
    def __init__(self,crawler):
        self.crawler = crawler
        # 使用优先级队列，不同的请求的优先级不同
        self.request_queue: Optional[PriorityQueue] = None
        self.item_count = 0
        self.response_count = 0
        self.logger = get_logger(self.__class__.__name__,log_level=crawler.settings.get("LOG_LEVEL"))

    def open(self):
        self.request_queue = SpiderPriorityQueue()

    async def next_request(self):
        request = await self.request_queue.get()
        return request

    async def enqueue_request(self,request):
        await self.request_queue.put(request)
        # 将请求的数量 +1
        self.crawler.stats.inc_value("request_Scheduled_count")

    def idle(self):
        """
        判断当前的请求队列中时候还有数据
        """
        return len(self) == 0

    def __len__(self):
        return self.request_queue.qsize()

    # 其实这个日志并不属于调度器，只是临时写在这个地方
    async def interval_log(self,interval):
        while True:
            last_item_count = self.crawler.stats.get_value("item_successful_count",default=0)
            last_response_count = self.crawler.stats.get_value("response_received_count",default=0)
            item_rate = last_item_count - self.item_count
            response_rate = last_response_count - self.response_count
            self.item_count = last_item_count
            self.response_count = last_response_count
            self.logger.info(f"Crawler {last_response_count} pages (at {response_rate} pages / {interval}s)"
                             f"Got {last_item_count} items (at {item_rate} items / {interval}s)")
            await asyncio.sleep(interval)
