from test.baidu_spider.spiders.baidu import BaiduSpider
from test.baidu_spider.spiders.weibo import WeiboSpider
from bald_spider.crawler import CrawlerProcess
import asyncio
import time
from bald_spider.utils.project import get_settings
# 虽然没有调用，但是导入就是执行，只有在AioDownloader挂代理失败的时候在导入
# from bald_spider.utils import system as _

async def run():
    # srp 单一职责原则：single responsibility principle
    settings = get_settings()
    process = CrawlerProcess(settings)
    # 创建爬虫spider任务
    await process.crawl(BaiduSpider)
    # await process.crawl(WeiboSpider)
    # 通过start实现真正的启动
    await process.start()

s = time.time()
asyncio.run(run())
print(time.time() - s)