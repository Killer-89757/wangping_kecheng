from abc import ABCMeta
class Field(dict):
    pass

class ItemMeta(ABCMeta):
    def __new__(mcs,name,bases,attrs):
        # mcs:metaclass
        # name:Item 类的名称
        # bases: 继承类的父类
        # attrs: 类属性
        field = {}
        for key,value in attrs.items():
            if isinstance(value,Field):
                field[key] = value
        cls_instance = super().__new__(mcs,name,bases,attrs)
        cls_instance.FIELDS = field
        return cls_instance