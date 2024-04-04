from bald_spider.core.download import Downloader
from typing import Optional,Generator


class Engine:
    def __init__(self):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Downloader = Downloader()
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None

    def start_spider(self, spider):
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_request())
        self.crawl()

    def crawl(self):
        """主逻辑"""
        while True:
            try:
                # 使用next取出迭代器中的数据
                start_request = next(self.start_requests)
                self.downloader.download(start_request)
            except StopIteration:
                self.start_requests = None
            except Exception:
                break
