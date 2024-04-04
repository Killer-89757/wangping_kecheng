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