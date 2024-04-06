# wangping_kecheng
>  猿人学王平老师的爬虫系统架构的代码

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

## 项目文档

[爬虫系统架构大纲](docs/爬虫系统架构大纲.md)

[猿人学-爬虫框架代码-part1](docs/猿人学-爬虫框架代码-part1.md)

[猿人学-爬虫框架代码-part2](docs/猿人学-爬虫框架课程-part2.md)

[猿人学-爬虫框架代码-part3](docs/猿人学-爬虫框架课程-part3.md)

[猿人学-爬虫框架代码-part4](docs/猿人学-爬虫框架课程-part4.md)

[猿人学-爬虫框架代码-part5](docs/猿人学-爬虫框架课程-part5.md)

[猿人学-爬虫框架代码-part6](docs/猿人学-爬虫框架课程-part6.md)