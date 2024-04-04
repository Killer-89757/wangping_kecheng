from baidu import BaiduSpider
from bald_spider.core.engine import Engine
import asyncio
import time
from bald_spider.utils.project import get_settings

async def run():
    settings = get_settings()
    print(settings)
    baidu_spider = BaiduSpider()
    engine = Engine(settings)
    await engine.start_spider(baidu_spider)

s = time.time()
asyncio.run(run())
print(time.time() - s)