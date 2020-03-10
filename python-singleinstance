import os
import time

class SingleInstance(object):
    __has_instance = None
    __is_inited = False
    def __new__(cls, msg):
        if not cls.__has_instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance
    def __init__(self, msg):
        if not self.__is_inited:
             SingleInstance.__is_inited = True
             print(msg)

def test_singeinstance():
    time.sleep(100)
    a = SingleInstance('testa')
if '__main__' == __name__:

    #a = SingleInstance('testa')
    b = SingleInstance('testb')
    c = SingleInstance('testc')
    d = SingleInstance('testd')
