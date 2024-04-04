# 猿人学-爬虫框架课程(1)

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
  - utils: 工具包
    - \__init__.py 
    - pqueue.py  **自己封装的优先级队列**
    - spider.py  **爬虫工具：生成器转化工具等**
  - \__init__.py       **方便导包**
  - execption.py  **自定义异常**
- test：测试爬虫的代码
  - baidu_spider
    - \__init__.py 
    - baidu.py  爬虫实例
    - run.py     项目启动文件

爬虫**脚本化**思维

```python
import requests

class BaiduSpider():
    start_url = "https://www.baidu.com"
    def start_requests(self):
        response = requests.get(self.start_url)
        print(response)

if __name__ == "__main__":
    baidu_spider = BaiduSpider()
    baidu_spider.start_requests()
```

> 思考学习是怎样写系统项目的
>
> - 分解
> - 流程图

### 第一个阶段：基础

在这个地方其实我们能感受到代码结构拆分，我们engine是负责调度的，spider是爬虫本虫，download是下载器，我们需要将spider和download都放入到engine中，然后通过engine的方法启动爬虫。

- 注意我们这个地方的spider爬虫，是百度的爬虫实例

```python
# 构建下载器和核心引擎,使用测试代码测试代码

# engine.py
from bald_spider.core.download import Download

class Engine:
    def __init__(self):
        self.downloader = Download()

    def start_spider(self, spider):
        start_url = spider.start_requests()
        self.downloader.download(start_url)
        
# download.py
import requests

class Download:
    def __init__(self):
        pass

    def download(self, url):
        response = requests.get(url)
        print(response)

# test文件夹
# baidu.py
class BaiduSpider():
    start_url = "https://www.baidu.com"

    def start_requests(self):
        return self.start_url


# run.py
# run启动文件
from baidu import BaiduSpider
from bald_spider.core.engine import Engine

baidu_spider = BaiduSpider()
engine = Engine()
engine.start_spider(baidu_spider)
```

### 第二个阶段：引擎、下载器、抽取基类

> 注意这个地方：yield得到的是生成器 不是对应数据类型

在上个简单爬虫中，我们使用的是baidu的爬虫实例，以后我们还会有更多的微博爬虫实例，知乎爬虫实例等，所以我们要为我们的spider创建一个基类，所有的爬虫实例都是基类实例化的结果。

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404140020455-3b4d84.png)

```python
# 第二个部分主要是解决spider的基类的设计
# 同时兼容start_url是一个或者多个的问题

# baidu.py
from bald_spider.spider import Spider

class BaiduSpider(Spider):
    start_urls = ["https://www.baidu.com","https://www.baidu.com","https://www.baidu.com"]
    # 字符串兼容测试
    # start_url = "https://www.baidu.com"

    # def start_requests(self):
    #     return self.start_urls[0]

# run.py
from baidu import BaiduSpider
from bald_spider.core.engine import Engine

baidu_spider = BaiduSpider()
engine = Engine()
engine.start_spider(baidu_spider)

# spider.__init__.py
# 爬虫的基类
class Spider:
    def __init__(self):
        if not hasattr(self,"start_urls"):
            self.start_urls = []

    def start_requests(self):
        if self.start_urls:
            for url in self.start_urls:
                yield url
        else:
            if hasattr(self, "start_url") and isinstance(getattr(self,"start_url"),str):
                yield getattr(self,"start_url")
                
# download.py
import time
import requests

class Downloader:
    def __init__(self):
        pass

    def download(self, url):
        # response = requests.get(url)
        # print(response)
        # 模拟请求
        time.sleep(0.1)
        print("result")

# engine.py
from typing import Optional,Generator
from bald_spider.core.download import Downloader

class Engine:
    def __init__(self):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader = Downloader()
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None

    def start_spider(self, spider):
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_requests())
        self.crawl()

    def crawl(self):
        """爬虫的主要逻辑 """
        # 使用next取出迭代器中的数据
        while True:
            try:
                self.start_request = next(self.start_requests)
                self.downloader.download(self.start_request)
            except StopIteration:
                self.start_requests = None
            except Exception as exec:
                break
```

> 主要值得学习的地方：
>
> 1. 每个人写Spider不同将其抽取，形成**基类**
> 2. 使用`yield`(生成器)配合`next`的方式，完成初始**数组** or **字符串**类型的统一
> 3. 防止人为`复写`(不用yield , 使用return)的时候构造的数据不是generator，使用iter提前进行防范
> 4. `hasattr`和`getattr`的配合使用

### 第三个阶段：添加调度器

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404142916824-df93e4.png)

