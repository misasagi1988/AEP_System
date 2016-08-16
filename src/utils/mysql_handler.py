'''
Created on 2016-07-26

@author: Bella_Meng
'''
import sys
import MySQLdb
import MySQLdb.cursors
from log_handler import Log_Handle


class MYSQL_Handle(object):
    '''
    mysql module api
    '''
    def __init__(self, sql_dict, logger):
        '''
        init function
        :param sql_dict: sql dict
        :param logger: logger handle
        '''
        db_host = sql_dict["host"]
        db_port = sql_dict["port"]
        db_name = sql_dict["name"]
        db_user = sql_dict["user"]
        db_pwd = sql_dict["pwd"]
        db_charset = sql_dict["charset"]
        self.logger = logger

        try:
            self.conn = MySQLdb.connect(host = db_host, user = db_user, passwd = db_pwd, db = db_name, port = db_port, cursorclass = MySQLdb.cursors.DictCursor)
            self.conn.set_character_set(db_charset)
            self.cur = self.conn.cursor()
        except MySQLdb.Error, e:
            self.logger.error("mysql db connection error, %s" %e)
            sys.exit()

    def execute(self, sql):
        '''
        execute non query sql(add, update, delete)
        :param sql: sql statement
        :return: execute number
        '''
        try:
            ret = self.cur.execute(sql)
            return ret
        except MySQLdb.Error, e:
            self.logger.error("mysql execute error: %s\nsql: %s" % (e.args[1], sql))
            sys.exit(1)

    def commit(self):
        '''
        commit data to database
        when add, update or delete data, execute commit to update database
        :return: None
        '''
        try:
            self.conn.commit()
        except MySQLdb.Error, e:
            self.logger.error("mysql commit error: %s\n" % e.args[1])
            sys.exit(1)

    def hasPrimaryKey(self, table):
        '''
        check if table has primary key
        :param table: table name
        :return: True if has primary key, else False
        '''
        has_key = False
        sql = "select count(*) as num from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='%s' and COLUMN_KEY='PRI'" % (
        table)

        num = int(self.queryRow(sql)['num'])
        if num > 0:
            has_key = True

        return has_key

    def insert(self, table, data_dict):
        '''
        insert data to table based on data_dict
        choose different insert methods for table which has primary-key and non-key
        :param table: table name
        :param data_dict: insert data dict
        :return: execute code
        '''
        # replace illegal char
        for key in data_dict:
            if "\\" in data_dict[key]:
                data_dict[key] = data_dict[key].replace("\\", "\\\\")
            if "'" in data_dict[key]:
                data_dict[key] = data_dict[key].replace("'", r"\'")

        if self.hasPrimaryKey(table):
            num = self.insertWithPrimaryKey(table, data_dict)
        else:
            num = self.insertWithNonKey(table, data_dict)

        return num

    def insertWithPrimaryKey(self, table, data_dict):
        '''
        insert data to table which has primary key
        :param table: table name
        :param data_dict: insert data dict
        :return: execute code
        '''
        key_list = []
        value_list = []
        for (key, value) in data_dict.items():
            key_list.append(key)
            if isinstance(value, int) or isinstance(value, float):
                value = str(value)
            else:
                value = "'%s'" % value
            value_list.append(value)

        keys = ",".join(key_list)
        values = ",".join(value_list)
        # prevent repeatedly insert
        sql = "insert ignore into %s(%s) values(%s)" % (table, keys, values)
        # print sql
        num = self.execute(sql)
        return num

    def insertWithNonKey(self, table, data_dict):
        '''
         insert data to table which has no primary key
        check if table has exist record before insert
        :param table: table name
        :param data_dict: insert data dict
        :return: execute code
        '''
        key_list = []
        value_list = []
        where_list = []
        for (key, value) in data_dict.items():
            key_list.append(key)
            if isinstance(value, int) or isinstance(value, float):
                value = str(value)
            else:
                value = "'%s'" % value
            value_list.append(value)
            where_list.append("%s=%s" % (key, value))

        keys = ",".join(key_list)
        values = ",".join(value_list)
        wheres = " and ".join(where_list)
        # prevent repeatedly insert
        sql = "insert into %s(%s) select %s from dual where not exists (select * from %s where %s)" % (
        table, keys, values, table, wheres)
        # print sql
        num = self.execute(sql)
        return num

    def update(self, table, data_dict, where):
        '''
        update table with data_dict, and condition is where
        :param table: table name
        :param data_dict: update data dict
        :param where: condition
        :return: execute code
        '''
        # replace illegal char
        for key in data_dict:
            if "\\" in data_dict[key]:
                data_dict[key] = data_dict[key].replace("\\", "\\\\")
            if "'" in data_dict[key]:
                data_dict[key] = data_dict[key].replace("'", r"\'")

        set_list = []
        for (key, value) in data_dict.items():
            if isinstance(value, int) or isinstance(value, float):
                value = str(value)
            else:
                value = "'%s'" % value
            set_list.append("%s=%s" % (key, value))

        set_values = ",".join(set_list)

        sql = "update %s set %s where %s" % (table, set_values, where)
        # print sql
        num = self.execute(sql)
        # print "update data row number:", num
        return num

    def delete(self, table, where=""):
        '''
        delete rows in table based on where condition, if where is "", clear table
        :param table: table name
        :param where: condition
        :return: execute code
        '''
        if where:
            sql = "delete from %s where %s" % (table, where)
        else:
            sql = "delete from %s" % table
        num = self.execute(sql)
        # print "delete data row number:", num
        return num

    def query(self, sql):
        '''
        execute query sql
        :param sql: sql statement
        :return: cursor
        '''
        try:
            self.cur.execute(sql)
            return self.cur
        except MySQLdb.Error, e:
            self.logger.error("mysql query error: %s\nsql: %s\n" % (e.args[1], sql))
            sys.exit(1)

    def queryAll(self, sql):
        '''
        execute query sql
        :param sql: sql statement
        :return: all data dict, format: ({field1:value1},{field1:value1})
        '''
        result = self.query(sql).fetchall()
        return result

    def queryRow(self, sql):
        '''
        execute query
        :param sql: sql statement
        :return: first row of results
        '''
        result = self.query(sql).fetchone()
        return result

    def hasExisted(self, tb_name, key_name, value):
        '''
        check if the value has existed in db
        :param tb_name: table name
        :param key_name: table primary key
        :param value: file hash value
        :return: True if existed, else False
        '''
        has_existed = False
        sql = "select count(*) as num from %s where %s='%s'" % (tb_name, key_name, value)
        row = self.queryRow(sql)
        if row["num"] > 0:
            has_existed = True
        return has_existed

    def getFields(self, tb_name):
        '''
        get field list for table tb_name
        :param tb_name: table name
        :return: field list
        '''
        sql = "SELECT * FROM %s" % tb_name
        self.execute(sql)
        desc = self.cur.description
        fields = []
        for i in desc:
            fields.append(i[0])
        return fields

    def addField(self, tb_name, field, type):
        '''
        add field for table tb_name
        :param tb_name: table name
        :param field: field name to add
        :param type: field type
        :return: execute code
        '''
        sql = "alter table %s add `%s` %s" %(tb_name, field, type)
        num = self.execute(sql)
        return num

    def getDifferRes(self, tb_name, field, condition):
        '''
        query db to get list
        :param tb_name: table name
        :param field: field name
        :param condition: condition to query
        :return: query list
        '''
        sql = "select %s from %s where %s" % (field, tb_name, condition)
        exec_res = self.queryAll(sql)
        return exec_res

    def close(self):
        '''
        close cursor and connection
        :return: None
        '''
        try:
            self.cur.close()
            self.conn.close()
        except Exception, e:
            pass

    def __del__(self):
        '''
        close everything
        :return: None
        '''
        self.close()

if __name__ == "__main__":
    info_dict = {}
    info_dict["host"] = "127.0.0.1"
    info_dict["port"] = 3306
    info_dict["user"] = "root"
    info_dict["pwd"] = r"mac8.6"
    info_dict["name"] = "test_a"
    info_dict["charset"] = "utf8"
    mysql = MYSQL_Handle(info_dict, Log_Handle(r"test.log"))
    x = r"http://fastfileget.info/file/Heaven\'s+Lost+Property+(1080p)+-+HD+[Season+1]/?"
    rows = {'zip_sha1': 'okada', 'zip_path': x}
    mysql.insert("zip_info", rows)
    mysql.commit()

