import os

def add2(x):
    return x + 2

def double(x):
    return x * 2

def opertion(x, opt):
    return opt(x)

def main():
    print opertion(4, add2)
    print opertion(4, double)

if __name__ == '__main__':
    main()
