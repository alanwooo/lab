import os

# 输入一个小于20的正整数n的条件下穷举出n位二进制数
def print_binary(x):
    num = sum((2**n for n in range(x)))
    for i in range(num + 1):
        #print((bin(i)[2:]).zfill(x))
        print( ('%0' + str(x) + 'd') % int(bin(i)[2:]))

print_binary(3)
