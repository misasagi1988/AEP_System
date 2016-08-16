'''
Created on 2016-08-11

@author: Bella_Meng
'''
import os
import sys
from utils.global_config import GlobalConfig
from utils.log_handler import Log_Handle
from utils.util_proc import Util_Proc

class Check_Result_Proc(object):
    '''
    check sample test result process class
    '''
    def __init__(self, build_number, config_path):
        '''
        init function
        :param build_number: check result for build
        :param config_path: cfg path
        '''
        self.cfg = GlobalConfig(config_path)
        log_path = self.cfg.get_result_log_path()
        if os.path.exists(log_path):
            os.remove(log_path)
        self.logger = Log_Handle(log_path)
        self.logger.info("start check asp sample result handle process.")
        self.build_number = build_number.strip()
        self.env_list = self.cfg.get_test_env_list()
        self.result_dict = self.cfg.get_result_folder_dict(self.build_number)
        self.util_proc = Util_Proc(self.logger, self.cfg.get_mysql_info_dict())
        self.logger.info("test build number: %s" %self.build_number)
        self.logger.info("test environment list: %s" %(self.env_list))

    def check_result(self):
        '''
        check sample test result for specific build
        :return: None
        '''
        db_fields = self.util_proc.get_db_fields()
        for key, res_folder in self.result_dict.items():
            self.logger.info("start check result folder: %s" %res_folder)
            if not os.path.exists(res_folder):
                self.logger.info("%s result folder not exists, continue." %res_folder)
                continue
            if key not in db_fields:
                self.util_proc.add_db_fields(key)
                self.logger.info("field %s not exists, add field." %key)
            self.util_proc.check_result_proc(key, res_folder)
        self.logger.info("check result process end.")


def main(build_number):
    '''
    main process
    :param build_number: check result for build
    :return:
    '''
    check_handle_proc = Check_Result_Proc(build_number, r"global.cfg")
    check_handle_proc.check_result()


if __name__ == "__main__":
    main(sys.argv[1])