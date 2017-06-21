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

def vmops(seed):
    def dt():
        #print('dt')
        time.sleep(1)
        return ''

    def iozone():
        time.sleep(2)
        #print('iozone')
        return ''

    def fio():
        #print('fio')
        time.sleep(1)
        return ''

    def svmotion():
        time.sleep(1)
        #print('svmotion')
        return  ''

    def poweroff():
        #print('poweroff')
        time.sleep(3)
        return 'off'

    def addvmdk():
        time.sleep(1)
        #print('addvmdk')
        return ''

    def addremovevmdk():
        time.sleep(4)
        #print('addremovevmdk')
        return ''

    def svmotion():
        time.sleep(2)
        #print('svmotion')
        return ''

    def poweron():
        #print('poweron')
        time.sleep(1)
        return 'on'

    def resume():
        time.sleep(1)
        #print('resume')
        return 'on'

    def suspend():
        time.sleep(1)
        #print('resume')
        return 'suspend'

    def updateWeight(idx, weight):
        for i, _ in enumerate(weight):
            if idx == i:
                continue
            weight[i] += 1

    def randomOp(weight):
        r = random.randint(0, sum(weight) - 1)
        for i, val in enumerate(weight):
            r -= val
            if r <= 0:
                break
        return i    

    def selectOp(vm_state, ops, weight, state):
        i = randomOp(weight)
        while True:
            if ops[i] in state[vm_state]:
                break
            else:
                i = randomOp(weight)
        updateWeight(i, weight)
        return i

    def runop(weight, steps):
        cur_state = 'on'
        for op in steps:
            if not stop:
                break
            name_to_op[op]()

    def sortops(op):
        return op.__name__

    def fixstate(op, cur_state):
        if op in state_change.keys():
            return state_change[op]
        return cur_state

    ops = []
    weight = []
    stop = False
    name_to_op = {}
    steps = []
    vm_num =  len(seed) if seed else 2
    state = {'on' : (dt, fio, iozone, svmotion, poweroff, suspend), 
             'off' : (addremovevmdk, poweron),
             'suspend' : (resume,), 
            }
    state_change = { suspend : 'suspend',
                     poweron : 'on',
                     poweroff : 'off',
                     resume : 'on',
                   }

    for _, val in state.items():
        for op in val:
            if op in ops:
                continue
            ops.append(op)
            name_to_op.update({op.__name__ : op})
    ops = sorted(ops, key=sortops)
    #print(ops)
    start = time.time()
    for i in seed:
        cur_state = 'on'
        sub = []
        weight = [1] * len(ops)
        random.seed(i)
        idxs=[]
        for _ in range(1000):
           idx = selectOp(cur_state, ops, weight, state)
           idxs.append(idx)
           op = ops[idx]
           sub.append(op.__name__)
           cur_state = fixstate(op, cur_state)
           #print (op, cur_state)
        steps.append(sub)
        #print (i, weight, sub)
        print (weight)
        #print (idxs)
    #print (steps)
    #sys.exit(1)
    multiprocessing.log_to_stderr()
    pool = LoggingPool(processes=vm_num)
    for w, s in zip(weight, steps):
        #print('id==', id(w),id(s), w, s)
        time.sleep(1)
        pool.apply_async(runop, args = (w, s))
    pool.close()
    while time.time() - start < 20:
        time.sleep(1)
    print('Waiting for the testing finished...')
    stop = True
    pool.join()
    #print(steps)
    #print(weight)

if __name__ in '__main__':
    repo = [10, 20]
    vmops(repo)
