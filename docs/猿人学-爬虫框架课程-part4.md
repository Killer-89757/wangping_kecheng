# 猿人学-爬虫框架课程(4)

## 项目简介

项目：wangping_kecheng

猿人学王平老师的爬虫系统架构的代码

课程环境：python 3.10

## 项目实现

创建两个包：

- bald_spider：项目代码的地方
  - core:核心代码存放处
    - downloader **下载器文件夹**
      - \__init__.py  **下载器基类和元类**
      - aiohttp_downloader.py **Aio下载器**
      - httpx_downloader.py  **httpx下载器**
    - \__init__.py 
    - engine.py        **引擎**
    - scheduler.py   **调度器**
    - processor.py   **数据处理器**
  - spider：存放spider基类的地方
    - \__init__.py     **基类**
  - http：存放spider基类的地方
    - \__init__.py     
    - request.py     **请求类**
    - response.py     **响应类**
  - items  数据
    - \_\_init\_\_.py  **Item元类**
    - items.py   **数据类**
  - settings：存放spider基类的地方
    - \__init__.py     
    - default_settings.py     **默认配置**
    - settings_manager.py     **配置管理器**
  - utils: 工具包
    - \__init__.py 
    - pqueue.py  **自己封装的优先级队列**
    - spider.py  **爬虫工具：生成器转化工具等**
    - project.py  **获取用户配置工具**
    - log.py   **全局日志系统**
    - system.py  **Aio代理异常处理**
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
    - items.py  **用户数据类**
    - run.py     **项目启动文件**
    - settings.py  **用户配置文件**
  - misc
    - demo1.py **测试信号量**
    - demo2.py **测试信号量**
    - demo3.py **测试模块信息(获取配置信息)**
    - demo4.py **\_\_getitem__的使用**
    - demo5.py **\_\_getattr__和\_\_getattribute\_\_的使用**
    - demo6.py  **测试下载器记录**

### 第十六阶段：Response(第一版本)

直接排除requests包，是因为他和asyncio不兼容

需要使用支持异步的下载包，`aiohttp` or `httpx`

**aiohttp httpx 插件化：插拔器，即插即用**

思路：

1. 在Engine中需要用到fetch、idle方法，需要分别实现

2. 我们生成的response是不同的，所以我们需要进行兼容

3. 我们根据配置文件实现动态加载

定义一个Response类，实现两种下载方式的结果统一

```python
# request.py
from typing import Dict, Optional, Callable


class Request:
    def __init__(
            self, url: str, *,
            headers: Optional[Dict] = None,
            callback: Callable = None,
            priority: int = 0,
            method: str = "GET",
            cookies: Optional[Dict] = None,
            proxy: Optional[Dict] = None,
            body="",
            encoding="utf-8",
            # 和请求无关，但是和运行流程有关
            meta:Optional[Dict] = None
    ):
        self.url = url
        self.headers = headers
        self.callback = callback
        self.priority = priority
        self.method = method
        self.cookies = cookies
        self.proxy = proxy
        self.body = body
        self.encoding = encoding
        self._meta = meta if meta is not None else {}

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        return f"{self.url} {self.method}"

    @property
    def meta(self):
        return self._meta

# response.py
from typing import Dict, Optional
from bald_spider import Request
import ujson
import re
from bald_spider.execptions import DecodeError
from urllib.parse import urljoin as _urljoin
from parsel import Selector

class Response:
    def __init__(
            self,
            url: str,
            *,
            request: Request,
            headers: Optional[Dict] = None,
            body: bytes = b"",
            status: int = 200
    ):
        self.url = url
        self.request = request
        self.headers = headers
        self.body = body
        self.status = status
        self.encoding = request.encoding
        # 设置缓存
        self._text_cache = None
        self._selector = None

    @property
    def text(self):
        """
        这个地方实际上是我们得到的body是bytes类型，但是我们得到数据需要转化成数据类型
        但是text = body.decode(),我们并不想存储两份，定义这个属性方法，需要用到的时候直接调用就行
        """
        if self._text_cache:
            return self._text_cache
        try:
            # 使用默认的encoding并不一定能decode成功
            self._text_cache = self.body.decode(self.encoding)
        except UnicodeDecodeError:
            try:
                # 从网页headers中的Content-Type处可以拿到encoding尝试进行decode
                _encoding_re = re.compile(r"charset=([\w-]+)", flags=re.I)
                _encoding_string = self.headers.get("Content-Type", "") or self.headers.get("content-type", "")
                _encoding = _encoding_re.search(_encoding_string)
                if _encoding:
                    _encoding = _encoding.group(1)
                    self._text_cache = self.body.decode(self.encoding)
                else:
                    raise DecodeError(f"{self.request} {self.request.encoding} error")
            except UnicodeDecodeError as exc:
                raise UnicodeDecodeError(
                    exc.encoding, exc.object, exc.start, exc.end, f"{self.request}"
                )
        return self._text_cache

    def json(self):
        return ujson.loads(self.text)

    def urljoin(self, url):
        return _urljoin(self.url, url)

    def xpath(self,xpath_string):
        if self._selector is None:
            self._selector = Selector(self.text)
        return self._selector.xpath(xpath_string)

    def __str__(self):
        return f"<{self.status}> {self.url}"

    @property
    def meta(self):
        return self.request.meta

# execptions.py
class DecodeError(Exception):
    pass
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405220712212-4c607e.png)

### 第十七阶段：使用aiohttp完善下载器

```python
# downloader.py
import asyncio
from typing import Final, Set, Optional
import random
# 下上文管理器的包
from contextlib import asynccontextmanager
from bald_spider import Response
from aiohttp import ClientSession, TCPConnector, BaseConnector, ClientTimeout, ClientResponse,TraceConfig
from bald_spider.utils.log import get_logger


