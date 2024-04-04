# 猿人学-爬虫框架课程(2)

## 项目简介

项目：wangping_kecheng

猿人学王平老师的爬虫系统架构的代码

课程环境：python 3.10

## 项目实现

创建两个包：

- bald_spider：项目代码的地方
  - core:核心代码存放处
    - \__init__.py 
    - download.py  **下载器**
    - engine.py        **引擎**
    - scheduler.py   **调度器**
  - spider：存放spider基类的地方
    - \__init__.py     **基类**
  - http：存放spider基类的地方
    - \__init__.py     
    - request.py     **请求类**
  - settings：存放spider基类的地方
    - \__init__.py     
    - default_settings.py     **默认配置**
    - settings_manager.py     **配置管理器**
  - utils: 工具包
    - \__init__.py 
    - pqueue.py  **自己封装的优先级队列**
    - spider.py  **爬虫工具：生成器转化工具等**
    - project.py  **获取用户配置工具**
  - \__init__.py       **方便导包**
  - execption.py  **自定义异常**
  - task_manager.py  **任务管理**
  - crawler.py    **工程启动封装**
- test：测试爬虫的代码
  - baidu_spider
    - spiders  用户爬虫
      - \__init__.py 
      - baidu.py  **爬虫实例**
      - weibo.py  **爬虫实例**
    - \__init__.py 
    - run.py     **项目启动文件**
    - settings.py  **用户配置文件**
  - misc
    - demo1.py **测试信号量**
    - demo2.py **测试信号量**
    - demo3.py **测试模块信息(获取配置信息)**
    - demo4.py **\_\_getitem__的使用**

### 第五个阶段：response判断

这个地方实际上加入的是对response的判断

- response是Request类的话，再次进入下载流程中，

- response是Item类的话，再次进入数据解析中
- 不是以上两种类型，抛出错误

```python
# engine.py
import asyncio
from inspect import iscoroutine

from bald_spider.core.download import Downloader
from typing import Optional,Generator,Callable
from bald_spider.core.scheduler import Scheduler
from bald_spider.spider import Spider
from bald_spider.utils.spider import transform
from bald_spider.execptions import OutputError
from bald_spider.http.request import Request

class Engine:
    def __init__(self):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None
        # 初始化spider
        self.spider:Optional[Spider] = None

    async def start_spider(self, spider):
        # 得到spider
        self.spider = spider

        # 初始化调度器和下载器
        self.scheduler = Scheduler()
        if hasattr(self.scheduler,"open"):
            self.scheduler.open()
        self.downloader = Downloader()
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_request())
        await self._open_spider()

    async def _open_spider(self):
        crawling = asyncio.create_task(self.crawl())
        # 这个地方可以做其他事情
        await crawling

    async def crawl(self):
        """主逻辑"""
        while True:
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    # 使用next取出迭代器中的数据
                    start_request = next(self.start_requests)

                except StopIteration:
                    self.start_requests = None
                except Exception:
                    break
                else:
                    # 入队
                    await self.enqueue_request(start_request)

    async def enqueue_request(self,request):
        await self._scheduler_request(request)

    async def _scheduler_request(self,request):
        # 为什么不在上面直接写await self.scheduler.enqueue_request(request)
        # 因为我们需要进行去重操作，而不是直接进行入队操作
        # todo 去重
        await self.scheduler.enqueue_request(request)

    async def _get_next_request(self):
        return await self.scheduler.next_request()

    async def _crawl(self,request):
        # todo 实现并发
        outputs = await self._fetch(request)
        # todo 处理output
        if outputs:
            await self._handle_spider_output(outputs)


    async def _fetch(self,request):
        async def _success(_response):
            callback: Callable = request.callback or self.spider.parse
            # 得到的数据类型可能是异步生成器，同步生成器，无类型数据，需要兼容
            # 当callback(_response)是None,直接跳出，默认直接返回None(就是无数据类型)
            if _outputs := callback(_response):
                # 是协程类型，等待执行即可
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    # 是生成器类型，就都转化成异步生成器
                    return transform(_outputs)
        _response = await self.downloader.fetch(request)
        # 能够得到结果调用到callback，说明上面的downloader下载成功了，但是实际网络请求中并不一定能成功
        # 这个地方暂时只处理成功的代码
        outputs = await _success(_response)
        return outputs
    async def _handle_spider_output(self,outputs):
        """
        在这个地方对输出的结果进行判断，数据走管道，请求重新回到spider
        """
        async for spider_output in outputs:
            if isinstance(spider_output,Request):
                await self.enqueue_request(spider_output)
            # todo 判断是不是数据,暂定为Item
            else:
                raise OutputError(f"{type(self.spider)} must return Request or Item")

# request.py
from typing import Dict, Optional,Callable

class Request:
    def __init__(
            self, url: str, *,
            headers: Optional[Dict] = None,
            callback:Callable = None,
            priority: int = 0,
            method: str = "GET",
            cookies: Optional[Dict] = None,
            proxy: Optional[Dict] = None,
            body=""
    ):
        self.url = url
        self.headers = headers
        self.callback = callback
        self.priority = priority
        self.method = method
        self.cookies = cookies
        self.proxy = proxy
        self.body = body

    def __lt__(self, other):
        return self.priority < other.priority

# baidu.py
from bald_spider.spider import Spider
from bald_spider import Request
class BaiduSpider(Spider):

    # start_url ="https://www.baidu.com"
    start_urls = ["https://www.baidu.com","https://www.baidu.com"]

    def parse(self,response):
        """
        其实在这个部分，我们无法预测到用户会怎样书写代码(同步、异步) 我们都需要进行兼容
        若使用异步的方式，得到的其实就是异步生成器
        """
        print("parse",response)
        for i in range(3):
            url = "https://www.baidu.com"
            request = Request(url=url,callback=self.parse_page)
            yield request

    def parse_page(self,response):
        print("parse_page",response)
        for i in range(3):
            url = "https://www.baidu.com"
            request = Request(url=url,callback=self.parse_detail)
            yield request

    def parse_detail(self,response):
        print("parse_detail",response)
            
# execption.py
class TransformTypeError(TypeError):
    pass

class OutputError(Exception):
    pass
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404184528490-45b21d.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404190855928-dcbda2.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404192709735-10a6da.png)

### 第六个阶段：并发请求(base)

```python
# engine.py
import asyncio
from inspect import iscoroutine

