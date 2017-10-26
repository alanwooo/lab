import time
#from multiprocessing.pool import ThreadPool as Pool
from multiprocessing.pool import Pool
import multiprocessing

def runJob(inQ, outQ):
    print('heheh')
    try:
        while True:
            print('hahah')
            job = inQ.get()
            if job == 'stop':
                outQ.put('Stop')
                break
            con = job.get('con')
            aaa
            testId = job.get('testId')
            time.sleep(1)
            print('con=%s, testId=%s' % (con, testId))
            time.sleep(3)
            outQ.put('Done')
    except Exception as e:
       print(e)
       outQ.put('Stop')

def worker(inQList, outQ):
    multiprocessing.log_to_stderr()
    #p = LoggingPool(processes=num)
    p = Pool(processes=len(inQList))
    for inQ in inQList:
        p.apply_async(runJob, args=(inQ,outQ))

def main():
    num = 4
    inMg = multiprocessing.Manager()
    outMg = multiprocessing.Manager()
    inQList = [inMg.Queue(maxsize=1) for _ in range(num)]
    outQ = outMg.Queue()
    worker(inQList, outQ)

    L = [] 
    for i in range(15):
        L.append({'con':i, 'testId':id(i)})

    i = 0
    ret = []
    while True:
        for q in inQList:
            if i == len(L):
                break
            #print('')
            if not q.full():
                q.put(L[i])
                i += 1
            time.sleep(1)
        while not outQ.empty():
            ret.append(outQ.get())
        if len(L) == len(ret) or ret.count('Stop') == 4:
            break
        time.sleep(1)
    print(ret)

if __name__ == '__main__':
    main()
        
