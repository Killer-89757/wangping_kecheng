# 猿人学-爬虫框架课程(6)

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
  - middleware  **中间件**
    - \_\_init\_\_.py  **中间件基类**
    - middleware_manager.py   **中间件管理类**
  - settings：存放spider基类的地方
    - \__init__.py     
    - default_settings.py     **默认配置**
    - settings_manager.py     **配置管理器**
  - utils: 工具包
    - \__init__.py 
    - date  **处理时间工具**
    - pqueue.py  **自己封装的优先级队列**
    - spider.py  **爬虫工具：生成器转化工具等**
    - project.py  **获取用户配置工具**
    - log.py   **全局日志系统**
    - system.py  **Aio代理异常处理**
  - \__init__.py       **方便导包**
  - execption.py  **自定义异常**
  - task_manager.py  **任务管理**
  - crawler.py    **工程启动封装**
  - stats_collector.py **统计信息封装**
- test：测试爬虫的代码
  - baidu_spider
    - spiders  用户爬虫
      - \__init__.py 
      - baidu.py  **爬虫实例**
      - weibo.py  **爬虫实例**
    - \__init__.py 
    - items.py  **用户数据类**
    - run.py     **项目启动文件**
    - middleware.py    **用户中间件**
    - settings.py  **用户配置文件**
  - misc
    - demo1.py **测试信号量**
    - demo2.py **测试信号量**
    - demo3.py **测试模块信息(获取配置信息)**
    - demo4.py **\_\_getitem__的使用**
    - demo5.py **\_\_getattr__和\_\_getattribute\_\_的使用**
    - demo6.py  **测试下载器记录**
    - demo7.py  **测试setdefault**
    - demo8.py  **middleware_method示例**

### 第二十四阶段：中间件基础构建

中间件架构

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240407002045519-c99e81.png)

在进行request_handler进行处理，到downloader的过程中失败，那么我们等同于**下载失败**，直接走exception_handler的流程

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240407003104190-8556ca.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240407015038903-973590.png)

```python
# middleware.__init__py

class BaseMiddleware:
    def process_request(self):
        # 请求的预处理
        pass

    def process_response(self):
        # 响应的预处理
        pass

    def process_execption(self):
        # 异常处理
        pass

    @classmethod
    def create_instance(cls, crawler):
        return cls()

# middleware_manager.py
from typing import List, Dict
from types import MethodType

from bald_spider.utils.log import get_logger
from bald_spider.utils.project import load_class
from bald_spider.execptions import MiddlewareInitError
from pprint import pformat
from collections import defaultdict
from bald_spider.middleware import BaseMiddleware


class MiddlewareManager:
    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get("LOG_LEVEL"))
        self.middlewares: List = []
        self.methods: Dict[str:List[MethodType]] = defaultdict(list)
        middlewares = self.crawler.settings.getlist("MIDDLEWARES")
        self._add_middleware(middlewares)
        self._add_method()
        breakpoint()

    def _add_method(self):
        for middleware in self.middlewares:
            if hasattr(middleware,"process_request"):
                if self._validate_method("process_request",middleware):
                    self.methods["process_request"].append(middleware.process_request)
            if hasattr(middleware,"process_response"):
                if self._validate_method("process_response",middleware):
                    self.methods["process_response"].append(middleware.process_response)
            if hasattr(middleware,"process_execption"):
                if self._validate_method("process_execption",middleware):
                    self.methods["process_execption"].append(middleware.process_execption)

    def _add_middleware(self, middlewares):
        enable_middlewares = [m for m in middlewares if self._validate_middleware(m)]
        if enable_middlewares:
            self.logger.info(f"enable middlewares:\n {pformat(enable_middlewares)}")

    def _validate_middleware(self, middleware):
        middleware_cls = load_class(middleware)
        if not hasattr(middleware_cls, "create_instance"):
            raise MiddlewareInitError(
                f"Middleware Init failed,must inherit from `BaseMiddleware` or must have `create_instance` method")
        instance = middleware_cls.create_instance(self.crawler)
        self.middlewares.append(instance)
        return True

    @classmethod
    def create_instance(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @staticmethod
    def _validate_method(method_name,middleware):
        method = getattr(type(middleware), method_name)
        base_method = getattr(BaseMiddleware,method_name)
        if method == base_method:
            return False
        else:
            return True

# exception.py
class MiddlewareInitError(Exception):
    pass

# settings.py
MIDDLEWARES = [
    "test.baidu_spider.middleware.TestMiddleware",
    "test.baidu_spider.middleware.TestMiddleware1",
]

# middleware.py
from bald_spider.middleware import BaseMiddleware

class TestMiddleware(BaseMiddleware):

    def __init__(self):
        pass

    def process_request(self):
        # 请求的预处理
        pass

    def process_response(self):
        # 响应的预处理
        pass

    def process_execption(self):
        # 异常处理
        pass

class TestMiddleware1(BaseMiddleware):
    def process_response(self):
        # 响应的预处理
        pass

    def process_execption(self):
        # 异常处理
        pass
```