from bald_spider.core.download import Downloader
from typing import Optional,Generator,Callable
from bald_spider.core.scheduler import Scheduler
from bald_spider.spider import Spider
from bald_spider.utils.spider import transform
from bald_spider.execptions import OutputError
from bald_spider.http.request import Request

class Engine:
    def __init__(self):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None
        # 初始化spider
        self.spider:Optional[Spider] = None
        # 控制爬虫进行的开关
        self.running = False

    async def start_spider(self, spider):
        # 打开开关
        self.running = True

        # 得到spider
        self.spider = spider

        # 初始化调度器和下载器
        self.scheduler = Scheduler()
        if hasattr(self.scheduler,"open"):
            self.scheduler.open()
        self.downloader = Downloader()
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_request())
        await self._open_spider()

    async def _open_spider(self):
        crawling = asyncio.create_task(self.crawl())
        # 这个地方可以做其他事情
        await crawling

    async def crawl(self):
        """主逻辑"""
        while self.running:
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    # 使用next取出迭代器中的数据
                    start_request = next(self.start_requests)

                except StopIteration:
                    self.start_requests = None
                except Exception:
                    # 1.发起请求的task要运行完毕
                    # 2.调度器是否空闲
                    # 3.下载器是否空闲
                    if not await self._exit():
                        continue
                    self.running = False
                else:
                    # 入队
                    await self.enqueue_request(start_request)

    async def enqueue_request(self,request):
        await self._scheduler_request(request)

    async def _scheduler_request(self,request):
        # 为什么不在上面直接写await self.scheduler.enqueue_request(request)
        # 因为我们需要进行去重操作，而不是直接进行入队操作
        # todo 去重
        await self.scheduler.enqueue_request(request)

    async def _get_next_request(self):
        return await self.scheduler.next_request()

    async def _crawl(self,request):
        async def crawl_task():
            outputs = await self._fetch(request)
            # todo 处理output
            if outputs:
                await self._handle_spider_output(outputs)
        asyncio.create_task(crawl_task(),name="crawl")

    async def _fetch(self,request):
        async def _success(_response):
            callback: Callable = request.callback or self.spider.parse
            # 得到的数据类型可能是异步生成器，同步生成器，无类型数据，需要兼容
            # 当callback(_response)是None,直接跳出，默认直接返回None(就是无数据类型)
            if _outputs := callback(_response):
                # 是协程类型，等待执行即可
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    # 是生成器类型，就都转化成异步生成器
                    return transform(_outputs)
        _response = await self.downloader.fetch(request)
        # 能够得到结果调用到callback，说明上面的downloader下载成功了，但是实际网络请求中并不一定能成功
        # 这个地方暂时只处理成功的代码
        outputs = await _success(_response)
        return outputs
    async def _handle_spider_output(self,outputs):
        """
        在这个地方对输出的结果进行判断，数据走管道，请求重新回到spider
        """
        async for spider_output in outputs:
            if isinstance(spider_output,Request):
                await self.enqueue_request(spider_output)
            # todo 判断是不是数据,暂定为Item
            else:
                raise OutputError(f"{type(self.spider)} must return Request or Item")

    async def _exit(self):
        """
        其实在这个地方有一点错误就是我们先判断调度器和下载器，为空直接返回结束，但是任务可能还在运行
        三者应该是共同决定是否结束的条件
        """
        # 调度器是否空闲
        # 下载器是否空闲
        if self.scheduler.idle() and self.downloader.idle():
            return True
        # 发起请求的task全部运行完毕
        for task in asyncio.all_tasks():
            # print(task.get_name())
            if not task.done() and task.get_name() == "crawl":
                return False
        return True
    