# aiohttp httpx 插件化：插拔器，即插即用
# 思路：
# 1.在Engine中需要用到fetch、idle方法，需要分别实现
# 2.我们生成的response是不同的，所以我们需要进行兼容
# 3.我们根据配置文件实现动态加载

class ActiveRequestManager:
    def __init__(self):
        self._active: Final[Set] = set()

    def add(self, request):
        # print("add", request)
        self._active.add(request)

    def remove(self, request):
        # print("remove", request)
        self._active.remove(request)

    @asynccontextmanager
    async def __call__(self, request):
        try:
            yield self.add(request)
        finally:
            self.remove(request)

    def __len__(self):
        return len(self._active)


class Downloader:
    def __init__(self, crawler):
        self._active = ActiveRequestManager()
        self.session: Optional[ClientSession] = None
        self.connector: Optional[BaseConnector] = None
        self._verify_ssl: Optional[bool] = None
        self._timeout: Optional[ClientTimeout] = None
        self.crawler = crawler
        self.request_method = {
            "get": self._get,
            "post": self._post,
        }
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get("LOG_LEVEL"))
        self._use_session:Optional[bool] = None

    def open(self):
        self.logger.info(f"{self.crawler.spider} <downloader class:{type(self).__name__}>"
                         f"<concurrency:{self.crawler.settings.getint('CONCURRENCY')}>")
        request_time = self.crawler.settings.getint("REQUEST_TIMEOUT")
        self._timeout = ClientTimeout(total=request_time)
        self._verify_ssl = self.crawler.settings.getbool("VERIFY_SSL")
        self._use_session = self.crawler.settings.getbool("USE_SESSION")
        if self._use_session:
            self.connector = TCPConnector(verify_ssl=self._verify_ssl)
            trace_config = TraceConfig()
            trace_config.on_request_start.append(self.request_start)
            # 存在一个待解决的问题：当前我们的下载使用的都是同一个session,在一些场景中，需要重启新session下载
            self.session = ClientSession(connector=self.connector, timeout=self._timeout,trace_configs=[trace_config])

    async def fetch(self, request) -> Optional[Response]:
        # 其实在这个地方，请求来的时候我们加入到队列中，当请求结束后，我们从队列中删除，可以使用上下文管理器来进行操作
        async with self._active(request):
            response = await self.download(request)
            return response

    async def download(self, request) -> Response:
        # 实际的下载
        try:
            # 配置参数中使用统一个session的话，使用self.session
            if self._use_session:
                response = await self.send_request(self.session,request)
                body = await response.content.read()
            # 不是的话，我们需要按照上面的方式进行创建session
            else:
                connector = TCPConnector(verify_ssl=self._verify_ssl)
                trace_config = TraceConfig()
                trace_config.on_request_start.append(self.request_start)
                async with ClientSession(
                        connector=connector, timeout=self._timeout,trace_configs=[trace_config]
                ) as session:
                    response = await self.send_request(session,request)
                    body = await response.content.read()
        except Exception as exc:
            self.logger.error(f"Error druing request:{exc}")
            raise exc
        return self.structure_response(request,response,body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=request.url,
            headers=dict(response.headers),
            status=response.status,
            body=body,
            request=request
        )

    async def send_request(self,session,request) -> ClientResponse:
        return await self.request_method[request.method.lower()](session,request)

    @staticmethod
    async def _get(session,request) -> ClientResponse:
        response = await session.get(
            request.url, headers=request.headers,
            cookies=request.cookies, proxy=request.proxy
        )
        return response

    @staticmethod
    async def _post(session,request) -> ClientResponse:
        response = await session.post(
            request.url, data=request.body, headers=request.headers,
            cookies=request.cookies, proxy=request.proxy
        )
        return response

    async def request_start(self,_session,_trace_config_ctx,params):
        # 在trace_config中进行设置，我们在请求开始之前就会调用当前的方法
        self.logger.debug(f"request downloading:{params.url}，method:{params.method}")


    def idle(self):
        return len(self) == 0

    def __len__(self):
        return len(self._active)

    async def close(self):
        if self.connector:
            await self.connector.close()
        if self.session:
            await self.session.close()

