import sys, traceback

def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)

    while tb.tb_next:
        tb = tb.tb_next

    print(sys.stderr, 'Locals:',  tb.tb_frame.f_locals)
    print(sys.stderr, 'Globals:', tb.tb_frame.f_globals)

sys.excepthook = excepthook

def x():
    y()

def y():
    foo = 1
    bar = 0

    foo/bar

x()