# download.py
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

    # 主要是为了解决退出程序，下载器为空是重要一环
    def idle(self):
        return len(self) == 0
	
    def __len__(self):
        return len(self._active)
    
# scheduler.py
from asyncio import PriorityQueue
from typing import Optional
from bald_spider.utils.pqueue import SpiderPriorityQueue

class Scheduler:
    def __init__(self):
        # 使用优先级队列，不同的请求的优先级不同
        self.request_queue: Optional[PriorityQueue] = None

    def open(self):
        self.request_queue = SpiderPriorityQueue()

    async def next_request(self):
        request = await self.request_queue.get()
        return request

    async def enqueue_request(self,request):
        await self.request_queue.put(request)

    def idle(self):
        """
        判断当前的请求队列中时候还有数据
        """
        return len(self) == 0

    def __len__(self):
        return self.request_queue.qsize()

# baidu.py
from bald_spider.spider import Spider
from bald_spider import Request
class BaiduSpider(Spider):

    # start_url ="https://www.baidu.com"
    start_urls = ["https://www.baidu.com","https://www.baidu.com"]

    def parse(self,response):
        """
        其实在这个部分，我们无法预测到用户会怎样书写代码(同步、异步) 我们都需要进行兼容
        若使用异步的方式，得到的其实就是异步生成器
        """
        print("parse",response)
        for i in range(3):
            url = "https://www.baidu.com"
            request = Request(url=url,callback=self.parse_page)
            yield request

    def parse_page(self,response):
        print("parse_page",response)
        for i in range(3):
            url = "https://www.baidu.com"
            request = Request(url=url,callback=self.parse_detail)
            yield request

    def parse_detail(self,response):
        print("parse_detail",response)
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404204007318-a16a2d.png)

### 第七个阶段：并发请求(upgrade)

主要完成了两个功能：

1. **将task统一进行管理，可以直接数出来当前正在运行的爬虫任务**
2. **控制并发**

