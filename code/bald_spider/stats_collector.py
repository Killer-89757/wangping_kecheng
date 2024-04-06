from bald_spider.utils.log import get_logger
from pprint import pformat
from bald_spider.utils.date import date_delta
from bald_spider.utils.date import now
class StatsCollector:
    """
    其实我们可以在请求的地方设置一个值，在下载成功的地方设置一个值，在其他需要统计的地方设置对应的值，最后在需要调用
    的地方，将所有统计数字放在一起，比较繁琐
    - 我们使用一个类统一对统计数据进行管理。
    - 将其放入到crawler当中，和spider和engine的融合的思路一样，使得我们在任何地方都可以直接拿到统计信息
    """

    def __init__(self, crawler):
        self.crawler = crawler
        self._dump = self.crawler.settings.getbool("STATS_DUMP")
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
        self._stats["end_time"] = now()
        self._stats["reason"] = reason
        self._stats["cost_time(s)"] = date_delta(self._stats["start_time"],self._stats["end_time"])
        if self._dump:
            self.logger.info(f"{spider} stats:\n" + pformat(self._stats))

    def __getitem__(self, item):
        return self._stats[item]

    def __setitem__(self, key, value):
        self._stats[key] = value

    def __delitem__(self, key):
        del self._stats[key]
