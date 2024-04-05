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