```python
# engine.py
import asyncio
from inspect import iscoroutine

from bald_spider.core.download import Downloader
from typing import Optional,Generator,Callable,Final,Set
from bald_spider.core.scheduler import Scheduler
from bald_spider.spider import Spider
from bald_spider.utils.spider import transform
from bald_spider.execptions import OutputError
from bald_spider.http.request import Request
from bald_spider.task_manager import TaskManager

class Engine:
    def __init__(self):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None
        # 初始化spider
        self.spider:Optional[Spider] = None
        # 控制爬虫进行的开关
        self.running = False
        # 初始化task管理器
        self.task_manager:TaskManager= TaskManager()

    async def start_spider(self, spider):
        # 打开开关
        self.running = True

        # 得到spider
        self.spider = spider

        # 初始化调度器和下载器
        self.scheduler = Scheduler()
        if hasattr(self.scheduler,"open"):
            self.scheduler.open()
        self.downloader = Downloader()
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_request())
        await self._open_spider()

    async def _open_spider(self):
        crawling = asyncio.create_task(self.crawl())
        # 这个地方可以做其他事情
        await crawling

    async def crawl(self):
        """主逻辑"""
        while self.running:
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    # 使用next取出迭代器中的数据
                    start_request = next(self.start_requests)

                except StopIteration:
                    self.start_requests = None
                except Exception:
                    # 1.发起请求的task要运行完毕
                    # 2.调度器是否空闲
                    # 3.下载器是否空闲
                    if not await self._exit():
                        continue
                    self.running = False
                else:
                    # 入队
                    await self.enqueue_request(start_request)

    async def enqueue_request(self,request):
        await self._scheduler_request(request)

    async def _scheduler_request(self,request):
        # 为什么不在上面直接写await self.scheduler.enqueue_request(request)
        # 因为我们需要进行去重操作，而不是直接进行入队操作
        # todo 去重
        await self.scheduler.enqueue_request(request)

    async def _get_next_request(self):
        return await self.scheduler.next_request()

    async def _crawl(self,request):
        async def crawl_task():
            outputs = await self._fetch(request)
            # todo 处理output
            if outputs:
                await self._handle_spider_output(outputs)
        await self.task_manager.semaphore.acquire()
        self.task_manager.create_task(crawl_task())

    async def _fetch(self,request):
        async def _success(_response):
            callback: Callable = request.callback or self.spider.parse
            # 得到的数据类型可能是异步生成器，同步生成器，无类型数据，需要兼容
            # 当callback(_response)是None,直接跳出，默认直接返回None(就是无数据类型)
            if _outputs := callback(_response):
                # 是协程类型，等待执行即可
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    # 是生成器类型，就都转化成异步生成器
                    return transform(_outputs)
        _response = await self.downloader.fetch(request)
        # 能够得到结果调用到callback，说明上面的downloader下载成功了，但是实际网络请求中并不一定能成功
        # 这个地方暂时只处理成功的代码
        outputs = await _success(_response)
        return outputs
    async def _handle_spider_output(self,outputs):
        """
        在这个地方对输出的结果进行判断，数据走管道，请求重新回到spider
        """
        async for spider_output in outputs:
            if isinstance(spider_output,Request):
                await self.enqueue_request(spider_output)
            # todo 判断是不是数据,暂定为Item
            else:
                raise OutputError(f"{type(self.spider)} must return Request or Item")

    async def _exit(self):
        """
        其实在这个地方有一点错误就是我们先判断调度器和下载器，为空直接返回结束，但是任务可能还在运行
        三者应该是共同决定是否结束的条件
        """
        # 调度器是否空闲
        # 下载器是否空闲
        # 任务列表中是否为空
        if self.scheduler.idle() and self.downloader.idle() and self.task_manager.all_done():
            return True
        return False

# run.py
from baidu import BaiduSpider
from bald_spider.core.engine import Engine
import asyncio
import time
async def run():
    baidu_spider = BaiduSpider()
    engine = Engine()
    await engine.start_spider(baidu_spider)

s = time.time()
asyncio.run(run())
print(time.time() - s)

# task_manager.py
import asyncio
from typing import Set,Final
from asyncio import Task,Future,Semaphore

class TaskManager:
    def __init__(self,total_concurrency=16):
        # Final是制定了类型，不能改变
        self.current_task:Final[Set] = set()
        self.semaphore:Semaphore = Semaphore(total_concurrency)

    def create_task(self,coroutine):
        task = asyncio.create_task(coroutine)
        self.current_task.add(task)

        def done_callback(_fut:Future):
            self.current_task.remove(task)
            self.semaphore.release()
        # 当任务完成的时候，执行回调函数，就是删除task
        task.add_done_callback(done_callback)
        return task

    def all_done(self):
        return len(self.current_task) == 0
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404211812457-e7a497.png)

并发控制demo

```python
# demo1
from asyncio import Semaphore
import asyncio

