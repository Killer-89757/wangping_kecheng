from bald_spider.spider import Spider
class BaiduSpider(Spider):

    # start_url ="https://www.baidu.com"
    start_urls = ["https://www.baidu.com","https://www.baidu.com","https://www.baidu.com"]

    def parse(self,response):
        print("parse",response)
