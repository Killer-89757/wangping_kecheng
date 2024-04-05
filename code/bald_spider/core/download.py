import asyncio
import random
# aiohttp httpx 插件化：插拔器，即插即用
# 思路：
# 1.在Engine中需要用到fetch、idle方法，需要分别实现
# 2.我们生成的response是不同的，所以我们需要进行兼容
# 3.我们根据配置文件实现动态加载

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