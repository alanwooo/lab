import os
import sys
import random
import time
import pickle
import socket
import struct
import itertools
from threading import Thread
from queue import Queue
from collections import deque
from abc import ABC, abstractmethod


SEVER_PORT = 5001
LAUNCHER_PORT = 5000
class Dispatcher():
    def __init__(self, ret_q, run_q):
        self.ret_q = ret_q
        self.run_q = run_q
        self.wait_list = []
        self.done_list = []
        self.live_launcher = []
        self.dead_launcher = []
        self.stop= False
        self.init()
        self.start_rev()
        self.start_send()
    def start_rev(self):
        tcp_server = Thread(target=self.revice)
        tcp_server.start()
    def start_send(self):
        send_server = Thread(target=self.start)
        send_server.start()
    def revice(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', SEVER_PORT))
            s.listen(10)
        except socket.error as e:
            sys.exit(1)
        while True:
            conn, address = s.accept()
            buf = b''
            while len(buf) < 4:
                buf += conn.recv(4 - len(buf))
            length = struct.unpack('!I', buf)[0]
            data = b''
            while length > 0:
                d = conn.recv(length)
                length -= len(d)
                data += d

            unpickle_data = dict(pickle.loads(data))
            self.ret_q.put(unpickle_data)
            if unpickle_data.get('Status') != 1000:
                self.done_list.append([address[0], unpickle_data])
            conn.close()

    def init(self):
        if not os.path.exists('launcher.cfg'):
            raise RuntimeError('Can not find launcher.cfg')
        with open('launcher.cfg', 'r+') as fd:
            for line in fd:
                launcher_ip = line.strip()
                self.live_launcher.append({'ip':launcher_ip, 'jobs':[]})

    def close(self):
        self.release()
        for launcher in itertools.chain(self.live_launcher, self.dead_launcher):
            if launcher['jobs']:
                print('Still have jobs %s' % launcher)
        self.stop = True

    def pickup(self):
        if not self.live_launcher:
            return {}
        self.live_launcher = sorted(self.live_launcher, key=lambda x: len(x['jobs']), reverse=False)
        print('Live launcher %s, dead launcher %s' % (self.live_launcher, self.dead_launcher))
        return self.live_launcher[0]

    def release(self):
        for _ in range(len(self.done_list)):
            address, data = self.done_list.pop(0)
            for launcher in self.live_launcher:
                if address != launcher['ip']:
                    continue
                for job in launcher['jobs']:
                    if job['JobID'] == data['JobID']:
                        launcher['jobs'].remove(job)
                        print('Case %s on host %s for driver %s done on launcher %s' % (data['Case']['Case'], data['TestHost'], data['Driver'], launcher))
                        break
                else:
                    self.done_list.append([address, data])
                    break

    def dead(self, launcher):
        print('Dead %s, %s' % (launcher['ip'], launcher['jobs']))
        self.live_launcher.remove(launcher)
        self.dead_launcher.append(launcher)

    def fix_dead(self):
        # 1. check launcher is available now
        # 2. check running job on launcher
        # 3. put the rest job into wait_list
        req = {'type':'alive'}
        for _ in range(len(self.dead_launcher)):
            launcher = self.dead_launcher.pop(0)
            data = self.send(req, launcher['ip'], LAUNCHER_PORT)
            if data and 'result' in data and data['result'] == 'ok':
                self.live_launcher.append(launcher) 
                continue
            self.dead_launcher.append(launcher)

    def start(self):
        while True:
            if self.stop:
                print('Break dispatcher from while loop')
                break
            self.fix_dead()
            self.release()
            print('wait_list %s' % self.wait_list)
            if self.wait_list:
                self.dispatch()
                continue
            if not self.run_q.empty():
                self.wait_list.append(self.run_q.get())
                continue
            time.sleep(10)

    def dispatch(self):
        msg = self.wait_list.pop(0)
        print('Got task %s'  % msg)
        launcher = self.pickup() 
        print(launcher)
        if not launcher:
            print('No launcher selected, dead launcher %s' % self.dead_launcher)
            #self.fix_dead()
            return
        data = self.send(msg, launcher['ip'], LAUNCHER_PORT)
        if data and 'result' in data and data['result'] == 'ok':
            launcher['jobs'].append(msg)
            return
        print('Putback message %s' % msg)
        self.wait_list.append(msg)
        self.dead(launcher)
    def send(self, msg, launcher, port):
        data = {}
        pickle_msg = pickle.dumps(msg)
        length = struct.pack('!I', len(pickle_msg))
        pickle_msg = length + pickle_msg
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((launcher, port))
            s.sendall(pickle_msg)
            response = s.recv(1024)
            data = dict(pickle.loads(response))
        except socket.error as e:
            print ('Failed to create socket %s %s' % (e, launcher))
        finally:
            s.close()
            return data


if __name__ == '__main__':
        ret_q = Queue()
        run_q = Queue()
        dispatcher = Dispatcher(ret_q, run_q)
        msg1 = {'type':"task", 'JobID': time.time(), 'host_ip':'10.115.242.145', 'host_port':5001}
        msg2 = {'type':"task", 'JobID': time.time(), 'host_ip':'10.115.242.145', 'host_port':5001}
        for i in range(10000):
            msg = msg1 if i % 2 == 0 else msg2
            print('put into run_q %s' % msg)
            run_q.put(msg)
            while not ret_q.empty():
                print('get from ret_q %s' % ret_q.get())
            time.sleep(2)
         
