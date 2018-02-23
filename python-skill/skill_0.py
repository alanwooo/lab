import os
import time
import heapq
import random
import itertools
import collections


###########################
def func():
    a = [1, 2, 3, 4, 5, 6]
    yield from a

for x in func():
    print(x)

###########################
class A():
   def __init__(self):
       self.time = 0
       pass
   @property
   def get_time(self):
       return time.time()
   @get_time.setter
   def set_time(self, value):
       if value < 0:
           print('value must > 0')
       else:
          self.time = value
          print('self.time = %d' % self.time)

a = A()
print(a.get_time)
a.set_time = -1
a.set_time = 10


###########################
# property descriptor
# self.birth has read/write property
# self.age only has read property
class Person():
    def __init__(self, birth_date):
        self._birth = birth_date
    @property
    def birth(self):
        return self._birth
    @birth.setter
    def birth(self, value):
        self._birth = value
    @property
    def age(self):
        return 2014 - self._birth

p = Person(1985)
print(p.birth, p.age)
p.birth = 1990
print(p.birth, p.age)
       
###########################
ls = [[1,2,3],[4,5,6],[7,8,9]]
ls_new = sum(ls, []) 
print(ls_new)


###########################
def func_doc():
    """
    Do nothing, just document it.

    Done.
    """
print(func_doc.__doc__)


###########################
matrix = [[1, 2, 3],[4, 5, 6]]
print(list(zip(*matrix)))


###########################
a, *b, c = [1, 2, 3, 4, 5]
print(a, b, c)


###########################
m = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
m_c = dict(zip(m.values(), m.keys()))
print(m)
print(m_c)
m_c = {v: k for k, v in m.items()}
print(m_c)


###########################
x = y = 1
result = True if x == y else False
print(result)
result = (False, True)[x == y]
print(result)


###########################
def add(x):
    class AddNum(int):
        def __call__(self, x):
            return AddNum(self.numerator + x)
    return AddNum(x)

print(add(1)(2)(3))


###########################
class A(object):
    def __init__(self, a, b, c, d, e, f):
        self.__dict__.update({k: v for k, v in locals().items() if k != 'self'})

a = A(1, 2, 3, 4, 5, 6)
print(vars(a))


###########################
print(4 < 10 < 20 < 100)
print(4 < 10 < 20 > 100)


###########################
a = collections.Counter([1, 1, 2, 2, 3, 3, 3, 3, 4, 5, 6, 7])
print(a)
print(a.most_common(1))
print(a.most_common(3))
c = collections.Counter('aaabbccccddddddeeff')
print(c)
print(c.most_common(2))

###########################
# max number/min number
a = [random.randint(0, 100) for _ in range(100)]
print(heapq.nsmallest(5, a))
print(heapq.nlargest(5, a))


###########################
a = [1, 2, 3, 4, 5, 6, 7, 8]
b = a[::-1]
print(b)
c = a[:]
print(c)
print(id(a), id(b), id(c))


###########################
a = [1, 3, 5, 7, 9]
b = [2, 3, 4, 5, 6]
c = [5, 6, 7, 8, 9]
print(list(set().union(a, b, c)))


###########################
with open('/tmp/a') as fd1, open('/tmp/b') as fd2, open('/tmp/c') as fd3:
    pass


###########################
class contextmanager():
    def __init__(self, sec):
        self.sec = sec
    def __enter__(self):
        print('in __enter__')
        time.sleep(self.sec)
        return self
    def print_hello(self):
        print('hello')
    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('in __exit__')
        if exc_traceback is None:
            print('do not hit exception')
        else:
            print('hit exception')

with contextmanager(2) as cm:
    cm.print_hello()


###########################
a = (x for x in range(10))
for i in a:
    print(i)



