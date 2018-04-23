from lock_between_process import lockServer, mutexLock
from concurrent.futures import ProcessPoolExecutor
import time
import random

key = ['host', 'lsi_msgpt3', 'lsi_mr3', 'novm_reset', 'loadunload', 'smart']

def send_A():
    lock_type = random.choice(key)
    timeout = random.choice([0, 50, 80])
    print('send_A %s %s' % (lock_type, timeout))
    with mutexLock(lock_type=lock_type, timeout=timeout):
        time.sleep(random.randint(0, 90))

def send_B():
    lock_type = random.choice(key)
    timeout = random.choice([0, 40, 70])
    m = mutexLock(lock_type=lock_type, timeout=timeout)
    r = m.lock()
    print('send_B %s %s, revice %s' % (lock_type, timeout, str(r)))
    time.sleep(random.randint(0, 90))
    m.unlock()

if '__main__' == __name__:
    pool = ProcessPoolExecutor(20)
    for _ in range(20):
        time.sleep(random.randint(0, 8))
        pool.submit(send_A) 
        time.sleep(random.randint(0, 5))
        pool.submit(send_B) 
