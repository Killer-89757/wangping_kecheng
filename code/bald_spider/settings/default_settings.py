"""
default config
"""
CONCURRENCY = 8
ABC = "wwww"

LOG_LEVEL = "INFO"
VERIFY_SSL = True
REQUEST_TIMEOUT = 60
USE_SESSION = True
DOWNLOADER = "bald_spider.core.downloader.aiohttp_downloader.AioDownloader"
# DOWNLOADER = "bald_spider.core.downloader.httpx_downloader.HttpxDownloader"
