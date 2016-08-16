'''
Created on 2016-07-26

@author: Bella_Meng
'''
import subprocess
import sys
import os
import shutil
import hashlib
import re
from log_handler import Log_Handle
from mysql_handler import MYSQL_Handle
import pefile
import peutils

# machine type
IMAGE_FILE_MACHINE_I386  = 0x014c

class Util_Proc(object):
    '''
    utility functions
    '''
    def __init__(self, logger, mysql_dict):
        '''
        init function
        :param logger: logger handle
        :param mysql_dict: mysql db info dict
        '''
        self.logger = logger
        self.tbname = mysql_dict["tbname"]
        self.mysql_handler = MYSQL_Handle(mysql_dict, logger)

    def unzip_file(self, zip_tool, src_file, dst_dir, keep_struct = True):
        '''
        use 7z to unzip file function
        :param zip_tool: 7z tool info dict
        :param src_file: src zip file
        :param dst_dir: dst unzipped dir
        :param keep_struct: default True
        :return: None
        '''
        #print "unzip file, ", src_file
        zip_toolname = zip_tool["7z_path"]
        zip_pwd = zip_tool["pwd"]
        if keep_struct:
            cmd = r'%s x "%s" -r -y -o"%s" -p%s >nul' %(zip_toolname, src_file, dst_dir, zip_pwd)
        else:
            cmd = r'%s e "%s" -r -y -o"%s" -p%s >nul' %(zip_toolname, src_file, dst_dir, zip_pwd)
        #self.logger.debug(cmd)
        subprocess.call(cmd, shell=True)

    def cal_hash(self, filename):
        '''
        call file hash value function
        :param filename: filename(full path)
        :return: hash value in string format
        '''
        fp = open(filename, "rb")
        fdata = fp.read()
        fp.close()
        sha1 = hashlib.sha1()
        sha1.update(fdata)
        return sha1.hexdigest()

    def isWin64PeFile(self, pe):
        '''
        call file hash value function
        :pe: filename(full path)
        :return: True if is win64PE, None if not PE
        '''
        peImage = None
        try:
            peImage = pefile.PE(pe, fast_load=True)
            return peImage.FILE_HEADER.Machine != IMAGE_FILE_MACHINE_I386
        except Exception, e:
            self.logger.debug("%s is not a PE file" %pe)
            return None
        finally:
            if peImage:
                peImage.close()

    def filter_proc(self, src_dir, dst_dir, txt_file):
        '''
        process sample, unique, filter exists in db
        :param src_dir: unzipped sample dir
        :param dst_dir: ultimate sample dir
        :param txt_file: txt file downloaded from ftp, exists in original sample folder
        :return: None
        '''
        sample_dict = {}
        if os.path.exists(txt_file):
            with open(txt_file, "r") as pf:
                for line in pf.readlines():
                    if not line.strip():
                        break
                    try:
                        res = re.split(r"\t", line.strip())
                        sample_dict[res[0].strip().lower()] = res[1].strip()
                    except:
                        continue

        for root, dirs, files in os.walk(src_dir):
            for filename in files:
                hash_value = self.cal_hash(os.path.join(root, filename))
                if filename.lower() != hash_value:
                    self.logger.debug("%s hash not match, hash value %s" % (filename, hash_value))
                    continue
                #update db info if key in txt and db, else insert into db
                if self.mysql_handler.hasExisted(self.tbname, "sample_id", hash_value):
                    self.logger.debug("file exists in db, %s" %hash_value)
                    if hash_value in sample_dict.keys():
                        row = {"trend_rule": sample_dict[hash_value]}
                        where_condition = "sample_id=" + "'" + hash_value + "'"
                        self.mysql_handler.update(self.tbname, row, where = where_condition)
                else:
                    trend_rule = sample_dict[hash_value] if hash_value in sample_dict.keys() else "null"
                    #check pe type
                    pe_type_res = self.isWin64PeFile(os.path.join(root, filename))
                    pe_type = "null"
                    if pe_type_res is None:
                        pe_type = "null"
                    elif pe_type_res == True:
                        pe_type = "win64"
                    else:
                        pe_type = "win32"
                    rows = {"sample_id": hash_value, "pe_type": pe_type, "trend_rule": trend_rule}
                    self.mysql_handler.insert(self.tbname, rows)
                    shutil.move(os.path.join(root, filename), os.path.join(dst_dir, hash_value))
            self.mysql_handler.commit()
        shutil.rmtree(src_dir)

    def get_db_fields(self):
        '''
        get field list for self db
        :return: field list
        '''
        return self.mysql_handler.getFields(self.tbname)

    def add_db_fields(self, field_name, type = "VARCHAR(10)"):
        '''
        add field for self db
        :param field_name: add field name
        :param type: field type
        :return: None
        '''
        self.mysql_handler.addField(self.tbname, field_name, type)
        self.mysql_handler.commit()

    def check_result_proc(self, field_name, result_folder):
        '''
        check result and update db
        :param field_name: field to be updated in db
        :param result_folder: result folder path
        :return: None
        '''
        result_folder = os.path.join(result_folder, "All")
        for subfolder in os.listdir(result_folder):
            sample_id = subfolder.split(".")[0]
            txt_file = os.path.join(result_folder, subfolder, sample_id + ".report.txt")
            if not os.path.exists(txt_file):
                self.logger.debug("%s result file not exists, continue" %sample_id)
                continue
            result = "null"
            with open(txt_file, "r") as pf:
                contents = pf.read()
                reg = re.compile("Result:\s*(\d+)")
                match_res = reg.search(contents)
                if match_res:
                    result = match_res.group(1)
            if self.mysql_handler.hasExisted(self.tbname, "sample_id", sample_id):
                self.logger.debug("file exists in db, %s, result is: %s" %(sample_id, result))
                row = {"`" + field_name + "`": result}
                where_condition = "sample_id=" + "'" + sample_id + "'"
                self.mysql_handler.update(self.tbname, row, where=where_condition)
            else:
                self.logger.debug("file not exists in db, continue, %s" % sample_id)
        self.mysql_handler.commit()

    def get_nodetection_sample(self, condition):
        '''
        get sc no detection sample
        :param condition: condition to query in db
        :return: no detection sample list
        '''
        field = "sample_id"
        condition = "trend_rule <> 'null' and " + condition
        exec_res = self.mysql_handler.getDifferRes(self.tbname, field, condition)
        ret_res = []
        for i in exec_res:
            ret_res.append(i[field])
        return ret_res