# engine.py
class Engine:
    async def start_spider(self, spider):
        # 打开开关
        self.running = True
        self.logger.info(f"bald_spider started.(project name:{self.settings.get('PROJECT_NAME')})")

        # 得到spider
        self.spider = spider

        # 初始化调度器和下载器、数据处理器
        self.scheduler = Scheduler()
        self.processor = Processor(self.crawler)
        if hasattr(self.scheduler,"open"):
            self.scheduler.open()
        self.downloader = Downloader(self.crawler)
        if hasattr(self.downloader,"open"):
            self.downloader.open()
        # 使用iter将任何变成类型变成generator、防止人为复写(不用yield,使用return)的时候构造的数据不是generator
        self.start_requests = iter(spider.start_request())
        await self._open_spider()

    

    async def crawl(self):
        """主逻辑"""
        while self.running:
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    # 使用next取出迭代器中的数据
                    start_request = next(self.start_requests)
                # 这个地方分开两次捕获异常，其实是为了确定初始请求是不是请求完整
                except StopIteration:
                    self.start_requests = None
                except Exception as exc:
                    # 1.发起请求的task要运行完毕
                    # 2.调度器是否空闲
                    # 3.下载器是否空闲
                    if not await self._exit():
                        continue
                    self.running = False
                    if self.start_requests is not None:
                        self.logger.error(f"Error during start_requests:{exc}")
                else:
                    # 入队
                    await self.enqueue_request(start_request)
        if not self.running:
            await self.close_spider()


   
    async def _crawl(self,request):
        # 因为在task这个地方完成了两件事，下载和处理输出，所以当任务完成的时候，下载也一定完成了
        async def crawl_task():
            outputs = await self._fetch(request)
            # todo 处理output
            if outputs:
                await self._handle_spider_output(outputs)
        await self.task_manager.semaphore.acquire()
        self.task_manager.create_task(crawl_task())

   

    async def _exit(self):
        """
        其实在这个地方有一点错误就是我们先判断调度器和下载器，为空直接返回结束，但是任务可能还在运行
        三者应该是共同决定是否结束的条件
        """
        # 调度器是否空闲
        # 任务列表中是否为空(下载器是否空闲,包含关系)
        # 数据处理队列为空
        # 保留下载器判断的原因是：必须要明确下载器状态，不能只从代码包含性的角度考量
        if self.scheduler.idle() and self.downloader.idle() and self.task_manager.all_done() and self.processor.idle():
            return True
        return False

    async def close_spider(self):
        await self.downloader.close()
        
