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