semaphore = Semaphore(5)

async def demo():
    # 其实限制的原理就是内置了一个value,acquire一次就会减一，release一次就会加一
    # 当到达最大信号量的时候会一直阻塞住
    await semaphore.acquire()
    print(1111)
    semaphore.release()
    await semaphore.acquire()
    print(2222)
    await semaphore.acquire()
    print(3333)
    await semaphore.acquire()
    print(4444)
    await semaphore.acquire()
    print(5555)
    await semaphore.acquire()
    print(6666)

asyncio.run(demo())

# demo2
from asyncio import Semaphore,BoundedSemaphore
import asyncio

semaphore = Semaphore(5)
# semaphore = BoundedSemaphore(5)

async def demo():
    # 其实限制的原理就是内置了一个value,acquire一次就会减一，release一次就会加一
    # 当到达最大信号量的时候会一直阻塞住
    semaphore.release()
    semaphore.release()
    semaphore.release()
    print(semaphore._value)

asyncio.run(demo())
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404212129903-d1d760.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404212327961-87ddee.png)

- 并发在4 和16 的对比

  - 并发 = 4

  ![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404212940661-4b62c1.png)

- 并发 = 16

  ![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404213046476-46dc0b.png)

### 第八个阶段：全局可移植配置文件

在这个部分我们设计了用户目录下的配置文件、系统的默认配置文件、配置文件的管理类、配置文件的加载过程

```python
# engine.py
# 其实在初始化的时候进行配置加载
class Engine:
    def __init__(self,settings):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None
        # 初始化spider
        self.spider:Optional[Spider] = None
        # 控制爬虫进行的开关
        self.running = False
        # 初始化task管理器
        self.task_manager:TaskManager= TaskManager(settings.get("CONCURRENCY"))

# run.py
from baidu import BaiduSpider
from bald_spider.core.engine import Engine
import asyncio
import time
from bald_spider.utils.project import get_settings

async def run():
    settings = get_settings()
    print(settings)
    baidu_spider = BaiduSpider()
    engine = Engine(settings)
    await engine.start_spider(baidu_spider)

s = time.time()
asyncio.run(run())
print(time.time() - s)

# settings.py
PROJECT_NAME = "baidu_spider"
CONCURRENCY = 16
ABC = "qqqq"

# project.py
from bald_spider.settings.settings_manager import SettingsManager

def get_settings(settings="settings"):
    # 注意在这个地方，我们的_settings是SettingsManager对象，所以在打印的时候使用__str__转换打印信息
    _settings = SettingsManager({"111":2})
    _settings.set_settings(settings)
    return _settings

# settings.default_settings.py
"""
default config
"""
CONCURRENCY = 8
ABC = "wwww"

# settings.settings_manager.py
from importlib import import_module
from bald_spider.settings import default_settings
from collections.abc import MutableMapping


class SettingsManager(MutableMapping):
    def __init__(self,values=None):
        self.attributes = {}
        self.set_settings(default_settings)
        self.update_values(values)

    def __getitem__(self, item):
        if item not in self:
            return None
        return self.attributes[item]

    def __contains__(self, item):
        return item in self.attributes

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, value):
        self.attributes[key] = value

    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    # 当我们不小心写了一个字符串的数字，使用getint兼容
    def getint(self, name, default=1):
        return int(self.get(name, default))

    def getfloat(self, name, default=0.0):
        return float(self.get(name, default))

    def getbool(self, name, default=False):  # noqa
        # 比较麻烦，可以写True/False or "True"/"False" or 0/1
        got = self.get(name, default)
        try:
            # 可以兼容bool or int类型
            return bool(int(got))
        except ValueError:
            # 报错就是str类型
            if got in ("True","true","TRUE"):
                return True
            if got in ("False","false","FALSE"):
                return False
            raise ValueError("Supported values for bool settings are (0 or 1),(True or False),('0' or '1'),('True' or 'False'),('TRUE' or 'FALSE'),('true' or 'false')")

    def getlist(self, name, default=None):
        value = self.get(name, default or [])
        if isinstance(value,str):
            value = value.split(",")
        return list(value)


    def __delitem__(self, key):
        del self.attributes[key]

    def delete(self, key):
        del self.attributes[key]

    def set_settings(self, module):
        # 我们可以直接传入模块、或者传入模块的str名称
        if isinstance(module, str):
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))

    def __str__(self):
        return f"<settings value={self.attributes}>"

    __repr__ = __str__

    def update_values(self,values):
        if values is not None:
            for key,value in values.items():
                self.set(key,value)

    # 继承自抽象类的抽象方法都是要自行实现的
    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)


if __name__ == "__main__":
    settings = SettingsManager()
    settings["CONCURRENCY"] = 16
    print(settings.items())
```