# default_settings.py
VERIFY_SSL = True
REQUEST_TIMEOUT = 60
USE_SESSION = True

# baidu.py
from bald_spider.spider import Spider
from bald_spider import Request
from items import BaiduItem   # type:ignore

class BaiduSpider(Spider):
    def parse_page(self,response):
        # print("parse_page",response)
        for i in range(3):
            url = "https://www.baidu.com"
            meta = {"test":"waws"}
            request = Request(url=url,callback=self.parse_detail,meta=meta)
            yield request

    def parse_detail(self,response):
        # print("parse_detail",response)
        # print(response.text)
        item = BaiduItem()
        item["url"] = "baidu.com"
        item["title"] = "百度首页"
        # item.title = "111"
        yield item
```

验证：保留下载器状态是不是会影响服务性能（并不会）

```python
# demo6.py
from timeit import timeit

s = set()

def demo():
    s.add(1)
    s.remove(1)

def run():
    print(timeit(demo,number=1000000))

run()
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405232700488-11a047.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406000022160-d5a7df.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406001812482-c641d5.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406002742409-bfcddd.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406004049786-66be30.png)

### 第十八阶段：使用httpx完善下载器

```python
# downloader.py
import asyncio
from typing import Final, Set, Optional
import httpx

class HttpxDownloader:
    def __init__(self, crawler):
        self.crawler = crawler
        self._active = ActiveRequestManager()
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get("LOG_LEVEL"))

        self._client:Optional[httpx.AsyncClient] = None
        self._timeout:Optional[httpx.Timeout]= None

    def open(self):
        self.logger.info(f"{self.crawler.spider} <downloader class:{type(self).__name__}>"
                         f"<concurrency:{self.crawler.settings.getint('CONCURRENCY')}>")
        request_time = self.crawler.settings.getint("REQUEST_TIMEOUT")
        self._timeout = httpx.Timeout(timeout=request_time)

    async def fetch(self, request) -> Optional[Response]:
        # 其实在这个地方，请求来的时候我们加入到队列中，当请求结束后，我们从队列中删除，可以使用上下文管理器来进行操作
        async with self._active(request):
            response = await self.download(request)
            return response

    async def download(self, request) -> Optional[Response]:
        # 实际的下载
        try:
            proxies = request.proxy
            async with httpx.AsyncClient(timeout=self._timeout,proxies=proxies) as client:
                self.logger.debug(f"request downloading:{request.url}，method:{request.method}")
                response = await client.request(
                    request.method,request.url,headers=request.headers,cookies=request.cookies,data=request.body
                )
                body = await response.aread()
        except Exception as exc:
            self.logger.error(f"Error druing request:{exc}")
            return None
        return self.structure_response(request,response,body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=request.url,
            headers=dict(response.headers),
            status=response.status_code,
            body=body,
            request=request
        )

    def idle(self):
        return len(self) == 0

    def __len__(self):
        return len(self._active)

    async def close(self):
        pass

# engine.py
from bald_spider.core.download import Downloader,HttpxDownloader

class Engine:
    def __init__(self,crawler):
        self.downloader:Optional[HttpxDownloader] = None

    async def start_spider(self, spider):
        self.downloader = HttpxDownloader(self.crawler)
```

### 第十九阶段：将下载器插件化配置

```python
# project.py
def load_class(_path):
    """
    根据配置文件的路径动态的加载下载类
    """
    if not isinstance(_path,str):
        if callable(_path):
            return _path
        else:
            raise TypeError(f"args expected string or object,got: {type(_path)}")
    module, name = _path.rsplit(".", 1)
    mod = import_module(module)
    try:
        cls = getattr(mod, name)
    except Exception:
        raise NameError(f"Module {module!r} does not define any object named {name!r}")
    return cls

# engine.py
from bald_spider.utils.project import load_class

class Engine:
    async def start_spider(self, spider):
        downloader_cls = load_class(self.settings.get("DOWNLOADER"))
        self.downloader = downloader_cls(self.crawler)
  
# defualt_settings.py
DOWNLOADER = "bald_spider.core.download.HttpxDownloader"
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406020512420-f275b9.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406020728404-1ae4eb.png)

### 第二十阶段：规范下载器代码

```python
# 去掉原有的downloader.py文件
# core下建立downloader
# core.downloader.__init__.py
from typing import Final, Set, Optional
from contextlib import asynccontextmanager
from abc import abstractmethod, ABCMeta

