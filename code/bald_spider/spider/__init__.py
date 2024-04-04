# 这个地方的导包的方式学习一下
from bald_spider import Request

class Spider:
    def __init__(self):
        if not hasattr(self,"start_urls"):
            self.start_urls = []

    def start_request(self):
        if self.start_urls:
            for url in self.start_urls:
                yield Request(url=url)
        else:
            if hasattr(self,"start_url") and isinstance(getattr(self,"start_url"),str):
                yield Request(url=getattr(self,"start_url"))

    def parse(self,response):
        raise NotImplementedError
