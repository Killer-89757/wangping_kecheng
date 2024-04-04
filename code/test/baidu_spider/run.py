from baidu import BaiduSpider
from bald_spider.core.engine import Engine
import asyncio
import time
async def run():
    baidu_spider = BaiduSpider()
    engine = Engine()
    await engine.start_spider(baidu_spider)

s = time.time()
asyncio.run(run())
print(time.time() - s)