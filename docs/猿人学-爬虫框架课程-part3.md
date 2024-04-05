# 猿人学-爬虫框架课程(3)

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
    - processor.py   **数据处理器**
  - spider：存放spider基类的地方
    - \__init__.py     **基类**
  - http：存放spider基类的地方
    - \__init__.py     
    - request.py     **请求类**
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

### 第十一阶段：Item数据类型(类属性方式)

前面封装了Request类型，留着数据类型未处理，这个地方就是对items进行封装

```python
# items.items.py
from bald_spider.items import Field

class Item:
    # FIELDS:dict = dict()

    def __init__(self):
        self.FIELDS = {}
        # print(self.__class__.__dict__)
        # {'__module__': '__main__', 'url': {}, 'title': {}, '__doc__': None}
        for cls_attr,value in self.__class__.__dict__.items():
            if isinstance(value,Field):
                self.FIELDS[cls_attr] = value
        print(self.FIELDS)
        self._value = {}

    def __setitem__(self, key, value):
        if key in self.FIELDS:
            self._value[key] = value
        else:
            raise KeyError(f"{self.__class__.__name__} dose not support field:{key}")

    def __getitem__(self, item):
        pass

    def __repr__(self):
        return str(self._value)

if __name__ == "__main__":
    class TestItem(Item):
        url = Field()
        title = Field()

    class TestItem2(Item):
        name = Field()
    testItem = TestItem()
    testItem2 = TestItem2()
    # testItem["url"] = "1111"
    # testItem["title"] = "title"
    # print(testItem)

# items.__init__.py
class Field(dict):
    pass

# baidu.py
from bald_spider.spider import Spider
from bald_spider import Request
from items import BaiduItem   # type:ignore

class BaiduSpider(Spider):

    def parse_detail(self,response):
        # print("parse_detail",response)
        item = BaiduItem()
        item["url"] = "baidu.com"
        item["title"] = "百度首页"
        # item["aaa"] = ""

# items.py
from bald_spider.items import Field
from bald_spider import Item


class BaiduItem(Item):
    """
    作用：
    1.让写代码的人一眼看过去就知道有哪些字段
    2.在未规定的字段出现的时候，及时抛出异常
    """
    url = Field()
    title = Field()
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405102830799-dc84f9.png)

不能使用简单粗暴的方式`__class__.__dict__`进行字段处理

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405105501047-913496.png)

将类属性替换成实例属性可以解决，但是不够好：

- 我们`__class__.__dict__`的使用简单粗暴，逻辑行的通，但是不够严谨
- 

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405105826323-2ff794.png)

### 第十二阶段：Item数据类型(元类方式)

上面我们使用的类属性的方式

```python
# items.__init__.py
from abc import ABCMeta
class Field(dict):
    pass

class ItemMeta(ABCMeta):
    def __new__(mcs,name,bases,attrs):
        # mcs:metaclass
        # name:Item 类的名称
        # bases: 继承类的父类
        # attrs: 类属性
        field = {}
        for key,value in attrs.items():
            if isinstance(value,Field):
                field[key] = value
        cls_instance = super().__new__(mcs,name,bases,attrs)
        cls_instance.FIELDS = field
        return cls_instance

# items.items.py
from pprint import pformat
from bald_spider.items import Field, ItemMeta
from collections.abc import MutableMapping
from copy import deepcopy


class Item(MutableMapping, metaclass=ItemMeta):
    FIELDS: dict

    def __init__(self):
        self._value = {}

    # __new__可以在调用__init__之前进行调用

    def __setitem__(self, key, value):
        if key in self.FIELDS:
            self._value[key] = value
        else:
            raise KeyError(f"{self.__class__.__name__} dose not support field:{key}")

    def __getitem__(self, item):
        return self._value[item]

    def __delitem__(self, key):
        del self._value[key]

    def __setattr__(self, key, value):
        # 在这个地方其实是放self._value通过
        if not key.startswith("_"):
            raise AttributeError(f"use item[{key!r}] = {value!r} to set field value")
        super().__setattr__(key, value)

    def __getattr__(self, item):
        # 在这个地方不使用的原因是，属性存在，只是为{}，不会调用__getattr__
        raise AttributeError(f"{self.__class__.__name__} does not support field:{item}."
                             f"please add the `{item}` field to the {self.__class__.__name__},"
                             f"and use item[{item!r}] to get field value")

    def __getattribute__(self, item):
        field = super().__getattribute__("FIELDS")
        # 能进入下面的判断说明属性在field中，不能使用"."方式调用抛出异常
        if item in field:
            raise AttributeError(f"use item[{item!r}] to get field value")
        # 若进不去，就是压根没有这个属性
        else:
            return super().__getattribute__(item)

    def __repr__(self):
        return pformat(dict(self))

    __str__ = __repr__

    def __iter__(self):
        return iter(self._value)

    def __len__(self):
        return len(self._value)

    def to_dict(self):
        return dict(self)

    def copy(self):
        return deepcopy(self)

