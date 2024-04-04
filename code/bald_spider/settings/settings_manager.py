from importlib import import_module
from bald_spider.settings import default_settings
from collections.abc import MutableMapping
from copy import deepcopy


class SettingsManager(MutableMapping):
    def __init__(self,values=None):
        self.attributes = {}
        self.set_settings(default_settings)
        self.update_values(values)

    def __getitem__(self, item):
        if item not in self:
            return None
        return self.attributes[item]

    def __contains__(self, item):
        return item in self.attributes

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, value):
        self.attributes[key] = value

    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    # 当我们不小心写了一个字符串的数字，使用getint兼容
    def getint(self, name, default=1):
        return int(self.get(name, default))

    def getfloat(self, name, default=0.0):
        return float(self.get(name, default))

    def getbool(self, name, default=False):  # noqa
        # 比较麻烦，可以写True/False or "True"/"False" or 0/1
        got = self.get(name, default)
        try:
            # 可以兼容bool or int类型
            return bool(int(got))
        except ValueError:
            # 报错就是str类型
            if got in ("True","true","TRUE"):
                return True
            if got in ("False","false","FALSE"):
                return False
            raise ValueError("Supported values for bool settings are (0 or 1),(True or False),('0' or '1'),('True' or 'False'),('TRUE' or 'FALSE'),('true' or 'false')")

    def getlist(self, name, default=None):
        value = self.get(name, default or [])
        if isinstance(value,str):
            value = value.split(",")
        return list(value)


    def __delitem__(self, key):
        del self.attributes[key]

    def delete(self, key):
        del self.attributes[key]

    def set_settings(self, module):
        # 我们可以直接传入模块、或者传入模块的str名称
        if isinstance(module, str):
            # 因为我们的代码结构很好，所以不会出现路径加载不成功的问题
            # 但是框架形成后，用户自定义编辑文件可能会出现找不到配置文件的情况
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))

    def __str__(self):
        return f"<settings value={self.attributes}>"

    __repr__ = __str__

    def update_values(self,values):
        if values is not None:
            for key,value in values.items():
                self.set(key,value)

    # 继承自抽象类的抽象方法都是要自行实现的
    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def copy(self):
        return deepcopy(self)


if __name__ == "__main__":
    settings = SettingsManager()
    settings["CONCURRENCY"] = 16
    print(settings.items())
