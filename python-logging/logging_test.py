import sys
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

#fh = logging.FileHandler('/tmp/test.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

ft = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(ft)

log.addHandler(ch)

log.info('info -- this is root')
log.debug('debug -- this is root')
log.error('error -- this is root')

log1 = logging.getLogger('LoggerTester')

log1.info('info -- this is LoggerTester')
log1.debug('debug -- this is LoggerTester')
log1.error('error -- this is LoggerTester')
