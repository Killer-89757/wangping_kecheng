from baidu import BaiduSpider
from bald_spider.core.engine import Engine

baidu_spider = BaiduSpider()
engine = Engine()
engine.start_spider(baidu_spider)