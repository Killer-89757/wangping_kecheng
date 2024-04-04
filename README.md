# wangping_kecheng
>  猿人学王平老师的爬虫系统架构的代码

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
    - baidu.py  **爬虫实例**
    - run.py     **项目启动文件**

## 项目文档

[爬虫系统架构大纲](docs/爬虫系统架构大纲.md)

[猿人学-爬虫框架代码-part1](docs/猿人学-爬虫框架代码-part1.md)