from bald_spider import Response, Request
from bald_spider.utils.log import get_logger


class ActiveRequestManager:
    def __init__(self):
        self._active: Final[Set] = set()

    def add(self, request):
        # print("add", request)
        self._active.add(request)

    def remove(self, request):
        # print("remove", request)
        self._active.remove(request)

    @asynccontextmanager
    async def __call__(self, request):
        try:
            yield self.add(request)
        finally:
            self.remove(request)

    def __len__(self):
        return len(self._active)

class DownloaderMeta(ABCMeta):
    """
    解决一个问题：就是我没有继承基类，但是我实现了你基类所有的方法，这个时候其实也是可行的
    """
    # 当我们调用issubclass的时候，默认调用的方法是__subclasscheck__
    def __subclasscheck__(self, subclass):
        required_method = ("fetch","download","create_instance","close","idle")
        # 当四个方法同时存在且都调用的情况下，才算是子类
        is_subclass = all(
            hasattr(subclass,method) and callable(getattr(subclass,method,None)) for method in required_method
        )
        return is_subclass

class DownloaderBase(metaclass=DownloaderMeta):
    def __init__(self,crawler):
        self.crawler = crawler
        self._active = ActiveRequestManager()
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get("LOG_LEVEL"))

    @classmethod
    def create_instance(cls,*args,**kwargs):
        return cls(*args,**kwargs)

    def open(self):
        self.logger.info(f"{self.crawler.spider} <downloader class:{type(self).__name__}>"
                         f"<concurrency:{self.crawler.settings.getint('CONCURRENCY')}>")

    async def fetch(self, request) -> Optional[Response]:
        # 其实在这个地方，请求来的时候我们加入到队列中，当请求结束后，我们从队列中删除，可以使用上下文管理器来进行操作
        async with self._active(request):
            response = await self.download(request)
            return response

    @abstractmethod
    async def download(self,request:Request) -> Response:
        pass

    def idle(self):
        return len(self) == 0

    def __len__(self):
        return len(self._active)

    async def close(self):
        pass
# core.downloader.aiohttp_downloader.py

from typing import Optional

from bald_spider import Response
from aiohttp import ClientSession, TCPConnector, BaseConnector, ClientTimeout, ClientResponse,TraceConfig
from bald_spider.utils.log import get_logger
from bald_spider.core.downloader import DownloaderBase

class AioDownloader(DownloaderBase):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.session: Optional[ClientSession] = None
        self.connector: Optional[BaseConnector] = None
        self._verify_ssl: Optional[bool] = None
        self._timeout: Optional[ClientTimeout] = None
        self.trace_config:Optional[TraceConfig] = None
        self.request_method = {
            "get": self._get,
            "post": self._post,
        }

        self._use_session:Optional[bool] = None

    def open(self):
        super().open()
        request_time = self.crawler.settings.getint("REQUEST_TIMEOUT")
        self._timeout = ClientTimeout(total=request_time)
        self._verify_ssl = self.crawler.settings.getbool("VERIFY_SSL")
        self._use_session = self.crawler.settings.getbool("USE_SESSION")
        self.trace_config = TraceConfig()
        self.trace_config.on_request_start.append(self.request_start)
        if self._use_session:
            self.connector = TCPConnector(verify_ssl=self._verify_ssl)
            # 存在一个待解决的问题：当前我们的下载使用的都是同一个session,在一些场景中，需要重启新session下载
            self.session = ClientSession(connector=self.connector, timeout=self._timeout,trace_configs=[self.trace_config])

    async def download(self, request) -> Optional[Response]:
        # 实际的下载
        try:
            # 配置参数中使用统一个session的话，使用self.session
            if self._use_session:
                response = await self.send_request(self.session,request)
                body = await response.content.read()
            # 不是的话，我们需要按照上面的方式进行创建session
            else:
                connector = TCPConnector(verify_ssl=self._verify_ssl)
                async with ClientSession(
                        connector=connector, timeout=self._timeout,trace_configs=[self.trace_config]
                ) as session:
                    response = await self.send_request(session,request)
                    body = await response.content.read()
        except Exception as exc:
            self.logger.error(f"Error druing request:{exc}")
            return None
        return self.structure_response(request,response,body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=request.url,
            headers=dict(response.headers),
            status=response.status,
            body=body,
            request=request
        )

    async def send_request(self,session,request) -> ClientResponse:
        return await self.request_method[request.method.lower()](session,request)

    @staticmethod
    async def _get(session,request) -> ClientResponse:
        response = await session.get(
            request.url, headers=request.headers,
            cookies=request.cookies, proxy=request.proxy
        )
        return response

    @staticmethod
    async def _post(session,request) -> ClientResponse:
        response = await session.post(
            request.url, data=request.body, headers=request.headers,
            cookies=request.cookies, proxy=request.proxy
        )
        return response

    async def request_start(self,_session,_trace_config_ctx,params):
        # 在trace_config中进行设置，我们在请求开始之前就会调用当前的方法
        self.logger.debug(f"request downloading:{params.url}，method:{params.method}")

    async def close(self):
        if self.connector:
            await self.connector.close()
        if self.session:
            await self.session.close()
            
