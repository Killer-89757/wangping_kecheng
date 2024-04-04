import requests
import asyncio
import random


class Downloader:
    def __init__(self):
        self._active = set()

    async def fetch(self,request):
        self._active.add(request)
        response = await self.download(request)
        self._active.remove(request)
        return response

    async def download(self, request):
        # response = requests.get(request.url)
        # print(response)
        await asyncio.sleep(random.uniform(0,1))
        # print("成功了")
        return "result"

    def idle(self):
        return len(self) == 0

    def __len__(self):
        return len(self._active)