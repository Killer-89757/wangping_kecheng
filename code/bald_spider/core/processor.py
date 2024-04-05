from asyncio import Queue
from typing import Union
from bald_spider import Item, Request


class Processor:
    def __init__(self, crawler):
        self.queue: Queue = Queue()
        self.crawler = crawler

    async def process(self):
        while not self.idle():
            result = await self.queue.get()
            if isinstance(result, Request):
                await self.crawler.engine.enqueue_request(result)
            else:
                assert isinstance(result, Item)
                await self._process_item(result)

    async def _process_item(self, item: Item):
        print(item)

    async def enqueue(self, output: Union[Request, Item]):
        await self.queue.put(output)
        await self.process()

    def idle(self):
        return len(self) == 0

    def __len__(self):
        return self.queue.qsize()
