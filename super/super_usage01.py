# python3.5

class A:
    def __init__(self):
        print ("in A")
        print ("out A")

class B(A):
    def __init__(self):
        print ("in B")
        super().__init__()
        print ("out B")

class D(B):
    def __init__(self):
        print ("in D")
        super().__init__()
        print ("out D")

class C(B):
    def __init__(self):
        print ("in C")
        super().__init__()
        print ("out C")

class E(C, D, B):
    def __init__(self):
        print ("in E")
        super().__init__()
        print ("out E")

class F(D):
    def __init__(self):
        print ("in F")
        super().__init__()
        print ("out F")

f = F()
print ('\n\n\n')
e = E()