```python
# 使用异步的方式添加调度器，并在



# engine.py
from typing import Optional, Generator
from bald_spider.core.downloader import Downloader
from bald_spider.core.scheduler import Scheduler

class Engine:
    def __init__(self):
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader: Optional[Downloader] = Downloader()
        # 初始化调度器
        self.scheduler: Optional[Scheduler] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests: Optional[Generator] = None

    async def start_spider(self, spider):
        self.scheduler = Scheduler()
        if hasattr(self.scheduler, "open"):
            self.scheduler.open()
        self.downloader = Downloader()
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_requests())
        await self.crawl()

    async def crawl(self):
        """爬虫的主要逻辑 """
        # 使用next取出迭代器中的数据
        while True:
            # 出队列
            if (request := await self._get_next_request()) is not None:
                # 请求拿到，完成下载操作
                await self._crawl(request)
            else:
                try:
                    start_request = next(self.start_requests)
                except StopIteration:
                    self.start_requests = None
                except Exception as exec:
                    break
                else:
                    # 入队
                    await self.enqueue_request(start_request)

    async def _crawl(self,request):
        await self.downloader.download(request)

    async def enqueue_request(self, request):
        await self._schedule_request(request)

    async def _schedule_request(self,request):
        # 完成去重后，在调用scheduler的入队操作
        await self.scheduler.enqueue_request(request)

    async def _get_next_request(self):
        # scheduler的出队操作，拿请求
        return await self.scheduler.next_request()

    
# scheduler.py
import asyncio
from asyncio import PriorityQueue,TimeoutError
from typing import Optional

class Scheduler:
    def __init__(self):
        # 使用优先级队列，不同的请求的优先级不同
        self.request_queue: Optional[PriorityQueue] = None

    def open(self):
        self.request_queue = PriorityQueue()

    async def next_request(self):
        # 在get的方法中Remove and return an item from the queue.If queue is empty, wait until an item is available.
        # 也就是说当队列中没有元素的时候，就会一直等待直到有数据为止，所以一直阻塞中
        # 当我们使用coro进行接收的时候，其实拿到的是一个协程对象
        coro = self.request_queue.get()
        try:
            # 在这个地方我们对协程对象进行判断，获取不到，超时0.1s的话就直接将其设置成None,防止一直wait使得程序卡住
            request = await asyncio.wait_for(coro,timeout=0.1)
        except TimeoutError:
            return None
        return request

    async def enqueue_request(self,request):
        await self.request_queue.put(request)
        
        
# downloader.py
import asyncio

class Downloader:
    def __init__(self):
        pass

    async def download(self, url):
        # response = requests.get(url)
        # print(response)
        await asyncio.sleep(0.1)
        print("result")
        
# run.py
from baidu import BaiduSpider
import asyncio
from bald_spider.core.engine import Engine

async def run():
    baidu_spider = BaiduSpider()
    engine = Engine()
    await engine.start_spider(baidu_spider)

asyncio.run(run())
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240404144954149-599444.png)

- 更进一步简化代码

```python
# 对队列的操作进行封装，方便以后再次使用
# utils.pqueue.py
from asyncio import PriorityQueue,TimeoutError
import asyncio

class SpiderPriorityQueue(PriorityQueue):
    def __init__(self, maxsize=0):
        super(SpiderPriorityQueue,self).__init__(maxsize=maxsize)

    async def get(self):
        # 在get的方法中Remove and return an item from the queue.If queue is empty, wait until an item is available.
        # 也就是说当队列中没有元素的时候，就会一直等待直到有数据为止，所以一直阻塞中
        # 当我们使用coro进行接收的时候，其实拿到的是一个协程对象
        coro = super().get()
        try:
            # 在这个地方我们对协程对象进行判断，获取不到，超时0.1s的话就直接将其设置成None,防止一直wait使得程序卡住
            return await asyncio.wait_for(coro, timeout=0.1)
        except TimeoutError:
            return None

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
```

### 第四个阶段：封装请求类

其实这个地方是为了让我们进行判断是request还是data，最终决定是继续走spider还是直接解析入库，我们将两个部分封装成俩个类，方便我们进行类型判断

Request库的封装

```python
# download.py
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
    
# engine.py
import asyncio

from bald_spider.core.download import Downloader
from typing import Optional,Generator,Callable
from bald_spider.core.scheduler import Scheduler
from bald_spider.spider import Spider


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
        await self._fetch(request)

    # 重点
    async def _fetch(self,request):
        _response = await self.downloader.fetch(request)
        # 对这个地方的回调的使用需要注意下
        callback:Callable = request.callback or self.spider.parse
        callback(_response)
        
# spider.py
# 这个地方的导包的方式学习一下
from bald_spider import Request

class Spider:
    def __init__(self):
        if not hasattr(self,"start_urls"):
            self.start_urls = []

    def start_request(self):
        if self.start_urls:
            for url in self.start_urls:
                # 使用Request类对原始的url进行封装
                yield Request(url=url)
        else:
            if hasattr(self,"start_url") and isinstance(getattr(self,"start_url"),str):
                yield Request(url=getattr(self,"start_url"))

    # 基类中我们无需实现parse，就
    def parse(self,response):
        raise NotImplementedError
        
# http.request.py
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
        
# bald_spider.__init__.py
from bald_spider.http.request import Request

# baidu.py
from bald_spider.spider import Spider
class BaiduSpider(Spider):

    # start_url ="https://www.baidu.com"
    start_urls = ["https://www.baidu.com","https://www.baidu.com","https://www.baidu.com"]

    def parse(self,response):
        print("parse",response)
```

对于parse的不同书写方式，会生成不同的数据类型，用户自行编写，各种情况我们都需要考虑

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240313181115786-207b3f.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240313181150506-f82bc8.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240313181228295-db38f8.png)

bug查证

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240313182955940-7e9eaa.png)

> 'async_generator' object is not iterable
>
> ![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240313183226969-3ad1e5.png)
>
> ![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240313183637692-df7bb0.png)

```python
# engine.py
import asyncio
from inspect import iscoroutine

from bald_spider.core.download import Downloader
from typing import Optional,Generator,Callable
from bald_spider.core.scheduler import Scheduler
from bald_spider.spider import Spider
from bald_spider.utils.spider import transform


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
            async for output in outputs:
                print(output)


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

# execption.py
class TransformTypeError(TypeError):
    pass

# utils.spider.py
from inspect import isgenerator,isasyncgen
from bald_spider.execptions import TransformTypeError

async def transform(func_result):
    # 这个地方就是对异步生成器和同步生成器进行兼容，都转化成异步生成器
    if isgenerator(func_result):
        for r in func_result:
            yield r
    elif isasyncgen(func_result):
        async for r in func_result:
            yield r
    else:
        raise TransformTypeError("callback return value must be generator or asyncgen")
        
# baidu.py
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
```

