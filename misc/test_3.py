class A:
    def __init__(self, x):
        self._x = x


a = A(1)
a._x = 2
print(a._x)
