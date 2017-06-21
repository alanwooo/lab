import os
import sys
import random
import traceback
import time
import threading
import queue

lock = threading.RLock()

def vmops(seed):
    def dt():
        print('dt')
        time.sleep(4)
        return ''

    def iozone():
        time.sleep(2)
        print('iozone')
        return ''

    def fio():
        aaa
        print('fio')
        time.sleep(1)
        return ''

    def svmotion():
        time.sleep(1)
        print('svmotion')
        return  ''

    def poweroff():
        print('poweroff')
        time.sleep(3)
        return 'off'

    def addvmdk():
        time.sleep(1)
        print('addvmdk')
        return ''

    def addremovevmdk():
        time.sleep(4)
        print('addremovevmdk')
        return ''

    def svmotion():
        time.sleep(2)
        print('svmotion')
        return ''

    def poweron():
        print('poweron')
        time.sleep(1)
        return 'on'

    def resume():
        time.sleep(1)
        print('resume')
        return 'on'

    def suspend():
        time.sleep(1)
        print('resume')
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
        #global stop
        #print('runop')
        try:
            cur_state = 'on'
            for op in steps:
                if stop:
                    break
                #print(op)
                name_to_op[op]()
                sys.stdout.flush()
                if op == 'dt':
                    resultQ.put(False)
                    continue
                resultQ.put(True)
                #stop = True
        except Exception as e:
            print('----%s--------hit except-----------' % threading.current_thread())
            #resultQ.put(False)
            raise e

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
    resultQ = queue.Queue()
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
        for _ in range(50):
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
    print (steps)
    threads = []
    #sys.exit(1)
    for w, s in zip(weight, steps):
        #print('id==', id(w),id(s), w, s)
        #time.sleep(1)
        t = threading.Thread(target=runop, args = (w, s))
        #t.setDaemon(False)
        threads.append(t)
        t.start()
    print(threads)
    while time.time() - start < 20:
        print('in while')
        time.sleep(1)
    print('Waiting for the testing finished...')
    lock.acquire()
    stop = True
    lock.release()
    for t in threads:
        t.join()
    print(resultQ)
    print(resultQ.qsize())
    while not resultQ.empty():
        print(resultQ.get())
    #print(steps)
    #print(weight)

if __name__ in '__main__':
    repo = [10, 20]
    vmops(repo)
