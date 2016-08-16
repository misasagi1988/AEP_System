'''
Created on 2016-07-22

@author: Bella_Meng
'''

import sys
import os
import re
import shutil
from utils.global_config import GlobalConfig
from utils.log_handler import Log_Handle
from utils.ftp_handler import FTP_Handle
from utils.util_proc import Util_Proc


class Deploy_Sample_Proc(object):
    '''
    deploy sample process class
    '''
    def __init__(self, config_path):
        '''
        init function
        :param config_path: cfg pat
        '''
        self.cfg = GlobalConfig(config_path)
        self.sample_original_dir = self.cfg.get_local_sample_zipdir()
        self.sample_unzip_dir = self.cfg.get_local_sample_unzipdir()
        self.sample_ultimate_dir = self.cfg.get_local_sample_ultimate_dir()
        self.sample_remote_dir = self.cfg.get_remote_sample_dir()
        log_path = self.cfg.get_deploy_log_path()
        if os.path.exists(log_path):
            os.remove(log_path)
        self.logger = Log_Handle(log_path)
        self.logger.info("start ASP sample handle process.")
        self.ftp_dict = self.cfg.get_ftpserver_dict()
        self.ftp_handle = FTP_Handle(self.logger)
        self.util_proc = Util_Proc(self.logger, self.cfg.get_mysql_info_dict())
        self.file_set = set()

    def download_sample_local(self):
        '''
        connect to ftp server, download sample to local
        :return: None
        '''
        ftp_server = self.ftp_handle.create_connection(self.ftp_dict["ftp_host"], self.ftp_dict["ftp_user"], self.ftp_dict["ftp_pwd"])
        if not ftp_server:
            self.logger.error("create ftp handle error, exit.")
            sys.exit()
        self.logger.info("download ftp server sample to local.")
        file_list = self.ftp_handle.list_directory(ftp_server, self.ftp_dict["sample_dir"])
        if file_list is None:
            self.logger.error("list ftp sample directory error, exit.")
            sys.exit()
        for file_name in file_list:
            if not (file_name.endswith(r".txt") or file_name.endswith(r".zip")):
                continue
            if file_name.rfind(r"_CBAQ") != -1:
                continue
            if os.path.exists(os.path.join(self.sample_original_dir, os.path.splitext(file_name)[0] + r".flag")):
                self.logger.debug("%s file flag exists, do not download this file." %file_name)
                continue
            self.logger.debug("download file:  %s"  %file_name)
            #check if file has been downloaded to local, if not, download it and append it to self.file_set
            if self.ftp_handle.download_file(ftp_server, file_name, self.ftp_dict["sample_dir"], self.sample_original_dir):
                self.file_set.add(os.path.splitext(file_name)[0])
                if file_name.endswith(r".zip"):
                    f = open(os.path.join(self.sample_original_dir, os.path.splitext(file_name)[0] + r".flag"), "w")
                    f.close()
            self.ftp_handle.delete_file(ftp_server, file_name, self.ftp_dict["sample_dir"])
        self.logger.info("download sample set: %s" %str(self.file_set))

    def unzip_sample(self):
        '''
        unzip sample in sample original dir to unzip dir
        :return: None
        '''
        self.logger.info("unzip downloaded sample.")
        for file_name in self.file_set:
            file_name += r".zip"
            if not os.path.exists(os.path.join(self.sample_original_dir, file_name)):
                continue
            self.logger.debug("unzip file, %s" %file_name)
            self.util_proc.unzip_file(self.cfg.get_7z_tool_dict(), os.path.join(self.sample_original_dir, file_name), os.path.join(self.sample_unzip_dir, os.path.splitext(file_name)[0]))
        self.logger.info("unzip downloaded sample end.")

    def process_sample(self):
        '''
        process unzipped folder, filter samples existed in db and sha1 unmatched
        :return: None
        '''
        self.logger.info("process unzipped sample files.")
        for sample_dir in os.listdir(self.sample_unzip_dir):
            self.logger.debug("process sample set: %s" %sample_dir)
            self.util_proc.filter_proc(os.path.join(self.sample_unzip_dir, sample_dir), self.sample_ultimate_dir, os.path.join(self.sample_original_dir, sample_dir + r".txt"))
        self.logger.info("process unzipped sample files end.")

    def upload_sample(self):
        '''
        upload sample in ultimate folder to remote sample folder, delete local sample 
        :return: None
        '''
        self.logger.info("upload sample to 218 share folder.")
        for f in os.listdir(self.sample_ultimate_dir):
            src_f = os.path.join(self.sample_ultimate_dir, f)
            dst_f = os.path.join(self.sample_remote_dir, f)
            if not os.path.exists(dst_f) or (os.path.exists(dst_f) and (os.path.getsize(dst_f) != os.path.getsize(src_f))):
                open(dst_f, "wb").write(open(src_f, "rb").read())
                self.logger.debug("upload sample: %s" %src_f)
        shutil.rmtree(self.sample_ultimate_dir)
        self.logger.info("upload sample to 218 share folder end.")


def main():
    '''
    main process
    :return: None
    '''
    deploy_handle_proc = Deploy_Sample_Proc(r"global.cfg")
    deploy_handle_proc.download_sample_local()
    if len(deploy_handle_proc.file_set) <= 0:
        deploy_handle_proc.logger.info("No file downloaded, exit")
        sys.exit()
    deploy_handle_proc.unzip_sample()
    deploy_handle_proc.process_sample()
    deploy_handle_proc.upload_sample()


if __name__ == "__main__":
    main()