#!/usr/bin/python -u

import os
import re
import sys
import copy
import time
import math
import random
import signal
import traceback
import subprocess
from pprint import pprint
from functools import partial
from collections import defaultdict
from threading import Thread
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, wait

from lib.esxlib import _run_cmd, get_dump_partition_device, is_native_driver, get_boot_device
from lib.esxlib import unmount_datastores, get_driver_vmhba_device_map, mount_datastores, get_vmhbas_devices_map
from lib.esxlib import getPciDeviceFullPath

from testapi import TestLogger
log = TestLogger('scheduler')
log.info('Let us start ...')

if not os.path.exists('/tmp/log'):
    os.mkdir('/tmp/log')

# interval to check job status, second
CHECKINTERVAL = 20
# max workers in thread pool
MAXWORKERS = 3
# case dir
CASEDIR = os.path.join(os.environ['TESTESX_DIR'], 'hwe/storagedriver/')
# block placeholder
HEAD = '# _ATTRIBUTE_BLOCK_START_'
END = '# _ATTRIBUTE_BLOCK_END_'
# case arrtibute
CASEATTRIBUTE = ['name', 'score','vmnum','parallel', 'group', 'runtime', 'auxdatastore','validdriver', 'nonvaliddriver', 'category']
# log folder
#if not os.environ['TESTESX_TESTROOT']:
#    raise RuntimeError('Can not get the test esx root dir.')
CASELOGDIR = os.environ['TESTESX_TESTROOT'] 
placeholder = object()
PASS = 0
FAIL = 1
KILL = 2
print_print = print

class CustomExitError(RuntimeError):
    pass

def cli(option):
    try:
        return runCli(option.split(), True)
    except Exception as e:
        print_print(e)
        raise e

class Case():
    """
    Each testcase.py will be a Case instance.
    """
    __slots__ = ['filepath'] + CASEATTRIBUTE
    def __init__(self):
        self.score = '2'
    def __str__(self):
        return self.name
    def __getattr__(self, name):
        if name in Case.__slots__:
            # user may not define the following attribute
            if name in ['validdriver', 'nonvaliddriver']:
                return []
            if name in ['vmnum']:
                return 0
            return None
        if name not in Case.__slots__:# and not name.startswith('__'):
            raise AttributeError('Case does not have attribute %s, case only have the following attribute:\n%s' % (name, ', '.join(Case.__slots__[1:])))
    def __setattr__(self, name, value):
        if name in ['score', 'vmnum', 'runtime']:
            if not value.isdigit():
                raise AttributeError('Case attribute value %s should be int, not %s' % (name, value))
            value = int(value)
        super().__setattr__(name, value)

class Parser():
    """
    Parse all the testcase.py
    """
    def __init__(self):
        self.caseDir = CASEDIR
        self.cases = []
        print_print('Starting to load test cases ...')
        self._loadCase()
        print_print('Loading test case done.')
    def _parseCaseFile(self, filepath):
        case = Case()
        def _skiphead(fd):
            for line in fd:
                if HEAD in line:
                    break
        def _readCfg(fd):
            _skiphead(fd)
            for line in fd:
                 if END in line:
                     raise StopIteration
                 m = re.match('^# (\D*): (.*)\n', line)
                 if not m:
                     yield (re.match('^# (\D*):\s', line).groups()[0], '')
                 else:
                     yield m.groups()
        def _checkCase(case):
            if case.category and case.name and case.runtime:
                return
            raise RuntimeError('category, name, parallel, runtime must be set in %s' % filepath)
        with open(filepath, 'r') as fd:
            for key, val in _readCfg(fd):
                if key not in CASEATTRIBUTE or not val: 
                    continue
                if not key:
                    raise RuntimeError('file %s format not correct' % filepath)
                if ',' in val:
                    setattr(case, key, val.replace(' ', '').split(','))
                    continue
                setattr(case, key, val.strip())
        try:
            if case.name:
                setattr(case, 'filepath', filepath)
                _checkCase(case)
                self.cases.append(case)
        except AttributeError as e:
            print_print('Case attribute define is not correct.')
            del case
    def _loadCase(self):
        for root, dirs, files in os.walk(self.caseDir, topdown=True):
            for filename in files:
                if filename.startswith(('.', '#')) or filename.endswith('~'):
                   continue
                casePath = os.path.join(root, filename)
                if os.access(casePath, os.X_OK):
                    filepath = os.path.realpath(casePath)
                    self._parseCaseFile(filepath)

