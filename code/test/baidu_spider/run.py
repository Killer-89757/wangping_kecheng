from test.baidu_spider.spiders.baidu import BaiduSpider
from test.baidu_spider.spiders.weibo import WeiboSpider
from bald_spider.crawler import CrawlerProcess
import asyncio
import time
from bald_spider.utils.project import get_settings

async def run():
    # srp 单一职责原则：single responsibility principle
    settings = get_settings()
    process = CrawlerProcess(settings)
    # 创建爬虫spider任务
    await process.crawl(BaiduSpider)
    await process.crawl(WeiboSpider)
    # 通过start实现真正的启动
    await process.start()

s = time.time()
asyncio.run(run())
print(time.time() - s)