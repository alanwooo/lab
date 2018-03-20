import os

############################
# https://www.jianshu.com/p/885d59db57fc
class URLGenerator():
    def __init__(self, url):
        self.url = url
    def __getattr__(self, item):
        if item in ['get', 'post']:
            return self.url
        return URLGenerator('{}/{}'.format(self.url, item))

url_gen = URLGenerator('http://google.com')
print(url_gen.map.userid.get)


print('\n\n\n\n')
##yy##########################
# 
class Attribute():
    def __init__(self, x):
        self.x = x
    #def __getattribute__(self, *args, **kwargs):
    def __getattribute__(self, name):
        print('in __getattribute__ %s' % name)
        if name == 'x':
            return 'x value %s' % super().__getattribute__(name)
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            print('hit %s' % e)
            raise AttributeError
    def __getattr__(self, name):
        print('in __getattr__ %s' % name)
        if name == 'test':
            return 'we want test'
        return 'can not find'
    def __setattr__(self, name, value):
        print('in __setattr__')
        if name == 'z':
            self.__dict__[name] = 'z value: %s' % value
        else:
            super().__setattr__(name, value)
    def foo(self, name):
        print('foo %s' % name)

a = Attribute('===')
print('----------------------------------')
print(a.x)
print('----------------------------------')
a.z = 1000
print(a.z)
print('----------------------------------')
a.a = 1111
print(a.a)
print('----------------------------------')
print(a.y)
print('----------------------------------')
print(a.test)
print('----------------------------------')
print('hasattr b %s' % hasattr(a, 'b'))
print(getattr(a, 'b', 3333))
a.b = 2222
print(getattr(a, 'b', 3333))
setattr(a, 'b', 4444)
print(a.b)
print('----------------------------------')
a.foo('~~~')
print('----------------------------------')


print('\n\n\n\n')
#########################################
class Dict(dict):
    '''
    通过使用__setattr__,__getattr__,__delattr__
    可以重写dict,使之通过"."调用
    '''
    def __setattr__(self, key, value):
        print("In __setattr__")
        self[key] = value
        
    def __getattr__(self, key):
        try:
            print("In __getattr__")
            return self[key]
        except KeyError as k:
            return None
            
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            return None
            
    # __call__方法用于实例自身的调用,达到()调用的效果
    def __call__(self, key):    # 带参数key的__call__方法
        try:
            print("In __call__")
            return self[key]
        except KeyError as k:
            return "In __call__ error"

d = Dict()
d['name'] = 'New Dict'
print(d.name)
d.value = 1000
print(d.value)
print(d('name'))