class Driver(ABC):
    """
    Driver
    """
    def __init__(self, esx, name, category):
        self.esx = esx
        self.name = name
        self.category = category
        self.cases = []
        self.done_cases = []
        self.done = False
        self.last_case = None
    def __str__(self):
        return self.name
    @abstractmethod
    def pickDevice(self):
        return ''

class NetworkDriver(Driver):
    """
    For network driver
    """
    def __init__(self, esx, name, category):
        super().__init__(name, category)
    def pickDevice(self):
        return ''
        
class StorageDriver(Driver):
    """
    For storage driver
    """
    def __init__(self, esx, name, category):
        super().__init__(esx, name, category)
        self._selectCase()
    def _selectCase(self):
        for case in self.esx.cases:
            if self.name.replace('_unstable', '') in case.nonvaliddriver:
                continue
            if case.validdriver:
                if self.name.replace('_unstable', '') in case.validdriver:
                    self.cases.append(case)
            else:
                self.cases.append(case)
    def pickDevice(self):
        if not self.esx.driver2device[self.name]:
            raise RuntimeError('Error to get device')
        return random.choice(self.esx.driver2device[self.name])
    def pop(self, group=False, score=0):
        # TODO test case or less than score test case
        select_case = None
        if not self.cases:
            return select_case
        if group:
            for case in self.cases:
                if self.last_case.group == case.group:
                    select_case = case
                    break
        if not select_case:
            select_case = random.choice(self.cases)
        # remove the test case if selected
        self.cases.remove(select_case)
        # record the last running test case
        self.last_case = select_case
        return select_case
    def add(self, case):
        self.cases.append(case)
    def caseDone(self, test):
        self.done_cases.append((test.case.name, test.result, test.log))

