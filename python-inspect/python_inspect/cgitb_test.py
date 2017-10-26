import sys
import cgitb
import traceback

def func(a, b):
    return a / b

if __name__ == "__main__":
    cgitb.enable(format = 'text')
    x = 10
    y = 100
    func(x, y)
    y = 0
    func(x ,y)
    
