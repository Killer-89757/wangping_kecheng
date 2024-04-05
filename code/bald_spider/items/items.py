from bald_spider.items import Field

class Item:
    # FIELDS:dict = dict()

    def __init__(self):
        self.FIELDS = {}
        # print(self.__class__.__dict__)
        # {'__module__': '__main__', 'url': {}, 'title': {}, '__doc__': None}
        for cls_attr,value in self.__class__.__dict__.items():
            if isinstance(value,Field):
                self.FIELDS[cls_attr] = value
        print(self.FIELDS)
        self._value = {}

    def __setitem__(self, key, value):
        if key in self.FIELDS:
            self._value[key] = value
        else:
            raise KeyError(f"{self.__class__.__name__} dose not support field:{key}")

    def __getitem__(self, item):
        pass

    def __repr__(self):
        return str(self._value)

if __name__ == "__main__":
    class TestItem(Item):
        url = Field()
        title = Field()

    class TestItem2(Item):
        name = Field()
    testItem = TestItem()
    testItem2 = TestItem2()
    # testItem["url"] = "1111"
    # testItem["title"] = "title"
    # print(testItem)
