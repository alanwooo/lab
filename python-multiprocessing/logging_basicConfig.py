import logging  

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='/tmp/test.log',  
                    filemode='w')  
  
logging.debug('this is debug message ')  
logging.info('this info message')  
logging.warning('this warning message')  
logging.error('this is error message')  
logging.critical('this is critical message')  
