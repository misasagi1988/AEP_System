'''
Created on 2016-07-25

@author: Bella_Meng
'''
import ftplib
import time
import os, sys
from log_handler import Log_Handle


class FTP_Handle(object):
    '''
    ftp module api
    '''
    def __init__(self, logger):
        '''
        init function
        :param logger: logger handle
        '''
        self.logger = logger
        self.logger.debug("start FTP handle.")

    def create_connection(self, host, user, pwd):
        '''
        create ftp connection
        :param host: ftp server host
        :param user: connect user
        :param pwd: connect password
        :return: ftp handle
        '''
        ftp = ftplib.FTP()
        max_num = 6
        b_connect = False
        for i in range(max_num):
            try:
                ftp.connect(host, port = 21, timeout = 60)
                b_connect = True
                break
            except ftplib.all_errors, e:
                self.logger.error("ftp connect error, %s" %e)
        if not b_connect:
            self.logger.error("connect ftp server failed, exit.")
            return None
        try:
            ftp.login(user, pwd)
        except ftplib.all_errors, e:
            self.logger.error("ftp login error, %s" %e)
            ftp.close()
            return None
        self.logger.debug("start FTP handle success.")
        return ftp

    def list_directory(self, ftp, dir_path):
        '''
        list ftp server directory file list
        :param ftp: ftp handle
        :param dir_path: ftp server directory
        :return: file list
        '''
        cur_list = []
        try:
            ftp.cwd(dir_path)
            cur_list = ftp.nlst()
        except Exception, e:
            self.logger.error("list ftp directory exception, %s" %e)
            return None
        return cur_list

    def is_samesize(self, ftp, remote_file, local_file):
        '''
        check if two files are the same
        :param ftp: ftp handle
        :param remote_file: remote file path
        :param local_file: local file path
        :return: True if size is the same, else False
        '''
        is_same = False
        try:
            rf_size = ftp.size(remote_file)
        except:
            rf_size = -1
        try:
            lf_size = os.path.getsize(local_file)
        except:
            lf_size = -1
        if rf_size == lf_size:
            is_same = True
        return is_same

    def download_file(self, ftp, sample_name, src_dir, dst_dir):
        '''
        download file from src to dst
        :param ftp: ftp handle
        :param sample_name: download file name
        :param src_dir: src dir
        :param dst_dir: dst dir
        :return: None
        '''
        fp = os.path.join(dst_dir, sample_name)
        try:
            ftp.cwd(src_dir)
            if self.is_samesize(ftp, sample_name, fp):
                self.logger.debug("file has existed, return")
                return False
            f = open(fp, "wb")
            ftp.retrbinary(r"RETR %s" %sample_name, f.write)
            f.close()
            return True
        except Exception, e:
            self.logger.error("download file exception, %s" %e)
            sys.exit()

    def delete_file(self, ftp, file_name, src_dir):
        '''
        delete file in ftp server
        :param ftp: ftp handle
        :param file_name:  file to be deleted
        :param src_dir: src dir
        :return: None
        '''
        try:
            ftp.cwd(src_dir)
            ftp.delete(file_name)
            return True
        except Exception, e:
            self.logger.error("delete file exception, %s" %e)
            sys.exit()


if __name__ == "__main__":
    ftp_dict = {}
    ftp_dict["ftp_host"] = r"10.5.36.116"
    ftp_dict["ftp_user"] = "ftp"
    ftp_dict["ftp_pwd"] = "ftp"
    ftp_dict["sample_dir"] = r"/sandcastle/bella/sample/"
    ftp_handle = FTP_Handle(Log_Handle(r"test.log"))
    ftp_server = ftp_handle.create_connection(ftp_dict["ftp_host"], ftp_dict["ftp_user"], ftp_dict["ftp_pwd"])
    if not ftp_server:
        ftp_handle.logger.error("create ftp handle error, exit.")
        sys.exit()
    file_list = ftp_handle.list_directory(ftp_server, ftp_dict["sample_dir"])
    print file_list