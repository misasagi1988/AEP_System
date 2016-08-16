'''
Created on 2016-08-12

@author: Bella_Meng
'''
import os
import sys
from utils.global_config import GlobalConfig
from utils.log_handler import Log_Handle
from utils.util_proc import Util_Proc

class Get_NoDetection_Sample_Proc(object):
    '''
    get sample that trend can detect, while sc cannot
    '''
    def __init__(self, condition, config_path):
        '''
        init function
        :param condition: condition to query in db
        :param config_path: cfg path
        '''
        self.cfg = GlobalConfig(config_path)
        log_path = self.cfg.get_nodetection_log_path()
        if os.path.exists(log_path):
            os.remove(log_path)
        self.logger = Log_Handle(log_path)
        self.logger.info("start get sc no detection sample process.")
        self.condition = condition.strip()
        self.util_proc = Util_Proc(self.logger, self.cfg.get_mysql_info_dict())
        self.differ_sample_dir = self.cfg.get_local_sample_nodetection_dir()
        self.remote_sample_dir = self.cfg.get_remote_sample_dir()

    def get_nodetection_sample(self):
        '''
        copy sc no detection sample to local
        :return: None
        '''
        sample_list = self.util_proc.get_nodetection_sample(self.condition)
        for f in sample_list:
            src_f = os.path.join(self.remote_sample_dir, f)
            dst_f = os.path.join(self.differ_sample_dir, f)
            open(dst_f, "wb").write(open(src_f, "rb").read())
            self.logger.debug("get no detection sample: %s" % f)
        self.logger.info("get sc no detection sample process end.")

def main(condition):
    '''
    main process
    :param build_number: condition to query in db
    :return: None
    '''
    nodetection_handle_proc = Get_NoDetection_Sample_Proc(condition, r"global.cfg")
    nodetection_handle_proc.get_nodetection_sample()


if __name__ == "__main__":
    main(sys.argv[1])
