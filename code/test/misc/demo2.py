from asyncio import Semaphore,BoundedSemaphore
import asyncio

semaphore = Semaphore(5)
# semaphore = BoundedSemaphore(5)

async def demo():
    # 其实限制的原理就是内置了一个value,acquire一次就会减一，release一次就会加一
    # 当到达最大信号量的时候会一直阻塞住
    semaphore.release()
    semaphore.release()
    semaphore.release()
    print(semaphore._value)


asyncio.run(demo())