# core.downloader.httpx_downloader.py
from typing import Optional

from bald_spider import Response
import httpx
from bald_spider.core.downloader import DownloaderBase


class HttpxDownloader(DownloaderBase):
    def __init__(self, crawler):
        super().__init__(crawler)

        self._client: Optional[httpx.AsyncClient] = None
        self._timeout: Optional[httpx.Timeout] = None

    def open(self):
        request_time = self.crawler.settings.getint("REQUEST_TIMEOUT")
        self._timeout = httpx.Timeout(timeout=request_time)

    async def download(self, request) -> Optional[Response]:
        # 实际的下载
        try:
            proxies = request.proxy
            async with httpx.AsyncClient(timeout=self._timeout, proxies=proxies) as client:
                self.logger.debug(f"request downloading:{request.url}，method:{request.method}")
                response = await client.request(
                    request.method, request.url, headers=request.headers, cookies=request.cookies, data=request.body
                )
                body = await response.aread()
        except Exception as exc:
            self.logger.error(f"Error druing request:{exc}")
            return None
        return self.structure_response(request, response, body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=request.url,
            headers=dict(response.headers),
            status=response.status_code,
            body=body,
            request=request
        )

# engine.py
import asyncio
from inspect import iscoroutine

from typing import Optional,Generator,Callable,Final,Set
from bald_spider.core.scheduler import Scheduler
from bald_spider.spider import Spider
from bald_spider.utils.spider import transform
from bald_spider.execptions import OutputError
from bald_spider.http.request import Request
from bald_spider.task_manager import TaskManager
from bald_spider.core.processor import Processor
from bald_spider.items.items import Item
from bald_spider.utils.log import get_logger
from bald_spider.utils.project import load_class
from bald_spider.core.downloader import DownloaderBase


class Engine:
    def __init__(self,crawler):
        self.downloader:Optional[DownloaderBase] = None
        

    def _get_downloader(self):
        downloader_cls = load_class(self.settings.get("DOWNLOADER"))
        # 暴漏下载器给用户可自行定义，这样的话，用户未必遵守规定
        # 为了代码的规范，我们使得下载器必须要继承自DownloaderBase
        if not issubclass(downloader_cls,DownloaderBase):
            raise TypeError(f"The downloader class ({self.settings.get('DOWNLOADER')})"
                            f"does not fully implemented required interface")
        return downloader_cls

    async def start_spider(self, spider):
        downloader_cls = self._get_downloader()
        self.downloader = downloader_cls.create_instance(self.crawler)

# utils.system.py
# 使用AioDownloader在windows系统下挂代理会产生问题
import asyncio
import platform
system = platform.system().lower()
if system == "windows":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
 
# default_settings.py
# DOWNLOADER = "bald_spider.core.downloader.aiohttp_downloader.AioDownloader"
DOWNLOADER = "bald_spider.core.downloader.httpx_downloader.HttpxDownloader"
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406031252926-4dcbb0.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406032553912-450a6f.png)