用于演示的demo文件

```python
# demo3.py
# 获取到
from test.baidu_spider import settings

# print(dir(settings))
# ['CONCURRENCY', 'PROJECT_NAME', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__']

# print(type(settings))
# <class 'module'>

for name in dir(settings):
    if name.isupper():
        print(name,getattr(settings,name))
        # CONCURRENCY 16
        # PROJECT_NAME baidu_spider
        
# demo4.py
class A:
    def __getitem__(self, item):
        print(item)

    def __setitem__(self, key, value):
        print(key,value)

a = A()
a[1]  # 1
a[1:3]  # slice(1, 3, None)
a["name"] = "value1" # name value1
```

### 第九个阶段：优化项目启动

我们为了不暴漏Engine给用户使用，我们创建一个Crawler和CrawlerProcess进行Engine和Spider的融合和隐匿

- Crawler：主要是创建Engine和Spider实例让两者之间融合，三者中互有，可以相互调用
- CrawlerProcess：对上面的Engine和Spider实例进行隐藏，同时创建任务和启动任务

```python
# engine.py
class Engine:
    def __init__(self,crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None
        # 初始化spider
        self.spider:Optional[Spider] = None
        # 控制爬虫进行的开关
        self.running = False
        # 初始化task管理器
        print("当前的并发数是：",self.settings.getint("CONCURRENCY"))
        self.task_manager:TaskManager= TaskManager(self.settings.getint("CONCURRENCY"))

# exexptions.py
class SpiderTypeError(TypeError):
    pass

# settings_manager.py
from copy import deepcopy

class SettingsManager(MutableMapping):
    def copy(self):
        return deepcopy(self)

# spider.__init__.py
# 这个地方的导包的方式学习一下
from bald_spider import Request

class Spider:
    def __init__(self):
        if not hasattr(self,"start_urls"):
            self.start_urls = []
        self.crawler = None

    @classmethod
    def create_instance(cls,crawler):
        """
        强制用户在使用的时候按照我们的想法去创建对象
        """
        o = cls()
        # 使得在创建的实例的时候也保留一份crawler
        o.crawler = crawler
        return o

# run.py
from test.baidu_spider.spiders.baidu import BaiduSpider
from test.baidu_spider.spiders.weibo import WeiboSpider
from bald_spider.crawler import CrawlerProcess
import asyncio
import time
from bald_spider.utils.project import get_settings

async def run():
    # srp 单一职责原则：single responsibility principle
    settings = get_settings()
    process = CrawlerProcess(settings)
    # 创建爬虫spider任务
    await process.crawl(BaiduSpider)
    await process.crawl(WeiboSpider)
    # 通过start实现真正的启动
    await process.start()

s = time.time()
asyncio.run(run())
print(time.time() - s)

# crawler.py
import asyncio
from typing import Type,Final,Set,Optional
from bald_spider.spider import Spider
from bald_spider.settings.settings_manager import SettingsManager
from bald_spider.execptions import SpiderTypeError
from bald_spider.core.engine import Engine


class Crawler:
    def __init__(self,spider_cls,settings):
        self.spider_cls = spider_cls
        self.spider:Optional[Spider] = None
        self.engine:Optional[Engine] = None
        self.settings:SettingsManager = settings.copy()

    async def crawl(self):
        self.spider = self._create_spider()
        self.engine = self._create_engine()
        await self.engine.start_spider(self.spider)

    # 在这个地方还有个好处就是 engine、spider、crawler之间互相关联，三者都互有对方
    def _create_spider(self):
        # 不合理的原因：因为spider_cls是用户自定义的类，所以可以接受参数等，直接使用()的方式生成欠妥
        spider = self.spider_cls.create_instance(self)
        return spider

    def _create_engine(self):
        # 在这个地方我们可以直接将self.settings扔进engine中，我们的第一版启动方式的确是这样
        # 但是这个部分self是Crawl类，其中包含settings,传self更全面
        engine = Engine(self)
        return engine


class CrawlerProcess:
    def __init__(self,settings=None):
        self.crawlers:Final[Set] = set()
        self._active:Final[Set] = set()
        self.settings = settings

    # 在这个地方，我们可以实例化多个爬虫，那么在创建的时候使用的是一个配置文件
    # 配置管理器中使用的是可变的Mapping类型，这样会相互干扰，所以需要对配置管理进行深拷贝
    async def crawl(self,spider:Type[Spider]):
        crawler:Crawler = self._create_crawler(spider)
        self.crawlers.add(crawler)
        task = await self._crawl(crawler)
        self._active.add(task)

    @staticmethod
    async def _crawl(crawler):
        return asyncio.create_task(crawler.crawl())

    # 真正的启动函数
    async def start(self):
        await asyncio.gather(*self._active)

    def _create_crawler(self,spider_cls) -> Crawler:
        # 防止传入的是字符串，类型异常抛出
        if isinstance(spider_cls,str):
            raise SpiderTypeError(f"{type(self)}.crawl args:String is not supported")
        crawler = Crawler(spider_cls,self.settings)
        return crawler
```

