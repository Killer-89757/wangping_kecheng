import requests
import asyncio
import random


class Downloader:
    def __init__(self):
        pass

    async def fetch(self,request):
        return await self.download(request)

    async def download(self, request):
        # response = requests.get(request.url)
        # print(response)
        await asyncio.sleep(random.uniform(0,1))
        # print("成功了")
        return "result"