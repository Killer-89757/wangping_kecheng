# 这个地方的导包的方式学习一下
from bald_spider import Request

class Spider:
    def __init__(self):
        if not hasattr(self,"start_urls"):
            self.start_urls = []
        self.crawler = None

    @classmethod
    def create_instance(cls,crawler):
        """
        强制用户在使用的时候按照我们的想法去创建对象
        """
        o = cls()
        # 使得在创建的实例的时候也保留一份crawler
        o.crawler = crawler
        return o


    def start_request(self):
        if self.start_urls:
            for url in self.start_urls:
                yield Request(url=url)
        else:
            if hasattr(self,"start_url") and isinstance(getattr(self,"start_url"),str):
                yield Request(url=getattr(self,"start_url"))

    def parse(self,response):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__
