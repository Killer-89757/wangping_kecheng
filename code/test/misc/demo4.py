class A:
    def __getitem__(self, item):
        print(item)

    def __setitem__(self, key, value):
        print(key,value)

a = A()
a[1]  # 1
a[1:3]  # slice(1, 3, None)
a["name"] = "value1" # name value1