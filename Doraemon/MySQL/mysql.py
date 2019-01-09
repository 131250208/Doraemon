import MySQLdb
import logging


class MySQL(object):    
    def __init__(self, host, username, passwd, database):
        self.db = MySQLdb.connect(host, username, passwd, database, charset='utf8')
        
    def insert(self, table, object_dict):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        vals_hold = ["%s" for _ in range(len(object_dict))]
        vals_hold_str = ", ".join(vals_hold)
        vals = tuple(object_dict.values())

        # SQL 插入语句
        sql = '''INSERT INTO {}({}) \
             VALUES ({})'''.format(table, ", ".join(object_dict.keys()), vals_hold_str)
        try:
            # 执行sql语句
            cursor.execute(sql, vals)
            # 提交到数据库执行
            self.db.commit()
        except Exception as e:
            logging.warning(e)
            # 发生错误时回滚
            self.db.rollback()
            return False
        return True

    def insert_many(self, table, object_dict_list):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()
        if len(object_dict_list) == 0:
            return False
    
        keys_str = ", ".join(object_dict_list[0].keys())
        vals_hold = ["%s" for _ in range(len(object_dict_list[0]))]
        vals_hold_str = ", ".join(vals_hold)
        row_list = [tuple(object_dict.values()) for object_dict in object_dict_list]
    
        # SQL 插入语句
        sql = """INSERT INTO {} ({})
            VALUES ({})""".format(table, keys_str, vals_hold_str)
    
        try:
            # 执行sql语句
            cursor.executemany(sql, row_list)
            # 提交到数据库执行
            self.db.commit()
        except Exception as e:
            logging.warning(e)
            # 发生错误时回滚
            self.db.rollback()
            return False
        return True

    def close_db(self):
        self.db.close()


if __name__ == "__main__":
   pass
