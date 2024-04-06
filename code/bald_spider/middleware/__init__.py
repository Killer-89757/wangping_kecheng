
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

