from multiprocessing.connection import Listener, Client
import traceback
import time
from threading import Thread

LOCK, UNLOCK = True, False

class lockServer(Thread):
    def __init__(self, address=('127.0.0.1', 5000), authkey=b'ca$hc0w'):
        super().__init__()
        self.address = address
        self.authkey = authkey
        # {'name': timeout time}
        self.lock_dict = {}
    def response(self, conn, msg):
        if not isinstance(msg, tuple):
            conn.send(False)
            return
        result = False
        action, lock_name, lock_time = msg
        if action == LOCK:
            if lock_name in self.lock_dict:
                if self.lock_dict[lock_name]:
                    if int(time.time()) > self.lock_dict[lock_name]:
                        print('lock %s timeout.' % (lock_name))
                        self.lock_dict[lock_name] = int(time.time()) + lock_time if lock_time else lock_time
                        result = True
            else:
                self.lock_dict[lock_name] = int(time.time()) + lock_time if lock_time else lock_time
                result = True
        else:
            if lock_name in self.lock_dict:
                self.lock_dict.pop(lock_name)
            result = True
        conn.send(result)
    def startServer(self):
        print('Listen starting ...')
        serv = Listener(self.address, authkey=self.authkey)
        while True:
            try:
                conn = serv.accept()
                msg = conn.recv()
                if msg is None:
                    print('self.lock_dict')
                    print('revice None ...')
                    break
                print('\n\n')
                print(self.lock_dict)
                print('revice %s' % str(msg))
                self.response(conn, msg)
                print(self.lock_dict)
                print('\n\n')
                conn.close()
            except Exception:
                traceback.print_exc()
        serv.close()
    def run(self): 
        self.startServer()
    def stop(self):
        conn = Client(self.address, authkey=self.authkey)
        conn.send(None)

class mutexLock():
    def __init__(self, lock_type='host', timeout=0, address=('127.0.0.1', 5000), authkey=b'ca$hc0w'):
        self.lock_type = lock_type
        self.timeout = timeout
        self.address = address
        self.authkey = authkey
        self._locked = False
    def __enter__(self):
        if not self.lock():
            raise RuntimeError('Fail to lock')
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unlock()
    def _send(self, msg):
        conn = Client(self.address, authkey=self.authkey)
        conn.send(msg)
        result = conn.recv()
        conn.close()
        if result:
            self._locked = True
        return result
    def lock(self):
        msg = (LOCK, self.lock_type, self.timeout)
        return self._send(msg)
    def unlock(self):
        msg = (UNLOCK, self.lock_type, self.timeout)
        if self._locked:
            return self._send(msg)
        return True

if '__main__' == __name__:
    sevr = lockServer(('127.0.0.1', 5000))
    sevr.start()
    print('sleep 600 seconds')
    time.sleep(600)
    print('stop')
    sevr.stop()
