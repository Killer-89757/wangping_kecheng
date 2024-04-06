# 当一个字典没有初始值的时候，我们可以使用setdefault设置值
# 当一个字典有初始值的时候，我们可以使用setdefault设置无效
a = {1: 1}
a.setdefault(1, 3)
print(a)
# {1: 1}

a = {}
a.setdefault(1, 3)
print(a)
# {1: 3}

a = {}
b = a.setdefault(1, 3)
print(b)
# 3

a = {1:1}
b = a.setdefault(1, 3)
print(b)
# 1
