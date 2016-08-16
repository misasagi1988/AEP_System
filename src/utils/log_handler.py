'''
Created on 2016-07-25

@author: Bella_Meng
'''
import os
import logging
import logging.handlers

MAX_BYTES = 10 * 1024 * 1024  # 10MB


class Log_Handle(object):
    '''
    log module api
    '''

    def __init__(self, log_file):
        '''
        create logger object and control handle
        :param log_file: log file path
        '''
        self.logger = logging.getLogger(os.path.abspath(log_file))
        self.logger.setLevel(logging.DEBUG)

        # create debug file handle to write log
        self.fhandle = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=MAX_BYTES)
        self.fhandle.setLevel(logging.DEBUG)

        # create info stream handle for output
        self.shandle = logging.StreamHandler()
        self.shandle.setLevel(logging.INFO)

        # set formatter
        # f_formatter = logging.Formatter("[%(asctime)s] [%(filename)s(%(lineno)d)] [%(threadName)s] %(levelname)s %(message)s")
        s_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        self.fhandle.setFormatter(s_formatter)
        self.shandle.setFormatter(s_formatter)

    def debug(self, msg):
        '''
        only write log to file
        :param msg:  string msg
        :return: None
        '''
        self.logger.addHandler(self.fhandle)
        self.logger.addHandler(self.shandle)
        self.logger.debug(msg)
        self.logger.removeHandler(self.fhandle)
        self.logger.removeHandler(self.shandle)

    def info(self, msg):
        '''
        write log to file and print to screen
        :param msg: string msg
        :return: None
        '''
        self.logger.addHandler(self.fhandle)
        self.logger.addHandler(self.shandle)
        self.logger.info(msg)
        self.logger.removeHandler(self.fhandle)
        self.logger.removeHandler(self.shandle)

    def error(self, msg):
        '''
        print error message
        :param msg: sting msg
        :return: None
        '''
        self.logger.addHandler(self.fhandle)
        self.logger.addHandler(self.shandle)
        self.logger.error(msg)
        self.logger.removeHandler(self.fhandle)
        self.logger.removeHandler(self.shandle)

    def warning(self, msg):
        '''
        print warning message
        :param msg: string msg
        :return: None
        '''
        self.logger.addHandler(self.fhandle)
        self.logger.addHandler(self.shandle)
        self.logger.warning(msg)
        self.logger.removeHandler(self.fhandle)
        self.logger.removeHandler(self.shandle)


if __name__ == "__main__":
    logger = Log_Handle("test.log")
    logger.info("1 info")
    logger.debug("1 debug")
    logger.warning("1 warning")
    logger.debug("2 debug")