if __name__ == "__main__":
    class TestItem(Item):
        url = Field()
        title = Field()


    class TestItem2(Item):
        name = Field()


    testItem = TestItem()
    # testItem2 = TestItem2()
    testItem["url"] = "1111"
    # testItem["title"] = "title"
    print(testItem["url"])
    # 以’.‘的方式去设置值的行为，我们需要禁止
    # testItem.url = 333
    # 以’.‘的方式去获取值的行为，我们需要禁止
    # print(testItem.url)
    print(testItem.xxx)
    
    
# engine.py
from bald_spider.items.items import Item

class Engine:
    
    async def _handle_spider_output(self,outputs):
        """
        在这个地方对输出的结果进行判断，数据走管道，请求重新回到spider
        """
        async for spider_output in outputs:
            if isinstance(spider_output,Request):
                await self.enqueue_request(spider_output)
            # 在这个地方打开输出Item类型数据的判断
            elif isinstance(spider_output, Item):
                print(spider_output)
            else:
                raise OutputError(f"{type(self.spider)} must return Request or Item")

# baidu.py
from items import BaiduItem   # type:ignore

class BaiduSpider(Spider):
    def parse_detail(self,response):
        # print("parse_detail",response)
        item = BaiduItem()
        item["url"] = "baidu.com"
        item["title"] = "百度首页"
        # item.title = "111"
        yield item

# weibo.py
from items import WeiboItem # type:ignore

class WeiboSpider(Spider):
    def parse_detail(self,response):
        # print("parse_detail",response)
        item = WeiboItem()
        item["url"] = "weibo.com"
        item["title"] = "微博首页"
        # item["aaa"] = ""
        yield item

# items.py
from bald_spider.items import Field
from bald_spider import Item


class BaiduItem(Item):
    """
    作用：
    1.让写代码的人一眼看过去就知道有哪些字段
    2.在未规定的字段出现的时候，及时抛出异常
    """
    url = Field()
    title = Field()

class WeiboItem(Item):
    """
    作用：
    1.让写代码的人一眼看过去就知道有哪些字段
    2.在未规定的字段出现的时候，及时抛出异常
    """
    url = Field()
    title = Field()
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405114122107-92c4ac.png)

可以使用`__setattr__`的方式对"."的赋值方式进行拦截

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405115735470-f0ed32.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405120311577-a843c3.png)

在属性不存在，使用"."的方式进行获取的时候，回触发`__getattr__`方法

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405121129806-405e7b.png)

`__getattribute__`属性拦截器，只要访问属性就会调用该方法

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405121833932-325945.png)

`__getattribute__`这个方法很容易触发无限递归，需要谨慎使用

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405122239600-7d378d.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405153204775-199c01.png)

先打印`__getattribute__`，然后再调用`AttributeError`的时候，会触发`__getattr__`，还是会输出`__getattr__`的数据，最终导致抛出异常无效

![image-20240405153644243](C:\Users\waws\AppData\Roaming\Typora\typora-user-images\image-20240405153644243.png)

输出成功

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405161022140-af5f8c.png)

demo测试

- 主要测试`__getattr__`和`__getattribute__`

```python
class A:
    a = 1
    def __init__(self):
        self.a = 222

    def __setattr__(self, key, value):
        print(key,value)

    def __getattr__(self, item):
        # 在获取不到属性的时候才会触发
        print("__getattr__",item)

    def __getattribute__(self, item):
        # 属性拦截器，只要访问属性，就会经历这个方法
        print("__getattribute__",item)
        raise AttributeError(f"use item[{item!r}] to get field value")


a = A()
# a.a = 3
print(a.aaaa)
```

### 第十三阶段：Processor接收数据

上面我们已经没使用item类构建得到数据，下面创建一个数据处理类processor，这个部分只是将数据和request的判断移动到processor中，并没有完成处理

```python
# processor.py
from asyncio import Queue
from typing import Union
from bald_spider import Item, Request


class Processor:
    def __init__(self, crawler):
        self.queue: Queue = Queue()
        self.crawler = crawler

    async def process(self):
        while not self.idle():
            result = await self.queue.get()
            if isinstance(result, Request):
                await self.crawler.engine.enqueue_request(result)
            else:
                assert isinstance(result, Item)
                await self._process_item(result)

    async def _process_item(self, item: Item):
        print(item)

    async def enqueue(self, output: Union[Request, Item]):
        await self.queue.put(output)
        await self.process()

    def idle(self):
        return len(self) == 0

    def __len__(self):
        return self.queue.qsize()

# engine.py
from bald_spider.core.processor import Processor

class Engine:
    def __init__(self,crawler):
        # 初始化数据处理器
        self.processor:Optional[Processor] = None

    async def start_spider(self, spider):
        self.processor = Processor(self.crawler)

    async def _handle_spider_output(self,outputs):
        """
        在这个地方对输出的结果进行判断，数据走管道，请求重新回到spider
        """
        async for spider_output in outputs:
            if isinstance(spider_output,(Request,Item)):
                await self.processor.enqueue(spider_output)
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
        # 数据处理队列为空
        if self.scheduler.idle() and self.downloader.idle() and self.task_manager.all_done() and self.processor.idle():
            return True
        return False
```

