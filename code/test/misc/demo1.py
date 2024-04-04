from asyncio import Semaphore
import asyncio

semaphore = Semaphore(5)

async def demo():
    # 其实限制的原理就是内置了一个value,acquire一次就会加一，release一次就会减一
    # 当到达最大信号量的时候会一直阻塞住
    await semaphore.acquire()
    print(1111)
    semaphore.release()
    await semaphore.acquire()
    print(2222)
    await semaphore.acquire()
    print(3333)
    await semaphore.acquire()
    print(4444)
    await semaphore.acquire()
    print(5555)
    await semaphore.acquire()
    print(6666)

asyncio.run(demo())