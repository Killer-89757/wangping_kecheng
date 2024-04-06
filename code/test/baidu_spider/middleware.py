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