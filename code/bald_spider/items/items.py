from pprint import pformat
from bald_spider.items import Field, ItemMeta
from collections.abc import MutableMapping
from copy import deepcopy
from bald_spider.execptions import ItemInitError,ItemAttributeError


class Item(MutableMapping, metaclass=ItemMeta):
    FIELDS: dict

    def __init__(self,*args,**kwargs):
        """
        处理参数传值的情况
        """
        self._value = {}
        if args:
            raise ItemInitError(f"{self.__class__.__name__}:ponition asgs is not supported,"
                                f"use keyword args")
        if kwargs:
            for k,v in kwargs.items():
                self[k] = v

    # __new__可以在调用__init__之前进行调用

    def __setitem__(self, key, value):
        if key in self.FIELDS:
            self._value[key] = value
        else:
            raise KeyError(f"{self.__class__.__name__} dose not support field:{key}")

    def __getitem__(self, item):
        return self._value[item]

    def __delitem__(self, key):
        del self._value[key]

    def __setattr__(self, key, value):
        # 在这个地方其实是放self._value通过
        if not key.startswith("_"):
            raise AttributeError(f"use item[{key!r}] = {value!r} to set field value")
        super().__setattr__(key, value)

    def __getattr__(self, item):
        # 在这个地方不使用的原因是，属性存在，只是为{}，不会调用__getattr__
        raise AttributeError(f"{self.__class__.__name__} does not support field:{item}."
                             f"please add the `{item}` field to the {self.__class__.__name__},"
                             f"and use item[{item!r}] to get field value")

    def __getattribute__(self, item):
        field = super().__getattribute__("FIELDS")
        # 能进入下面的判断说明属性在field中，不能使用"."方式调用抛出异常
        if item in field:
            raise ItemAttributeError(f"use item[{item!r}] to get field value")
        # 若进不去，就是压根没有这个属性
        else:
            return super().__getattribute__(item)

    def __repr__(self):
        return pformat(dict(self))

    __str__ = __repr__

    def __iter__(self):
        return iter(self._value)

    def __len__(self):
        return len(self._value)

    def to_dict(self):
        return dict(self)

    def copy(self):
        return deepcopy(self)

if __name__ == "__main__":
    class TestItem(Item):
        url = Field()
        title = Field()


    class TestItem2(Item):
        name = Field()


    testItem = TestItem()
    # testItem = TestItem(url="111")
    # testItem = TestItem("111")
    # testItem2 = TestItem2()
    # testItem["url"] = "1111"
    # testItem["title"] = "title"
    # print(testItem["url"])
    # 以’.‘的方式去设置值的行为，我们需要禁止
    # testItem.url = 333
    # 以’.‘的方式去获取值的行为，我们需要禁止
    print(testItem.url)
    # print(testItem.xxx)
