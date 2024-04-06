PROJECT_NAME = "baidu_spider"
CONCURRENCY = 16
ABC = "qqqq"
LOG_LEVEL = "DEBUG"
# USE_SESSION = False
# DOWNLOADER = "bald_spider.core.downloader.aiohttp_downloader.AioDownloader"
MIDDLEWARES = [
    "test.baidu_spider.middleware.TestMiddleware",
    "test.baidu_spider.middleware.TestMiddleware1",
]