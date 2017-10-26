from queue import Queue
import time
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing

def runJob(inQ, outQ):
    print('heheh')
    while True:
        print('hahah')
        job = inQ.get()
        if job == 'stop':
            break
        con = job.get('con')
        testId = job.get('testId')
        time.sleep(1)
        print('con=%s, testId=%s' % (con, testId))
        time.sleep(3)
        outQ.put('Done')

def worker(num, inQList, outQ):
    multiprocessing.log_to_stderr()
    #p = LoggingPool(processes=num)
    p = Pool(processes=num)
    for i in range(num):
        p.apply_async(runJob, args=(inQList[i],outQ))

def main():
    num = 4
    inQList = [Queue(maxsize=1) for _ in range(num)]
    outQ = Queue()
    worker(num, inQList, outQ)

    L = [] 
    for i in range(15):
        L.append({'con':i, 'testId':id(i)})

    i = 0
    ret = []
    while True:
        for q in inQList:
            if i == len(L):
                break
            if not q.full():
                q.put(L[i])
                i += 1
            time.sleep(1)
        while not outQ.empty():
            ret.append(outQ.get())
        if len(L) == len(ret):
            break
        time.sleep(1)
    print(ret)

if __name__ == '__main__':
    main()
        