class EsxHost():
    """
    ESXi
    """
    def __init__(self, cases):
        self.cases = cases
        self.result = PASS
        self.stor_drvs = []
        self.nic_drvs = []
        # platform info
        self.cpu = self._getCPU()
        self.memory = self._getMemory()
        self.build = self._getBuild()
        # score
        self.score = (self.cpu['numCores'], self.memory['physmem'])[self.cpu['numCores'] > self.memory['physmem']]
        self.score = 8
        self.cur_score = 0
        # nic drivers
        self.mgmt_nic = self._getMgmtNic()
        self.nics, self.driver2vmnic = self._getNics()
        # can not use storage devices
        self.boot_device = get_boot_device()
        self.dump_device = [dev.split(':')[0] for dev in get_dump_partition_device() if dev]
        # TODO remove the following line
        self.boot_device = ''
        self.dump_device = ''
        self.test_esx_device = self._getTestEsxUsedDevice()
        # TODO put the auxDatastore into unavailable_device
        self._auxDatastore = self._getAuxDatastore()
        # unavailable drivers
        self.unavailable_device = set([dev for dev in [self.boot_device, *self.dump_device, *self.test_esx_device] if dev])
        self.unavailable_nics = []
        # storage driver info
        self.vmhbas, self.devices, self.driver2vmhbas, self.driver2device,\
            self.vmhbas2device, self.device2vmhbas, self.device2driver = self._getStorage() 
        # available driver for testing
        self.avail_storage_driver = [key for key, val in self.driver2device.items() if len(val)]
        self.avail_network_driver = []
        
        self._initStorageDriver()
        self.running_storage_driver = []
        self.running_network_driver = []

        self.running_jobs = []
        self.done_workers= []
        self.transient_workers = []
        self.finished = defaultdict(list)

        self.driver2case = defaultdict(list)
        #self._mapDriver2Case()
        # ######
        self.running_workers = []
        #self.running_drivers = []
        self.done_drivers = []

    def _initStorageDriver(self):
        # TODO init network drivers
        for drv in self.avail_storage_driver:
            d = StorageDriver(self, drv, 'storage')
            self.stor_drvs.append(d)
        print_print('Unavailable drivers: %s' % ', '.join([drv for drv in list(self.unavailable_device) + list(self.unavailable_nics)]))
        print_print('Available drivers: %s' % ', '.join([drv.name for drv in self.stor_drvs + self.nic_drvs]))
        for drv in self.stor_drvs + self.nic_drvs:
            print_print('%s has %d test cases: %s' % (drv, len(drv.cases), ', '.join([case.name for case in drv.cases])))
    def _getTestEsxUsedDevice(self):
        return ''
    def _getAuxDatastore(self):
        filesystem = cli('storage filesystem list')
        for f in filesystem:
            if not f['Volume Name']:
               return f['Volume Name']
    def _mapDriver2Case(self):
        for case in self.case_list:
            if case.category == 'storage':
                for drv in self.avail_storage_driver:
                    if drv in case.nonvaliddriver:
                        continue
                    self.driver2case[drv].append(case)
    def _getCPU(self):
        cpu = vsi.get('/hardware/cpu/cpuInfo')
        if not cpu:
           print_print('Failed to get bios vsish node.')
           return {}
        return {'numPackages': cpu['numPackages'],
                'numCores': cpu['numCores'],
                'nvoa': cpu['nvoa'] }
    def _getMemory(self):
        memory = vsi.get('/memory/comprehensive')
        if not memory:
            print_print('Failed to get memory.')
            return {}
        return { 'physmem': math.ceil(memory['physmem']/1024/1024) }
    def _getMgmtNic(self):
        nics = []
        sws = cli('network vswitch standard list')
        for sw in sws:
            if 'Management Network' in sw['Portgroups']:
                nics.append(sw['Uplinks'][0])
        return nics
    def _getNics(self):
        nics = defaultdict(dict)
        driver2vmnic = defaultdict(list)
        res = cli('network nic list')
        nic_drvs = {item['Driver'] for item in res}
        for item in res:
            details = {}
            vmnic = item['Name']
            driver = item['Driver']
            details['Driver'] = driver
            details['PCI Device'] = item['PCI Device']
            details['Link Status'] = item['Link Status']
            details['Speed'] = item['Speed']
            details['MAC Address'] = item['MAC Address']
            details['Description'] = item['Description']
            nics[vmnic] = details
            driver2vmnic[driver].append(vmnic)
        return nics, driver2vmnic
    @property
    def auxDatastore(self):
        return self._auxDatastore
    @auxDatastore.setter
    def auxDatastore(self):
        raise RuntimeError('Can not change auxDatastore.')
    @property
    def vmfs(self):
        return '/vmfs/volumes'
    @property
    def disk(self):
        return '/vmfs/devices/disks'
    @property
    def kernelLog(self):
        return '/var/log/vmkernel.log'
    def _getBuild(self):
        build = vsi.get('/system/version')
        return { 'Build Number': build['buildVersionNumeric'],
                 'Build Type': build['buildType'],
                 'Build Version': build['productVersion'] }
    def _getStorage(self):
        vmhbas = defaultdict(dict)
        devices = defaultdict(dict)
        driver2vmhbas = defaultdict(list)
        driver2device = defaultdict(list)
        vmhbas2device = defaultdict(list)
        vmhba2driver = {}
        device2vmhba = {}
        adapter = cli('storage core adapter list')
        for a in adapter:
            driver = a['Driver']
            vmhba = a['HBA Name']
            vmhbas[vmhba] = copy.deepcopy(a)
            driver2vmhbas[driver].append(vmhba)
            vmhba2driver[vmhba] = driver
        path = cli('storage core path list')
        for p in path:
            device = p['Device']
            vmhba = p['Adapter']
            device2vmhba[device] = vmhba
        useless_device = []
        dev = cli('storage core device list')
        for d in dev:
            device = d['Device']
            if device in self.unavailable_device:
                continue
            if d['Size'] < 1024:
                useless_device.append(device)
                continue
            devices['device'] = copy.deepcopy(d)
            vmhba = device2vmhba[device]
            driver = vmhba2driver[vmhba]
            vmhbas2device[vmhba].append(device)
            driver2device[driver].append(device)
        del vmhba2driver
        del device2vmhba
        for key, val in vmhbas2device.items():
            for dev in useless_device:
                if dev in val:
                    val.remove(dev)
        device2vmhbas = { dev:key for key, val in vmhbas2device.items() for dev in val }
        device2driver = { dev:key for key, val in driver2device.items() for dev in val } 
        #pprint(vmhbas)
        #pprint(devices)
        #pprint(driver2vmhbas)
        #pprint(driver2device)
        #pprint(vmhbas2device)
        #pprint(device2vmhbas)
        #pprint(device2driver)
        return (vmhbas, devices, driver2vmhbas, driver2device, vmhbas2device, device2vmhbas, device2driver)
    # must called before pickDriver function
    def fixJob(self):
        #print_print('fixJob done workers ========== %s' % self.done_workers)
        #print_print('fixJob done case driver ============ %s' % [worker.test.driver.name for worker in self.done_workers])
        while self.done_workers:
            # remove worker in running workers list
            worker = self.done_workers.pop()
            #print_print('====worker====%s====test====%s=====' % (worker, worker.test))
            worker.test.driver.caseDone(worker.test)
            self.cur_score -= worker.test.case.score
            result = worker.test.result
            print_print('%s test case %s done, result %s' % (worker.test.driver.name, worker.test.case.name, 'PASS' if not result else 'FAIL' if result == FAIL else 'KILL'))
            if not result:
                self.result = FAIL
            # append work to the transient list, so we can firstly select the job to run from this list
            self.transient_workers.append(worker)
            #for x in worker.test.driver.done_cases:
                #print_print('==driver %s==done %s====' % (worker.test.driver, x))
        #print_print('pickDriver transient drivers 0_0 ========== %s' % [worker.test.driver.name for worker in self.transient_workers])
        #print_print('pickDriver running drivers 0_0: ======== %s' % [worker.test.driver.name for worker in self.running_workers])
        #print_print('pickDriver running workers 0_0 ======  %s' % self.running_workers)
    def pickDriver(self):
        select_driver = None
        drivers = []
        # just start, no running and transient driver
        #print_print('pickDriver running workers 1_1 ======  %s' % self.running_workers)
        #print_print('pickDriver running drivers 1_1: ======== %s' % [worker.test.driver.name for worker in self.running_workers])
        #print_print('pickDriver transient drivers 1_1 ========== %s' % [worker.test.driver.name for worker in self.transient_workers])
        for worker in self.transient_workers:
            if worker in self.running_workers:
                self.running_workers.remove(worker)
        #print_print('pickDriver running drivers 2_2: ======== %s' % [worker.test.driver.name for worker in self.running_workers])
        if not self.transient_workers:
            drivers = self.nic_drvs + self.stor_drvs
            for driver in self.done_drivers:
                drivers.remove(driver)
            for worker in self.running_workers:
                drivers.remove(worker.test.driver)
            if drivers:
                select_driver = random.choice(drivers)
                drivers.remove(select_driver)  # TODO remove this line
        else:
            while self.transient_workers:
                done_worker = self.transient_workers.pop()
                if done_worker.test.driver.cases:
                    select_driver = done_worker.test.driver
                    break
                else:
                    self.done_drivers.append(done_worker.test.driver)
            else:
                # nothing to do here, wait to next cycle to pickup driver
                pass
        #print_print('pickDriver running drivers 3_3: ======== %s' % [worker.test.driver.name for worker in self.running_workers])
        #print_print('pickDriver transient drivers 2_2 ========== %s' % [worker.test.driver.name for worker in self.transient_workers])
        #print_print('pcikDriver reset drivers ========== %s ' % [drv.name for drv in drivers])
        #print_print('pickDriver done_drivers ======== %s' % [drv.name for drv in self.done_drivers])
        #print_print('pickDriver pickup driver ======== %s' % select_driver)
        return select_driver
    def pickJob(self):
        #print_print('cur_score %d, score %d' % (self.cur_score, self.score))
        self.fixJob()
        if self.cur_score >= self.score:
            #print_print('^^^^^^^^^^^^^^^^^^^^^^^^^score is more than 8 < %d' % self.cur_score)
            return placeholder
        select_driver = self.pickDriver()
        #print_print('pickJob&&&&&& done drivers %s' % [ str(drv) for drv in self.done_drivers])
        if not select_driver:
            # this mean, all the drivers testing was done, so return None to quite scheduler
            if len(self.done_drivers) == len(self.nic_drvs + self.stor_drvs) and not self.running_workers and not self.transient_workers:
                return None
            return placeholder
        case = select_driver.pop()
        if not case:
            return placeholder
        self.cur_score += case.score
        test = Test(case, select_driver, {})
        print_print('Pick up %s for %s' % (case, select_driver))
        return Worker(test)

