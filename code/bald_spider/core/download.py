import requests
import asyncio


class Downloader:
    def __init__(self):
        pass

    async def download(self, url):
        # response = requests.get(url)
        # print(response)
        await asyncio.sleep(0.1)
        print("成功了")
