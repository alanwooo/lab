import fcntl
import time
import os
from subprocess import *

def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output
    except:
        return ''

cmd = 'while true; do echo "haha"; echo "hehe"; sleep 20; done'
process = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
while process.poll() is None:
    for line in non_block_read(process.stdout):
        print(line)
    print('sleep 7 seconds')
    time.sleep(7)