class Test():
    """
    The test will be sent to a worker to run
    """
    def __init__(self, case, driver, addendum):
        self.runtime = case.runtime
        self.timeout = int(self.runtime * 1.5)
        self.script = case.filepath
        self.driver = driver
        self.name = case.name
        self.case = case
        self.result = FAIL
        #self.log = '/tmp/log/info.log.%d' % int(time.time() * 10000)
        self.log = os.path.join(os.environ['TESTESX_TESTROOT'], '%s_%s.py' % (self.driver, self.name))
        self.device = self.driver.pickDevice()
        if isinstance(addendum, dict):
            self.addendum = addendum
        else:
            raise RuntimeError('addendum arguments should be dict.')
    def __str__(self):
        return '%s:%s:%s' % (self.driver, self.name, self.log)
    @property
    def cmd(self):
        return [self.script]
    @property
    def env(self):
        env = {'HWE_DEVICE': self.device}
        for attr in ['runtime', 'timeout', 'driver']:
            env.update({'HWE_%s' % attr.upper():str(getattr(self, attr))})
        env.update(self.addendum)
        env.update(dict(os.environ))
        return env

class Worker(): 
    """
    A worker is a job, will be put into thread pool to run
    """
    def __init__(self, test):
        #self.id = int(time.time() * 10000)
        self.test = test
        self.cmd = test.cmd
        self.runtime = test.runtime
        self.timeout = test.timeout
        self.stdout = open(test.log, 'w+b')
        self.stdin = open('/dev/zero', 'rb')
    def submit(self):
        testTmpDir=os.environ['TESTESX_TMPDIR']
        env = {}
        env.update(dict(os.environ))
        env.update(self.test.env)
        self.proc = subprocess.Popen(self.cmd, stdin=self.stdin, stdout=self.stdout,
                                stderr=subprocess.STDOUT, close_fds=True, env=env,
                                preexec_fn=os.setpgrp, cwd=testTmpDir)
    def waitTime(self):
        return [CHECKINTERVAL for _ in range(int((self.timeout + 100 + CHECKINTERVAL)/CHECKINTERVAL))]
    def kill(self):
        print_print('%s(PID:%s) killed by Ctrl-C' % (self.test.case.name, self.proc.pid))
        try:
            os.killpg(self.proc.pid, signal.SIGINT)
        except ProcessLookupError as e:
            return
        #try:
        #    self.proc.wait(60)
        #except TimeoutExpired as e:
        #    print(e)
        #    self.proc.terminate()
    def run(self):
        killed = False
        self.submit()
        start = time.time()
        wait_time= self.waitTime()
        for t in wait_time:
            time.sleep(t)
            #print_print('*********pid %s, %s, runtime %s, timeout %s, poll %s, time escape %s' % (self.proc.pid, wait_time, self.runtime, self.timeout, self.proc.poll(), time.time() - start))
            if self.proc.poll() is None:
                continue
            #print_print('break here time escape:%s, t:%s, wait_time:%s, pid:%s' % (time.time() - start, t, wait_time, self.proc.pid))
            break
        else:
            print_print('Timeout: test case %s runtime is %d, timeout is %d, process id is %s, currently run %s seconds, kill it.' % (self.test.case, self.runtime, self.timeout, self.proc.pid, int(time.time() - start)))
            os.killpg(self.proc.pid, signal.SIGINT)
            killed = True
            try:
                self.proc.wait(20)
            except TimeoutExpired as e:
                print_print(e)
                self.proc.terminate()
        #print_print('########################t:%s, runtime:%s, timeout:%s, time escape:%s, pid:%s, return code %d' % (t, self.runtime, self.timeout, time.time() - start, self.proc.pid, self.proc.returncode))
        if not self.proc.returncode:
            self.test.result = PASS
        if killed:
            self.test.result = KILL
        return self.proc.returncode
