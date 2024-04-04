from bald_spider.core.download import Download


class Engine:
    def __init__(self):
        self.downloader = Download()

    def start_spider(self, spider):
        start_url = spider.start_url
        self.downloader.download(start_url)
