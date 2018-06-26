import socketserver
import signal
import os
import struct
import sys
import socket
import pickle
from threading import Thread
import time
import random
import subprocess
import shlex


def localCmd(cmd):
    args = shlex.split(cmd)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    err = p.returncode
    if err:
        return err, stderr.decode('utf-8')
    else:
        return err, stdout.decode('utf-8')


def ping(address, count=1):
    cmd = 'ping '
    if count:
        cmd += '-c %s ' % count
    cmd += address
    err, output = localCmd(cmd)
    if err:
        ping('Ping %s failed. Output:\n%s' % (address, output))
        return False
    return True


SEVER_PORT = 5001
class Worker(Thread):
    def __init__(self, request, hostname, address):
        super().__init__()
        self.request_ip = address[0]
        self.request_port = SEVER_PORT
        self.hostname = hostname
        self.driver = request['Driver']
        self.esx = request['TestHost']
        self.case = dict(request['Case'])
        if not isinstance(self.case, dict):
            print('Error, not dict')
        self.cmd = request['Cmd']
        self.testbuild = request['TestBuild']
        self.job_id = request['JobID']
        self.skip_setup = request['SkipSetup']
        self.skip_cleanup = request['SkipCleanup']
        if isinstance(self.skip_setup, bool) and isinstance(self.skip_cleanup, bool):
            print('both skip are bool')
        self.others =  request['Others']
    def run(self):
        for _ in range(6):
            if ping(self.esx, 10):
                break
            time.sleep(50)
        self.launch()
    def launch(self):
        os.chdir('/opt/workspace/')
        cmd = ' '.join(['/usr/bin/python', 'Launcher.py', self.esx, self.cmd, '--driver %s' %self.driver, '--test %s' % self.case['Case']])
        log_folder = ''
        print('Starting %s on %s for %s' % (self.case['Case'], self.esx, self.driver))
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(process.stdout.readline, ''):
            line = line.decode('utf-8')
            if not log_folder:
                log_folder = line.partition('Setting logs folder: ')[-1].strip()
                resp = {'result': 'ok',
                        'Driver': self.driver,
                        'TestHost': self.esx,
                        'Case': self.case,
                        'TestLauncher': self.hostname,
                        'JobID': self.job_id,
                        'Status': 1000,
                        'Log': log_folder,
                        'reason': 'get log folder'}
                self.response(resp)
            if line == '' and process.poll() is not None:
                break
        rc = process.returncode
        #time.sleep(random.randint(1,5))
        resp = {'result': 'ok',
                'Driver': self.driver,
                'TestHost': self.esx,
                'Case': self.case,
                'TestLauncher': self.hostname,
                'JobID': self.job_id,
                'Status': rc,
                'Log': log_folder,
                'launcher': self.hostname,
                'Others': '',
                'reason': 'pass case'}
        self.response(resp)
        print('Finished %s on %s for %s. Result %d' % (self.case['Case'], self.esx, self.driver, rc))
    def response(self, resp):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.request_ip, self.request_port))
            pickle_resp = pickle.dumps(resp)
            length = struct.pack('!I', len(pickle_resp))
            pickle_resp = length + pickle_resp
            s.sendall(pickle_resp)
        except socket.error as e:
            print(e)
        finally:
            s.close()
    def triage(self, log_folder):
        def _get_log_content(log_file):
            log_content = ''
            with open(os.path.join(log_folder, log_file)) as fd:
                return fd.read()

LAUNCHER_PORT = 5000 
class TCPServer(object):
    def __init__(self):
        self.threads = []
        self.types = {'task': self.startTask,
                      'query': self.query,
                      'alive': self.isAlive }
        self.hostname = socket.gethostname()

    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('0.0.0.0', LAUNCHER_PORT))
        self.s.listen(1000)
        while True:
            self.conn, address = self.s.accept()
            self.handle(address)

    def shutdown(self):
        if self.s:
            self.s.close()

    def handle(self, address):
        buf = b''
        while len(buf) < 4:
            buf += self.conn.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]
        data = b''
        while length > 0:
            d = self.conn.recv(length)
            length -= len(d)
            data += d
        tmp = pickle.loads(data)
        pickle_data = dict(tmp)

        if not isinstance(pickle_data, dict):
            resp = {'result': 'fail',
                    'reason': 'Bad request' }
            self.response(resp)
            return
        if 'type' not in pickle_data:
            resp = {'result': 'fail',
                    'reason': 'Require task type' }
            self.response(resp)
            return
        else:
            if pickle_data['type'] not in self.types.keys():
                respose = {'result': 'fail',
                           'reason': 'Support operations: %s' % ', '.join(self.types.keys())}
                self.response(resp)
                return
        self.types[pickle_data['type']](pickle_data, address)

    def response(self, resp):
        pickle_resp = pickle.dumps(resp)
        try:
            self.conn.sendall(pickle_resp)
        except Exception as e:
            self.conn.close()

    def fix(self):
        for th in self.threads[:]:
            if not th.is_alive():
                self.threads.remove(th)

    def startTask(self, request, address):
        task_worker = Worker(request, self.hostname, address)
        #task_worker.daemon = True
        task_worker.start()
        self.threads.append(task_worker)
        if not task_worker.is_alive():
            resp = {'result':'fail',
                    'reason':'sorry'}
        else:
            resp = {'result': 'ok',
                    'reason': 'null' }
        self.response(resp)
        self.fix()

    def query(self, request, address):
        self.fix()
        resp = {'result':'ok',
                'job_num': len(self.threads)}
        self.response(resp)

    def isAlive(self, request, address):
        resp = {'result':'ok'}
        self.response(resp)

def daemonize(self, stdin='/dev/null', stdout='/dev/null', stderr='dev/null'):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write('fork #1 failed: %s:%d' % (e.strerror, e.errno))
        sys.exit(1)
    os.chdir('/')
    os.umask(0)
    os.setsid()
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write('fork #2 failed: %s:%d' % (e.strerror, e.errno))
        sys.exit(1)
    for fd in sys.stdout, sys.stderr:
        fd.flush()
    std_in = open(stdin, 'r')
    std_out = open(stdout, 'a+')
    std_err = open(stderr, 'a+')
    os.dup2(std_in.fileno(), sys.stdin.fileno())
    os.dup2(std_out.fileno(), sys.stdout.fileno())
    os.dup2(std_err.fileno(), sys.stderr.fileno())

def signalHandler(signum, frame):
    raise KeyboardInterrupt()

def main():
    server = TCPServer()
    #server = socketserver.ThreadingTCPServer((HOST, PORT), TCPRequestHandler)
    #daemonize('/dev/null', '/tmp/stdout', '/tmp/stderr')
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    try:
        server.start()
    except (KeyboardInterrupt, OSError):
        server.shutdown()
        sys.exit(1)

if __name__ == '__main__':
    main()
