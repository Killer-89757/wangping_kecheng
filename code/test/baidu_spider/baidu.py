from bald_spider.spider import Spider
from bald_spider import Request
class BaiduSpider(Spider):

    # start_url ="https://www.baidu.com"
    start_urls = ["https://www.baidu.com","https://www.baidu.com","https://www.baidu.com"]

    async def parse(self,response):
        """
        其实在这个部分，我们无法预测到用户会怎样书写代码(同步、异步) 我们都需要进行兼容
        若使用异步的方式，得到的其实就是异步生成器
        """
        print("parse",response)
        for i in range(10):
            url = "https://www.baidu.com"
            request = Request(url=url)
            yield request