### 第十四阶段：之前遗漏问题完善

- 新增创建Item实例的关键字方式传值
- `__getattr__`和`__getattribute__`异常引发冲突问题，导致`__getattribute__`的异常被覆盖

```python
# execptions.py
class ItemInitError(Exception):
    pass

class ItemAttributeError(Exception):
    pass

# items.items.py
from bald_spider.execptions import ItemInitError,ItemAttributeError


class Item(MutableMapping, metaclass=ItemMeta):
    FIELDS: dict

    def __init__(self,*args,**kwargs):
        """
        处理参数传值的情况
        """
        self._value = {}
        if args:
            raise ItemInitError(f"{self.__class__.__name__}:ponition asgs is not supported,"
                                f"use keyword args")
        if kwargs:
            for k,v in kwargs.items():
                self[k] = v


    def __getattr__(self, item):
        # 在这个地方不使用的原因是，属性存在，只是为{}，不会调用__getattr__
        raise AttributeError(f"{self.__class__.__name__} does not support field:{item}."
                             f"please add the `{item}` field to the {self.__class__.__name__},"
                             f"and use item[{item!r}] to get field value")

    def __getattribute__(self, item):
        field = super().__getattribute__("FIELDS")
        # 能进入下面的判断说明属性在field中，不能使用"."方式调用抛出异常
        if item in field:
            raise ItemAttributeError(f"use item[{item!r}] to get field value")
        # 若进不去，就是压根没有这个属性
        else:
            return super().__getattribute__(item)


if __name__ == "__main__":
    class TestItem(Item):
        url = Field()
        title = Field()


    class TestItem2(Item):
        name = Field()


    testItem = TestItem()
    # testItem = TestItem(url="111")
    # testItem = TestItem("111")
    # testItem2 = TestItem2()
    # testItem["url"] = "1111"
    # testItem["title"] = "title"
    # print(testItem["url"])
    # 以’.‘的方式去设置值的行为，我们需要禁止
    # testItem.url = 333
    # 以’.‘的方式去获取值的行为，我们需要禁止
    print(testItem.url)
    # print(testItem.xxx)
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405204107339-4c8e18.png)

### 第十五阶段：日志系统构建

```python
# engine.py
from bald_spider.utils.log import get_logger

class Engine:
    def __init__(self,crawler):
        self.crawler = crawler
        self.settings = crawler.settings

        # 初始化日志对象,就使用默认的日志级别INFO
        self.logger = get_logger(self.__class__.__name__)
        # 写类型注解 self.downloader: Downloader = Downloader()
        self.downloader:Optional[Downloader] = None
        # 我们使用yield的方式得到生成器，兼容于urls和url
        self.start_requests:Optional[Generator] = None
        # 初始化调度器
        self.scheduler:Optional[Scheduler] = None
        # 初始化数据处理器
        self.processor:Optional[Processor] = None
        # 初始化spider
        self.spider:Optional[Spider] = None
        # 控制爬虫进行的开关
        self.running = False
        # 初始化task管理器
        print("当前的并发数是：",self.settings.getint("CONCURRENCY"))
        self.task_manager:TaskManager= TaskManager(self.settings.getint("CONCURRENCY"))

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
        self.downloader = Downloader()
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

# utils.log.py
from logging import Formatter,StreamHandler,INFO,Logger

LOG_FORMAT = F"%(asctime)s [%(name)s] %(levelname)s: %(message)s"

class LogManager:
    logger = {}

    @classmethod
    def get_logger(cls,name:str="default",log_level=None,log_format=LOG_FORMAT):
        # 在这个地方其实是使用name和level唯一化一个logger，当存在直接从字典中返回
        # 若不存在在创建一个新的logger返回
        key = (name,log_level)
        def gen_logger():
            log_formatter = Formatter(log_format)
            handler = StreamHandler()
            handler.setFormatter(log_formatter)
            handler.setLevel(log_level or INFO)
            _logger = Logger(name)
            _logger.addHandler(handler)
            _logger.setLevel(log_level or INFO)
            cls.logger[key] = _logger
            return _logger
        return cls.logger.get(key,None) or gen_logger()

get_logger = LogManager.get_logger

if __name__ == "__main__":
    LogManager.get_logger(name="xxx",log_level=INFO)
    
# default_setting.py
"""
default config
"""
LOG_LEVEL = "INFO"

# settings.py
LOG_LEVEL = "INFO"
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405211900762-0d0997.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405212457029-e12377.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240405212632411-62f35e.png)