### 第十个阶段：爬虫拥有各自的配置文件

- 用户爬虫并不是所有都是使用统一的配置文件
  - 我们可以在用户自定义的爬虫文件中使用`custom_settings`完成自定义爬虫配置项

```python
import asyncio
from typing import Type,Final,Set,Optional
from bald_spider.spider import Spider
from bald_spider.settings.settings_manager import SettingsManager
from bald_spider.execptions import SpiderTypeError
from bald_spider.core.engine import Engine
from bald_spider.utils.project import merge_settings


class Crawler:
    def __init__(self,spider_cls,settings):
        self.spider_cls = spider_cls
        self.spider:Optional[Spider] = None
        self.engine:Optional[Engine] = None
        self.settings:SettingsManager = settings.copy()

    async def crawl(self):
        self.spider = self._create_spider()
        self.engine = self._create_engine()
        await self.engine.start_spider(self.spider)

    # 在这个地方还有个好处就是 engine、spider、crawler之间互相关联，三者都互有对方
    def _create_spider(self):
        # 不合理的原因：因为spider_cls是用户自定义的类，所以可以接受参数等，直接使用()的方式生成欠妥
        spider = self.spider_cls.create_instance(self)
        self._set_spider(spider)
        return spider

    def _create_engine(self):
        # 在这个地方我们可以直接将self.settings扔进engine中，我们的第一版启动方式的确是这样
        # 但是这个部分self是Crawl类，其中包含settings,传self更全面
        engine = Engine(self)
        return engine

    def _set_spider(self,spider):
        merge_settings(spider,self.settings)

# settings_manager.py
class SettingsManager(MutableMapping):
    def set_settings(self, module):
        # 我们可以直接传入模块、或者传入模块的str名称
        if isinstance(module, str):
            # 因为我们的代码结构很好，所以不会出现路径加载不成功的问题
            # 但是框架形成后，用户自定义编辑文件可能会出现找不到配置文件的情况
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))
                
# project.py
def _get_closest(path="."):
    path = os.path.abspath(path)
    return path


def _init_env():
    # 将最近的路径加入到环境变量中，在搜索配置文件时候防止报错
    closest = _get_closest()
    if closest:
        project_dir = os.path.dirname(closest)
        sys.path.append(project_dir)

# baidu.py
from bald_spider.spider import Spider
from bald_spider import Request
class BaiduSpider(Spider):

    # start_url ="https://www.baidu.com"
    start_urls = ["https://www.baidu.com","https://www.baidu.com"]

    custom_settings = {"CONCURRENCY" : 8}
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405021317913-ec1944.png)