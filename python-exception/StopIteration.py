class LogicExit(StopIteration):
    """
    Using this class to break out of the loop
    """
    pass

def test():
    print('start...')
    try:
        for x in range(3):
            for y in range(2):
                print('x=%s, y=%s' % (x, y))
                if x == 1 and y ==1:
                    print('break...')
                    raise LogicExit('x=%s,y=%s' % (x,y))
        else:
            print('stop...')
            return True
    except LogicExit as e:
        print('stop... %s' % e)
    finally:
        print('finally...')
    return False

print('before')
print(test())
print('after')
