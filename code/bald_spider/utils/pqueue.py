from asyncio import PriorityQueue,TimeoutError
import asyncio

class SpiderPriorityQueue(PriorityQueue):
    def __init__(self, maxsize=0):
        super(SpiderPriorityQueue,self).__init__(maxsize=maxsize)

    async def get(self):
        # 在get的方法中Remove and return an item from the queue.If queue is empty, wait until an item is available.
        # 也就是说当队列中没有元素的时候，就会一直等待直到有数据为止，所以一直阻塞中
        # 当我们使用coro进行接收的时候，其实拿到的是一个协程对象
        coro = super().get()
        try:
            # 在这个地方我们对协程对象进行判断，获取不到，超时0.1s的话就直接将其设置成None,防止一直wait使得程序卡住
            return await asyncio.wait_for(coro, timeout=0.1)
        except TimeoutError:
            return None