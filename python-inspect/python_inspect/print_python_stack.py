import inspect
from pprint import pprint
import sys
import traceback
import types
# https://stackoverflow.com/questions/19514288/locals-and-globals-in-stack-trace-on-exception-python
# https://stackoverflow.com/questions/18078971/can-exception-handler-get-access-to-globals-and-locals-variables-at-exception-ra
# http://codegist.net/snippet/python/loggingpy_bobuss_python
# http://www.math.uiuc.edu/~gfrancis/illimath/windows/aszgard_mini/pylibs/twisted/python/failure.py
# http://www.cnblogs.com/kill-signal/archive/2012/10/10/2718002.html
# http://www.creativelydo.com/blog/how-to-globally-customize-exceptions-in-python/  !!!!
#
#
#
#

GLOBAL = "This is the test for logging exception"

def foo():
    f = "bar"
    1/0

def print_exc_plus():
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    tb = sys.exc_info()[2]
    while 1:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    traceback.print_exc()
    print("Locals by frame, innermost last")
    for frame in stack:
        print()
        print("Frame %s in %s at line %s" % (frame.f_code.co_name,
                                             frame.f_code.co_filename,
                                             frame.f_lineno))
        for key, value in frame.f_locals.items():
            print("\t%20s = " % key,)
            #We have to be careful not to cause a new error in our error
            #printer! Calling str() on an unknown object could cause an
            #error we don't want.
            try:                   
                print(value)
            except:
                print("<ERROR WHILE PRINTING VALUE>")

def sys_exc_info():
    tmp = 10
    tmp_in_sys_exc_info = "jack"
    try:
        foo()
    except:
        pprint('---------------------exc_info pprintting:-----------------------')
        exc_type, exc_value, tb = sys.exc_info()
        pprint(exc_type)
        pprint(exc_value)
        while tb.tb_next:
            pprint(tb.tb_frame.f_locals)
            pprint(tb.tb_frame.f_globals)
            tb = tb.tb_next
    pprint('---------------------exc_info pprintting:end--------------------')


def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %s" % (attr, getattr(obj, attr)))

def isclass(object):
    """Return true if the object is a class.

    Class objects provide these attributes:
        __doc__         documentation string
        __module__      name of module in which this class was defined"""
    return isinstance(object, (type, types.ClassType))

def traceback_pprint(type, value, tb):
    traceback.print_exception(type, value, tb)
    tmp = 10
    tmp_traceback_pprint = True
    pprint('---------------------Traceback pprintting:----------------------')
    traceback.print_stack()
    traceback.print_tb(tb)
    traceback.print_last()
    traceback.print_exc()
    traceback.print_stack()
    while tb.tb_next:
        pprint('-------------------------frame------------------------------')
        pprint(tb.tb_frame.f_locals)
        pprint(tb.tb_frame.f_globals)
        pprint(tb.tb_frame.f_code)
        pprint(tb.tb_frame.f_lineno)
        pprint(tb.tb_frame.f_lasti)
        pprint(tb.tb_frame.f_trace)
        for k, v in tb.tb_frame.f_locals.items():
            if k == 'self':
            #if isinstance(v, type):
                print(k, v)
                print(vars(v))
                dump(v)
            #pprint(isinstance(v, (type, type.ClassType)))
        tb = tb.tb_next
    pprint('---------------------Traceback pprintting:end-------------------')

def inspect_pprint():
    tmp_inspect_pprint = "Tony"
    f = inspect.currentframe()
    pprint('---------------------func inspect pprintting:----------------------')
    pprint(f.f_locals)
    pprint(f.f_globals)
    pprint('---------------------func inspect pprintting:end-------------------')
    return f

class Test():
    def __init__(self):
        self.name = 'I am test class'
        self.num = 100
        print(type(self))

    def func(self):
        self.tmp_main = 10
        f = inspect_pprint()
        sys_exc_info()
        pprint('---------------------main inspect pprintting 1:--------------------')
        pprint(f.f_locals)
        pprint(f.f_globals)
        pprint('---------------------main inspect pprintting 1:end-----------------')
        sys.excepthook = traceback_pprint 
        pprint('---------------------main inspect pprintting 2:--------------------')
        pprint(f.f_locals)
        pprint(f.f_globals)
        pprint('---------------------main inspect pprintting 2:end-----------------')
        foo()
        pprint('----------------------print_exc_plus-------------------------------')
        try:
            foo()
        except:
            print_exc_plus()
        pprint('----------------------print_exc_plus:end---------------------------')
        #traceback_pprint()

if __name__ == '__main__':
    t = Test()
    t.func()
