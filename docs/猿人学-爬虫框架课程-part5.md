# 猿人学-爬虫框架课程(5)

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
    - settings.py  **用户配置文件**
  - misc
    - demo1.py **测试信号量**
    - demo2.py **测试信号量**
    - demo3.py **测试模块信息(获取配置信息)**
    - demo4.py **\_\_getitem__的使用**
    - demo5.py **\_\_getattr__和\_\_getattribute\_\_的使用**
    - demo6.py  **测试下载器记录**

### 第二十一阶段：解决中断报错问题

前面当我们手动中止程序代码的时候，会疯狂的报错，这个部分就是解决这个问题

- 解决方式：手动的捕捉`ctrl + c`的信号，然后让程序正常关闭

```python
# crawler.py
import signal
from bald_spider.utils.log import get_logger

logger = get_logger(__name__)

class CrawlerProcess:
    def __init__(self,settings=None):
        self.crawlers:Final[Set] = set()
        self._active:Final[Set] = set()
        self.settings = settings
        # `ctrl + c`的信号是SIGINT
        signal.signal(signal.SIGINT,self._shutdown)
        
    def _shutdown(self,_signum,_frame):
        for crawler in self.crawlers:
            crawler.engine.running = False
        logger.warning(f"spider received `ctrl c` single,closed")

# engine.py
class Engine:
    async def close_spider(self):
        # 为了处理异常关闭下，请求中途断开，然后报错的问题，我们可以等所有的请求请求完毕，在关闭下载器
        await asyncio.gather(*self.task_manager.current_task)
        await self.downloader.close()
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406193427919-ada9b0.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406193730399-1e883b.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406193953357-d78b9f.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406194814727-f14c2c.png)

为了处理异常关闭下，请求中途断开，然后报错的问题，我们可以等所有的请求请求完毕，在关闭下载器

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406195255318-07b4f0.png)

### 第二十二阶段：添加统计信息(总计)

当我们程序正常关闭的时候，数据量比较小，我们能一眼看出来，但是数据量多起来后，我们就不能得到数据的准确信息，需要进行数据统计

- 抓到多少条数据
- 爬虫的起始时间
- 爬虫的中止时间

```python
# engine.py
class Engine:
    async def start_spider(self, spider):
        self.scheduler = Scheduler(self.crawler)
       

    async def close_spider(self):
        # 为了处理异常关闭下，请求中途断开，然后报错的问题，我们可以等所有的请求请求完毕，在关闭下载器
        await asyncio.gather(*self.task_manager.current_task)
        await self.downloader.close()
        await self.crawler.close()
        
# processor.py
class Processor:
   async def _process_item(self, item: Item):
        self.crawler.stats.inc_value("item_successful")
        print(item)

# scheduler.py
class Scheduler:
    def __init__(self,crawler):
        self.crawler = crawler
        # 使用优先级队列，不同的请求的优先级不同
        self.request_queue: Optional[PriorityQueue] = None

    async def enqueue_request(self,request):
        await self.request_queue.put(request)
        # 将请求的数量 +1
        self.crawler.stats.inc_value("request_Scheduled_count")

# crawler.py
from bald_spider.stats_collector import StatsCollector
from bald_spider.utils.date import now

logger = get_logger(__name__)

class Crawler:
    def __init__(self,spider_cls,settings):
        self.stats:Optional[StatsCollector] = None
   
    async def crawl(self):
        self.stats = self._create_stats()

    def _create_stats(self):
        stats = StatsCollector(self)
        stats["start_time"] = now()
        return stats

    async def close(self,reason="finished"):
        self.stats["end_time"] = now()
        self.stats.close_spider(self.spider,reason)

# stats_collector.py
from bald_spider.utils.log import get_logger
from pprint import pformat

class StatsCollector:
    """
    其实我们可以在请求的地方设置一个值，在下载成功的地方设置一个值，在其他需要统计的地方设置对应的值，最后在需要调用
    的地方，将所有统计数字放在一起，比较繁琐
    - 我们使用一个类统一对统计数据进行管理。
    - 将其放入到crawler当中，和spider和engine的融合的思路一样，使得我们在任何地方都可以直接拿到统计信息
    """

    def __init__(self, crawler):
        self.crawler = crawler
        self._stats ={}
        self.logger = get_logger(self.__class__.__name__,"INFO")

    def inc_value(self, key, count=1, start=0):
        self._stats[key] = self._stats.setdefault(key,start) + count

    def get_value(self,key,default = None):
        return self._stats.get(key,default)

    def get_stats(self):
        return self._stats

    def set_stats(self,stats):
        self._stats = stats

    def clear_stats(self):
        self._stats.clear()

    def close_spider(self,spider,reason):
        self._stats["reason"] = reason
        self.logger.info(f"{spider} stats:\n" + pformat(self._stats))

    def __getitem__(self, item):
        return self._stats[item]

    def __setitem__(self, key, value):
        self._stats[key] = value

    def __delitem__(self, key):
        del self._stats[key]

