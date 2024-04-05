from bald_spider.spider import Spider
from bald_spider import Request
from items import BaiduItem   # type:ignore

class BaiduSpider(Spider):

    # start_url ="https://www.baidu.com"
    start_urls = ["http://www.baidu.com","http://www.baidu.com"]

    custom_settings = {"CONCURRENCY" : 8}

    def parse(self,response):
        """
        其实在这个部分，我们无法预测到用户会怎样书写代码(同步、异步) 我们都需要进行兼容
        若使用异步的方式，得到的其实就是异步生成器
        """
        # print("parse",response)
        for i in range(3):
            url = "https://www.baidu.com11"
            request = Request(url=url,callback=self.parse_page)
            yield request

    def parse_page(self,response):
        # print("parse_page",response)
        for i in range(3):
            url = "http://www.baidu.com"
            meta = {"test":"waws"}
            request = Request(url=url,callback=self.parse_detail,meta=meta)
            yield request

    def parse_detail(self,response):
        # print("parse_detail",response)
        # print(response.text)
        item = BaiduItem()
        item["url"] = "baidu.com"
        item["title"] = "百度首页"
        # item.title = "111"
        yield item
