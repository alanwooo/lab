import os
import re
import copy
import time
import random
import signal
from pprint import pprint
from functools import partial
import subprocess
from collections import defaultdict
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait

placeholder = object()

if not os.path.exists('log'):
    os.mkdir('log')

class CustomExitError(RuntimeError):
    pass
class EsxHost():
    def __init__(self):
        self.total = 0
    def pickJob(self):
        self.total += 1
        print('total is %d' % self.total)
        if self.total >= 10:
            return None
        runtime = random.randint(10, 30)
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
        env = {'VMBLD': 'VM%s' % time.time()}
        self.proc = subprocess.Popen(self.cmd, stdin=self.stdin, stdout=self.stdout,
                                stderr=subprocess.STDOUT, close_fds=True, env=env,
                                preexec_fn=os.setpgrp, cwd=testTmpDir)
    def wait(self):
        return [10, self.runtime, 60, 30,  self.timeout - self.runtime]
    def kill(self):
        print('%s killed by Ctrl-C' % self.proc.pid)
        try:
            os.killpg(self.proc.pid, signal.SIGINT)
        except ProcessLookupError as e:
            return
        try:
            self.proc.wait(60)
        except TimeoutExpired as e:
            print(e)
            self.proc.terminate()
    def run(self):
        self.submit()
        start = time.time()
        wait_time= self.wait()
        for t in wait_time:
            time.sleep(t)
            if self.proc.poll() is None:
                continue
            print('break here, pid %s, wait time: %s, runtime %s, timeout %s, poll %s, time escape %s' % (self.proc.pid, wait_time, self.runtime, self.timeout, self.proc.poll(), time.time() - start))
            break
        else:
            print('========timeout======pid %s hit timeout, time escap:%s, timeout %s, runtime %s, wait time %s' % (self.proc.pid, time.time() - start, self.timeout, self.runtime, wait_time))
            # we do not use self.proc.send_signal, since it will send to all the thread in ThreadPoolExecutor, also add preexec_fn=os.setpgrp in subprocess.Popen
            #self.proc.send_signal(signal.SIGINT)
            os.killpg(self.proc.pid, signal.SIGINT)
            try:
                self.proc.wait(20)
            except TimeoutExpired as e:
                print(e)
                self.proc.terminate()
        print('poll %s, t:%s, runtime:%s, timeout:%s, time escape:%s, pid:%s, return code %d' % (self.proc.poll(), t, self.runtime, self.timeout, time.time() - start, self.proc.pid, self.proc.returncode))
        return self.proc.returncode

class WorkerPool(ThreadPoolExecutor):
    def __init__(self, *args, **kwargs):
        #print(kwargs)
        self.job2worker = kwargs.pop('job2worker')
        super().__init__(*args, **kwargs)
    def __fix(self, job_state):
        for job in job_state.done:
            if job.exception() is not None:
                print('job %s hit exceptioni %s' % (job, job.exception()))
            else:
                print('job %s result %s' % (job, job.result()))
            if job in self.job2worker:
                self.job2worker.pop(job)
    def submit(self, worker):
        job = super().submit(worker.run)
        self.job2worker[job]=worker
    def __enter__(self):
        def signalHandle(job2worker, signum, frame):
            print(signum, frame, job2worker)
            print('revice kill in main...')
            for _, worker in job2worker.items():
                worker.kill()
            raise CustomExitError('kill all the jobs')
        signal.signal(signal.SIGINT, partial(signalHandle, self.job2worker))
        return super().__enter__()
    def __exit__(self, exc_type, exc_val, exc_tb):
        #print(self, exc_type, exc_val, exc_tb)
        if exc_type is CustomExitError:
            print('killed by the ctrl-c')
            return super().__exit__(None, None, None)
        super().__exit__(exc_type, exc_val, exc_tb)
def main():
    esx = EsxHost()
    job2worker = {}
    with WorkerPool(job2worker=job2worker, max_workers=8) as pool:
        while True:
            time.sleep(1)
            #print('pool.jobs %s' % pool.jobs)
            if len(pool.job2worker) < 8:
                worker = esx.pickJob()
                if worker is placeholder:
                    print('no worker selected, sleep 2 second')
                    time.sleep(2)
                    continue
                if worker is None:
                    wait(list(job2worker.keys()))
                    print('all job done')
                    break
                pool.submit(worker)
            if len(pool.job2worker) >= 8:
                job_state = wait(list(job2worker.keys()), 5)
                print('full job queue, sleep 5 second, job state %s' % str(job_state))
                pool._WorkerPool__fix(job_state) 

if '__main__' == __name__:
    main()
