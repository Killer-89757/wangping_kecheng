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