# utils.date.py
from datetime import datetime

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

测试`setdefault`的用法

```python
# demo7.py
# 当一个字典没有初始值的时候，我们可以使用setdefault设置值
# 当一个字典有初始值的时候，我们可以使用setdefault设置无效
a = {1: 1}
a.setdefault(1, 3)
print(a)
# {1: 1}

a = {}
a.setdefault(1, 3)
print(a)
# {1: 3}

a = {}
b = a.setdefault(1, 3)
print(b)
# 3

a = {1:1}
b = a.setdefault(1, 3)
print(b)
# 1

```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406214422285-2ca9c7.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406215658348-e0914c.png)

### 第二十三阶段：局部统计信息

如果我们的代码跑动几个小时，我们只有最后的结果信息，那么过程中我们无法知道请求数目和当前的请求效率，所以需要隔一段时间输出一下

- 局部统计信息
  - 当前的请求统计信息
  - 当前的请求速率等

```python
# date.py
def date_delta(start,end):
    start = datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end,"%Y-%m-%d %H:%M:%S")
    time_diff = end - start
    seconds = time_diff.total_seconds()
    return seconds

# stats_collector.py
from bald_spider.utils.log import get_logger
from pprint import pformat
from bald_spider.utils.date import date_delta
from bald_spider.utils.date import now
class StatsCollector:
    def __init__(self, crawler):
        self.crawler = crawler
        self._dump = self.crawler.settings.getbool("STATS_DUMP")
        self._stats ={}
        self.logger = get_logger(self.__class__.__name__,"INFO")

    def close_spider(self,spider,reason):
        self._stats["end_time"] = now()
        self._stats["reason"] = reason
        self._stats["cost_time(s)"] = date_delta(self._stats["start_time"],self._stats["end_time"])
        if self._dump:
            self.logger.info(f"{spider} stats:\n" + pformat(self._stats))
            
# engine.py
class Engine:
    def __init__(self,crawler):
        self.normal = True

    async def close_spider(self):
        # 为了处理异常关闭下，请求中途断开，然后报错的问题，我们可以等所有的请求请求完毕，在关闭下载器
        await asyncio.gather(*self.task_manager.current_task)
        await self.downloader.close()
        if self.normal:
            await self.crawler.close()

# aiohttp_downloader.py
class AioDownloader(DownloaderBase):

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
        else:
            # 临时性代码
            self.crawler.stats.inc_value("response_received_count")
        return self.structure_response(request,response,body)

# httpx_downloader.py
class HttpxDownloader(DownloaderBase):
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
        else:
            # 临时性代码
            self.crawler.stats.inc_value("response_received_count")
        return self.structure_response(request, response, body)

# processor.py
class Processor:
    async def _process_item(self, item: Item):
        self.crawler.stats.inc_value("item_successful_count")
        print(item)

# scheduler.py
from bald_spider.utils.log import get_logger
class Scheduler:
    def __init__(self,crawler):
        self.crawler = crawler
        # 使用优先级队列，不同的请求的优先级不同
        self.request_queue: Optional[PriorityQueue] = None
        self.item_count = 0
        self.response_count = 0
        self.logger = get_logger(self.__class__.__name__,log_level=crawler.settings.get("LOG_LEVEL"))

    async def enqueue_request(self,request):
        await self.request_queue.put(request)
        # 将请求的数量 +1
        self.crawler.stats.inc_value("request_Scheduled_count")

    # 其实这个日志并不属于调度器，只是临时写在这个地方
    async def interval_log(self,interval):
        while True:
            last_item_count = self.crawler.stats.get_value("item_successful_count",default=0)
            last_response_count = self.crawler.stats.get_value("response_received_count",default=0)
            item_rate = last_item_count - self.item_count
            response_rate = last_response_count - self.response_count
            self.item_count = last_item_count
            self.response_count = last_response_count
            self.logger.info(f"Crawler {last_response_count} pages (at {response_rate} pages / {interval}s)"
                             f"Got {last_item_count} items (at {item_rate} items / {interval}s)")
            await asyncio.sleep(interval)

# crawler.py
from bald_spider.utils.log import get_logger
from bald_spider.stats_collector import StatsCollector
from bald_spider.utils.date import now

logger = get_logger(__name__)

class Crawler: 
    def _shutdown(self,_signum,_frame):
        for crawler in self.crawlers:
            crawler.engine.running = False
            crawler.engine.normal = False
            crawler.stats.close_spider(crawler.spider,"ctrl c")
        logger.warning(f"spider received `ctrl c` single,closed")
```

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406223318031-236e59.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F04%2Fimage-20240406225521400-b9c2ba.png)