class A:
    a = 1
    def __init__(self):
        self.a = 222

    def __setattr__(self, key, value):
        print(key,value)

    def __getattr__(self, item):
        # 在获取不到属性的时候才会触发
        print("__getattr__",item)

    def __getattribute__(self, item):
        # 属性拦截器，只要访问属性，就会经历这个方法
        print("__getattribute__",item)
        raise AttributeError(f"use item[{item!r}] to get field value")


a = A()
# a.a = 3
print(a.aaaa)