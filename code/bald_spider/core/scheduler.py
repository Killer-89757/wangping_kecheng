from asyncio import PriorityQueue
from typing import Optional
from bald_spider.utils.pqueue import SpiderPriorityQueue

class Scheduler:
    def __init__(self):
        # 使用优先级队列，不同的请求的优先级不同
        self.request_queue: Optional[PriorityQueue] = None

    def open(self):
        self.request_queue = SpiderPriorityQueue()

    async def next_request(self):
        request = await self.request_queue.get()
        return request

    async def enqueue_request(self,request):
        await self.request_queue.put(request)

    def idle(self):
        """
        判断当前的请求队列中时候还有数据
        """
        return len(self) == 0

    def __len__(self):
        return self.request_queue.qsize()
