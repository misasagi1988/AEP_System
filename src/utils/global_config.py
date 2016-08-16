'''
Created on 2016-07-22

@author: Bella_Meng
'''
import os
import shutil
from ConfigParser import ConfigParser


class GlobalConfig(object):
    '''
    cfg parse class
    '''
    def __init__(self, cfg_path):
        '''
        init function
        :param cfg_path: cfg file path
        '''
        self.cfg = ConfigParser()
        self.cfg.read(cfg_path)
        self.root_dir = self.get_root_dir()

    def get_root_dir(self):
        '''
        get root_dir
        :return: root_dir string
        '''
        return self.cfg.get("project", "root_dir").strip()

    def get_ftpserver_dict(self):
        '''
        get ftp server info
        :return: server info dict
        '''
        host = self.cfg.get("ftp_server", "ftp_host").strip()
        user = self.cfg.get("ftp_server", "ftp_user").strip()
        pwd = self.cfg.get("ftp_server", "ftp_pwd").strip()
        sample_dir = self.cfg.get("ftp_server", "sample_dir").strip()
        return {"ftp_host": host, "ftp_user": user, "ftp_pwd":pwd, "sample_dir": sample_dir}

    def get_local_sample_zipdir(self):
        '''
        get downloaded sample store original dir
        :return: dir string
        '''
        local_dir = os.path.join(self.root_dir, self.cfg.get("sample_dir", "original_dir").strip())
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        return local_dir

    def get_local_sample_unzipdir(self):
        '''
        get unzip sample store dir
        :return: dir string
        '''
        local_dir = os.path.join(self.root_dir, self.cfg.get("sample_dir", "unzip_dir").strip())
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        return local_dir

    def get_local_sample_ultimate_dir(self):
        '''
        get sample ultimate store dir
        :return: dir string
        '''
        local_dir = os.path.join(self.root_dir, self.cfg.get("sample_dir", "ultimate_dir").strip())
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        return local_dir

    def get_local_sample_nodetection_dir(self):
        '''
        get no detection sample store dir, trend can detect, while sc cannot
        :return: dir string
        '''
        local_dir = os.path.join(self.root_dir, self.cfg.get("sample_dir", "nodetection_dir").strip())
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)
        os.mkdir(local_dir)
        return local_dir

    def get_remote_sample_dir(self):
        '''
        get remote sample store dir
        :return: dir string
        '''
        local_dir = self.cfg.get("sample_dir", "remote_dir").strip()
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        return local_dir

    def get_deploy_log_path(self):
        '''
        get deploy sample log dir
        :return: log path string
        '''
        return os.path.join(self.root_dir, self.cfg.get("log_dir", "deploy_log_path").strip())

    def get_result_log_path(self):
        '''
        get result check log dir
        :return: log path string
        '''
        return os.path.join(self.root_dir, self.cfg.get("log_dir", "result_log_path").strip())

    def get_nodetection_log_path(self):
        '''
        get no detection sample check log dir
        :return: log path string
        '''
        return os.path.join(self.root_dir, self.cfg.get("log_dir", "nodetection_log_path").strip())


    def get_7z_tool_dict(self):
        '''
        get unzip tool 7z dir
        :return: 7z tool dict
        '''
        return {"7z_path": os.path.join(self.root_dir, self.cfg.get("zip_tool", "7z_dir").strip()) + os.path.sep + "7z", "pwd": self.cfg.get("zip_tool", "7z_pwd").strip()}

    def get_mysql_info_dict(self):
        '''
        get mysql db server info
        :return: mysql db info dict
        '''
        info_dict = {}
        section = "db_mysql"
        info_dict["host"] = self.cfg.get(section, "host").strip()
        info_dict["port"] = int(self.cfg.get(section, "port").strip())
        info_dict["user"] = self.cfg.get(section, "user").strip()
        info_dict["pwd"] = self.cfg.get(section, "pwd").strip()
        info_dict["name"] = self.cfg.get(section, "name").strip()
        info_dict["charset"] = self.cfg.get(section, "charset").strip()
        info_dict["tbname"] = self.cfg.get(section, "tbname").strip()
        return info_dict

    def get_test_env_list(self):
        '''
        get test environment list
        :return: test environment list
        '''
        envlist = (self.cfg.get("test_info", "test_env").strip(",")).strip()
        return map(lambda x: x.strip(), envlist.split(","))

    def get_result_folder_dict(self, build_num):
        '''
        get result folder name dict
        :return: result folder dict, key is build number + test env
        '''
        result_folder = self.cfg.get("result_info", "result_path").strip()
        sample_set = self.cfg.get("sample_dir", "remote_dir").strip().split("\\")[-1]
        build_number = build_num
        test_env_list = self.get_test_env_list()
        result_folder_dict = {}
        for l in test_env_list:
            path_tmp = os.path.join(result_folder, build_number + l, sample_set)
            if l.rfind("xp") != -1:
                result_folder_dict[build_number + "_" + "xp"] = path_tmp
            elif l.rfind("x64") != -1:
                result_folder_dict[build_number + "_" + "win7X64"] = path_tmp
            else:
                result_folder_dict[build_number + "_" + "win7"] = path_tmp
        return result_folder_dict



if __name__ == "__main__":
    cfg = GlobalConfig(r"..\main\global.cfg")
    print cfg.get_result_folder_dict()