class WorkerPool(ThreadPoolExecutor):
    """
    Threads pool to run workers
    """
    def __init__(self, *args, **kwargs):
        self.job2worker = kwargs.pop('job2worker')
        super().__init__(*args, **kwargs)
    def __fix(self, job_state):
        workers = []
        for job in job_state.done:
            if job.exception() is not None:
                print_print('Job %s hit exception: %s result: %s' % (job, job.exception(), job.result()))
            #else:
            #    print_print('job %s result %s' % (job, job.result()))
            if job in self.job2worker:
                workers.append(self.job2worker[job])
                self.job2worker.pop(job)
        return workers
    def submit(self, worker):
        job = super().submit(worker.run)
        self.job2worker[job]=worker
    def __enter__(self):
        def signalHandle(job2worker, signum, frame):
            #print_print(signum, frame, job2worker)
            print_print('Revice Ctrl-C, please wait to kill all the running jobs...')
            for _, worker in job2worker.items():
                worker.kill()
            raise CustomExitError()
        signal.signal(signal.SIGINT, partial(signalHandle, self.job2worker))
        return super().__enter__()
    def __exit__(self, exc_type, exc_val, exc_tb):
        #print_print(self, exc_type, exc_val, exc_tb)
        if exc_type is CustomExitError:
            super().__exit__(None, None, None)
        else:
            traceback_string = ''
            for line in traceback.format_tb(exc_tb):
                traceback_string += line
            print_print('Hit exception, exception type: %s, exception val: %s, exception traceack:\n%s' % (exc_type, exc_val, traceback_string))
            super().__exit__(exc_type, exc_val, exc_tb)
