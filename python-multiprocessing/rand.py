import os
import sys
import random
import traceback
import time
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing


def error(msg, *args):
    return multiprocessing.get_logger().error(msg, *args)
class LogExceptions(object):
    def __init__(self, callable):
        self.__callable = callable
        return
    def __call__(self, *args, **kwargs):
        try:
            result = self.__callable(*args, **kwargs)
        except Exception as e:
            # Here we add some debugging help. If multiprocessing's
            # debugging is on, it will arrange to log the traceback
            error(traceback.format_exc())
            # Re-raise the original exception so the Pool worker can
            # clean up
            raise
        # It was fine, give a normal answer
        return result
    pass

class LoggingPool(Pool):
    def apply_async(self, func, args=(), kwds={}, callback=None):
        return Pool.apply_async(self, LogExceptions(func), args, kwds, callback)

def vmops(repo):
    def dt():
        print('dt')
        time.sleep(1)
        return ''

    def iozone():
        print('iozone')
        return ''

    def fio():
        print('fio')
        time.sleep(100)
        return ''

    def svmotion():
        print('svmotion')
        return  ''

    def poweroff():
        print('poweroff')
        time.sleep(3)
        return 'off'

    def addvmdk():
        print('addvmdk')
        return ''

    def addremovevmdk():
        print('addremovevmdk')
        return ''

    def svmotion():
        print('svmotion')
        return ''

    def poweron():
        print('poweron')
        time.sleep(2)
        return 'on'

    def resume():
        print('resume')
        return 'on'

    def suspend():
        print('resume')
        return 'suspend'

    def updateWeight(idx, weight):
        for i, _ in enumerate(weight):
            if idx == i:
                continue
            weight[i] += 1

    def randomOp(weight):
        #random.seed()
        r = random.randint(0, sum(weight) - 1)
        #print('roandom=', r, weight, multiprocessing.current_process().ident)
        for i, val in enumerate(weight):
            r -= val
            if r <= 0:
                break
        return i    

    def selectOp(vm_state, ops, weight, state):
        i = randomOp(weight)
        while True:
            if ops[i] in state[vm_state]:
                #print (ops[i].__name__, ops[i], vm_state)
                break
            else:
                i = randomOp(weight)
        updateWeight(i, weight)
        return i
        #cur_state = ops[i]()
        #return cur_state if cur_state else vm_state

    def runop(weight, steps):
        cur_state = 'on'
        #print('id=', id(weight), id(steps))
        #print (globals())
        #print(steps)
        #print (locals())
        if steps:
            for op in steps:
                name_to_op[op]()
                #vm_state = eval(op)()
        else:
            while not stop:
                op = selectOp(cur_state, ops, weight, state)
                steps.append(ops[op].__name__)
                vm_state = ops[op]()
                #print("vm_state=",vm_state)
                #print(ops[op])
                time.sleep(1)
                cur_state = vm_state if vm_state else cur_state

    ops = []
    weight = []
    stop = False
    name_to_op = {}
    steps = repo if repo else []
    vm_num =  len(repo) if repo else 2
    state = {'on' : (dt, fio, iozone, svmotion, poweroff, suspend), 
             'off' : (addremovevmdk, svmotion, poweron),
             'suspend' : (resume,), 
            }

    for _, val in state.items():
        for op in val:
            if op in ops:
                continue
            ops.append(op)
            name_to_op.update({op.__name__ : op})
    #print(ops)
    start = time.time()
    for i in range(vm_num):
        weight.append([1] * len(ops))
        steps.append([] * len(ops))
 
    multiprocessing.log_to_stderr()
    pool = LoggingPool(processes=vm_num)
    for w, s in zip(weight, steps):
        #print('id==', id(w),id(s))
        time.sleep(2)
        pool.apply_async(runop, args = (w, s))
    pool.close()
    while time.time() - start < 30:
        time.sleep(2)
    print('Waiting for the testing finished...')
    stop = True
    pool.join()
    print(steps)
    print(weight)

if __name__ in '__main__':
    repo = [['fio', 'poweroff', 'svmotion', 'addremovevmdk', 'poweron', 'iozone', 'iozone', 'svmotion', 'suspend', 'resume', 'svmotion', 'poweroff'], ['fio', 'svmotion', 'suspend', 'resume', 'poweroff', 'poweron', 'poweroff']]
    repo = None
    vmops(repo)
