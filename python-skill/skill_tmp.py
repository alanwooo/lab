from inspect import signature
import logging

class MatchSignatureMeta(type):
    def __init__(self, cls, base, clsdict):
        print(self, cls, base, clsdict)
        super().__init__(cls, base, clsdict)
        sup = super(self, self)
        for name, value in clsdict.items():
            print(name, value)
            if name.startswith('_') or not callable(value):
                continue
            sup_dfn = getattr(sup, name, None)
            if sup_dfn:
                sup_name_sig = signature(sup_dfn)
                name_sig = signature(value)
                if name_sig != sup_name_sig:
                    logging.warn('signature mismatch %s %s %s != %s' % (value.__qualname__, sup_dfn.__qualname__, sup_name_sig, name_sig))

class Root(metaclass=MatchSignatureMeta):
    pass

class A(Root):
    def __init__(self, a, b):
        pass
    def foo(self, x, y):
        pass
    def func(self, m, n):
        pass

class B(A):
    def __init__(self, x, y, z):
        pass
    def foo(self, x, y):
        pass
    def func(self, n, m):
        pass
