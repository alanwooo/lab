import os
import re
import copy
import time
import random
import signal
from pprint import pprint
import subprocess
from collections import defaultdict
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait

placeholder = object()

if not os.path.exists('log'):
    os.mkdir('log')

class EsxHost():
    def __init__(self):
        self.total = 0
    def pickJob(self):
        self.total += 1
        print('total is %d' % self.total)
        if self.total >= 60:
            return None
        runtime = random.randint(100, 300)
        if not runtime % 13:
            if not runtime % 3:
                print('get runtime %s, runtime is multiple of 3 and 13' % runtime)
            else:
                print('get runtime %s, multiple of 13' % runtime)
        if not runtime % 3:
            print('runtime is %d' % runtime)
            return placeholder
        script = 'sleep'
        log = 'log/%s' % str(time.time())
        test = Test(script, runtime, log)
        job = Worker(test)
        return job

class Driver():
    def __init__(self):
        self.auxDatastore
        pass
class Test():
    def __init__(self, script, runtime, log):
        self.runtime = runtime
        self.timeout = int(runtime * 1.5)
        self.script = script
        self.log = log
    @property
    def cmd(self):
        return [self.script, str(self.runtime)]
class Worker(): 
    def __init__(self, test):
        self.cmd = test.cmd
        self.runtime = test.runtime
        self.timeout = test.timeout
        self.stdout = open(test.log, 'w+b')
        self.stdin = open('/dev/zero', 'rb')
    def submit(self):
        testTmpDir='./'
        env = {'VMBLD': 'VM'}
        return subprocess.Popen(self.cmd, stdin=self.stdin, stdout=self.stdout,
                                stderr=subprocess.STDOUT, close_fds=True, env=env,
                                preexec_fn=os.setpgrp, cwd=testTmpDir)
    def wait(self):
        return [10, self.runtime, 60, 30,  self.timeout - self.runtime]
           
    def run(self):
        w = self.submit()
        start = time.time()
        wait_time= self.wait()
        for t in wait_time:
            time.sleep(t)
            if w.poll() is None:
                continue
            print('break here, pid %s, wait time: %s, runtime %s, timeout %s, poll %s, time escape %s' % (w.pid, wait_time, self.runtime, self.timeout, w.poll(), time.time() - start))
            break
        else:
            print('========timeout======pid %s hit timeout, time escap:%s, timeout %s, runtime %s, wait time %s' % (w.pid, time.time() - start, self.timeout, self.runtime, wait_time))
            # we do not use w.send_signal, since it will send to all the thread in ThreadPoolExecutor, also add preexec_fn=os.setpgrp in subprocess.Popen
            #w.send_signal(signal.SIGINT)
            os.killpg(w.pid, signal.SIGINT)
            try:
                w.wait(20)
            except TimeoutExpired as e:
                print(e)
                w.terminate()
        print('poll %s, t:%s, runtime:%s, timeout:%s, time escape:%s, pid:%s, return code %d' % (w.poll(), t, self.runtime, self.timeout, time.time() - start, w.pid, w.returncode))
        return w.returncode

class WorkerPool(ThreadPoolExecutor):
    def __init__(self, *args, **kwargs):
        #print(kwargs)
        self.jobs = kwargs.pop('jobs')
        super().__init__(*args, **kwargs)
    def __fix(self, job_state):
        for job in job_state.done:
            if job.exception() is not None:
                print('job %s hit exceptioni %s' % (job, job.exception()))
            else:
                print('job %s result %s' % (job, job.result()))
            self.jobs.remove(job)
    def submit(self, func):
        job = super().submit(func)
        self.jobs.append(job)
def main():
    esx = EsxHost()
    jobs = []
    with WorkerPool(jobs=jobs, max_workers=8) as pool:
        while True:
            time.sleep(1)
            #print('pool.jobs %s' % pool.jobs)
            if len(pool.jobs) < 8:
                job = esx.pickJob()
                if job is placeholder:
                    print('no job selected, sleep 5 second')
                    time.sleep(5)
                    continue
                if job is None:
                    wait(pool.jobs)
                    print('all job done')
                    break
                pool.submit(job.run)
            if len(pool.jobs) >= 8:
                job_state = wait(pool.jobs, 5)
                #print('full job queue, sleep 5 second, job state %s' % str(job_state))
                pool._WorkerPool__fix(job_state) 

if '__main__' == __name__:
    main()
