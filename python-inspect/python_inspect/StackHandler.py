import logging, logging.handlers, logging.config
import sys
import os
import time
import json
import inspect

log = logging.getLogger('StackHandler')

# Create a handler
class StackHandler(logging.Handler):
    PRINT_STACK = False
    # since the handler of the logging module is thread safe, we do not need to
    # add a lock here to lock the I/O output to stack.log for multi-threading
    #
    # recursive to get the inner variables, only recursive 2 times,
    # since some variables are reference each others.
    STACKDEEP = 2
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.stackdeep = 0

    def emit(self, record):
        """
        override emit method in logging.Handler
        """
        def _saveStacktoFile(msg):
            """
            write message to file
            """
            with open(self.filename, 'a+') as fd:
                fd.write(msg)

        def _skipVars(k, v):
            """
            skip variables which we do not want
            """
            if k in bypassVars:
                return True
            if inspect.isclass(v) or inspect.ismodule(v) or inspect.isfunction(v):
                return True
            return False

        def _extendDict(v, num):
            """
            extend the output of dictionary
            """
            try:
                if isinstance(v, dict):
                    return json.dumps(v, indent=4).replace('\n', '\n%s' % ('\t'*num))
            except:
                pass
            return str(v)

        def _getInnerVars(k, v):
            """
            get the inner variables
            """
            msg = ''
            self.stackdeep += 1
            if isinstance(v, classList):
                first_line = 1
                msg += '{0}{1}:\t{2}\n{0}  \-----'.format('\t'*(self.stackdeep - first_line), str(k),
                       _extendDict(v, self.stackdeep - first_line + 1))
                for s_k, s_v in vars(v).items():
                    if _skipVars(s_k, s_v):
                        continue
                    if self.stackdeep < StackHandler.STACKDEEP and isinstance(s_v, classList):
                        msg += _getInnerVars(s_k, s_v)
                    else:
                        msg += '{0}{1}:\t{2}\n'.format('\t'*(0 if first_line else self.stackdeep - first_line),
                               str(s_k), _extendDict(s_v, self.stackdeep - first_line + 1))
                    first_line = 0
                self.stackdeep -= 1
            return msg

        def _getVars(f_vars):
            """
            get the variables
            """
            msg = ''
            for k, v in f_vars.items():
                if _skipVars(k, v):
                    continue
                msg_inner = _getInnerVars(k, v)
                self.stackdeep = 0
                if not msg_inner:
                    msg += "%s:\t%s\n" % (str(k), _extendDict(v, 1))
                    continue
                msg += msg_inner
            return msg

        if StackHandler.PRINT_STACK:
            # import the modules as local variables
            from lib.CheckHandler import CheckHandler
            classList = (CheckHandler)
            bypassVars = ['__doc__', '__loader__', '__cached__', '__builtins__', '__spec__', 'xmlConfig',
                          'json_testgroups', 'test_group', 'summaryFields', 'hwPCI']
            # ignore all the exceptions
            try:
                msg = "{0}\n{1}Full ERROR Stack\n{0}\n\n\n".format("#"*120, " "*45)
                msg += "{0}\n{1}ERROR Msg\n{0}\n".format("*"*120, " "*50)
                msg += "%s-%s-%s-%s : %s\n\n\n" % (record.asctime, record.levelname, record.name,
                                      record.funcName, record.message)
                _saveStacktoFile(msg)
                i = 1
                callstack = []
                for frame, filename, line_num, func, source_code, source_index in inspect.stack():
                    if 'StackHandler.py' in filename or 'logging/__init__.py' in filename:
                        continue
                    msg = "{0}\n{1} The stack of {2}() in {3} \n{0}\n".format("*"*120, " "*30, func,
                          os.path.basename(filename))
                    msg += "FILENAME:%s\nLINENO:%s\nFUNCTION:%s\n" % (filename, line_num, func)
                    msg += "{0}\n{1}Global Variables in {2}\n{0}\n".format("-"*120, " "*30,
                           "%s(%s)" % (func, os.path.basename(filename)))
                    # get global variables
                    msg += _getVars(frame.f_globals)
                    msg += "{0}\n{1}Local Variables in {2}\n{0}\n".format("-"*120, " "*30,
                           "%s(%s)" % (func, os.path.basename(filename)))
                    # get local variables
                    msg += _getVars(frame.f_locals)
                    msg += '\n\n\n'
                    _saveStacktoFile(msg)
                    callstack.append('%s(%s):%s' % (func, os.path.basename(filename), str(line_num)))
                    i += 1
                msg = "{0}\n{1} Function Call Stack \n{0}\n".format("*"*120, " "*50)
                msg += ' -> '.join(callstack[::-1])
                msg += '\n\n\n'
                _saveStacktoFile(msg)
            except Exception as e:
                # ignore all the exccption in above block
                # we do not want break the main process at any time.
                log.debug(e, exc_info=True)
                pass