def scheduler():
    """
    Test case scheduler
    """
    print_print(os.environ['TESTESX_TESTROOT'])
    print_print('%s'%(os.getcwd()))
    for key, val in dict(os.environ).items():
        print('%s:%s' % (key, val))
    p = Parser()
    print_print('Got total %d test cases: %s' % (len(p.cases), ', '.join([case.name for case in p.cases])))
    if not len(p.cases):
        print_print('Did not get any test cases, please make sure the test cases folder is correct.')
        return FAIL
    esx = EsxHost(p.cases)
    #return 0
    job2worker = {}
    with WorkerPool(job2worker=job2worker, max_workers=MAXWORKERS) as pool:
        while True:
            time.sleep(1)
            if pool.job2worker:
                job_state = wait(list(job2worker.keys()), 5)
                #print_print('full job queue, sleep 5 second, job state %s' % str(job_state))
                if job_state.done:
                    done_workers = pool._WorkerPool__fix(job_state)
                    if done_workers:
                        esx.done_workers.extend(done_workers)
            if len(pool.job2worker) < MAXWORKERS:
                worker = esx.pickJob()
                if worker is None:
                    break
                if worker is placeholder:
                    #print_print('no worker selected, sleep 2 second')
                    time.sleep(2)
                    continue
                pool.submit(worker)
                esx.running_workers.append(worker)
    print_print('Finished all the tests.\n')
    print_print('**********************Test Report********************')
    for drv in esx.stor_drvs + esx.nic_drvs:
        print_print('>>>>>>>>>%s total run %d cases:<<<<<<<<<' % (drv, len(drv.done_cases)))
        for name, result, log in drv.done_cases:
            print_print('%-15s %-30s %-4s   %s' % (drv, name, 'PASS' if not result else 'FAIL' if result == FAIL else 'KILL', log))
    print_print('*****************************************************')
    print_print('All Tests Result: %d' % esx.result)
    return esx.result

if '__main__' == __name__:
    sys.exit(scheduler())
