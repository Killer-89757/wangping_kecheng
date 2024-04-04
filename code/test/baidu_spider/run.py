from baidu import BaiduSpider
from bald_spider.core.engine import Engine
import asyncio
async def run():
    baidu_spider = BaiduSpider()
    engine = Engine()
    await engine.start_spider(baidu_spider)

asyncio.run(run())