# -*- coding: UTF-8 -*-
import datetime
import cx_Oracle

# 用于清理历史数据库脚本，采用cx_oracle库进行操作


class Ops:
    def __init__(self):
        self.oracle = 'user/passwd@ip:1521/orcl'

    def Create(self, sql):
        conn = cx_Oracle.connect(self.oracle)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            cursor.close()
            conn.close()

        except Exception as e:
            logger("Create failed:" + str(e))

    def DelteOldTable(self, sql):
        conn = cx_Oracle.connect(self.oracle)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            cursor.close()
            conn.close()

        except Exception as e:
            logger("DelteOldTable failed:" + str(e))

    def SelectTest(self, sql):
        conn = cx_Oracle.connect(self.oracle)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            row = cursor.fetchall()
            cursor.close()
            conn.close()
            return row

        except Exception as e:
            logger("SelectTest failed:" + str(e))

    def run(self):
        # 起始时间
        nowTime = datetime.datetime.strptime('2012-06-01', '%Y-%m-%d')
        # 递增间隔时间 1天
        delta = datetime.timedelta(days=1)
        # 目标时间
        dstTime = datetime.datetime.strptime('2018-06-03', '%Y-%m-%d')
        changTime = nowTime

        while True:
            tableName = "tablename" + str(changTime.strftime('%Y%m%d'))
            logger("正在处理表：" + tableName)

            # 计算原表中行数
            sqlCountOld = """SELECT count(vin) FROM {tableName}""".format(tableName=tableName)
            rowOld = self.SelectTest(sqlCountOld)  # 操作

            # 筛选数据，建立一个没有重复数据的临时表
            sqlCreateTable = """CREATE TABLE tablename_coursor AS(SELECT * FROM {tableName} WHERE ID IN (SELECT MAX(rvt.ziduanming) FROM {tableName} rvt GROUP BY rvt.ziduanming))""".format(
                tableName=tableName)
            logger("第一步：建立临时表tablename_coursor...\n" + "SQL语句：" + sqlCreateTable)
            self.Create(sqlCreateTable)  # 操作
            logger("建立临时表tablename_coursor成功！")

            # 删除原来重复数据的表，truncate 然后再drop
            sqlTruncate = """truncate table {tableName}""".format(tableName=tableName)
            sqlDrop = """drop table {tableName}""".format(tableName=tableName)
            logger("第二步：删除原表" + tableName + "...\n" + "SQL语句：" + sqlTruncate + "\t\t\t\t" + "SQL语句：" + sqlDrop)
            self.DelteOldTable(sqlTruncate)  # 操作
            self.DelteOldTable(sqlDrop)  # 操作
            logger("删除原表" + tableName + "成功！")

            # 数据还原并且删除临时表
            sqlCreateTable = """create table {tableName} as select * from tablename_coursor""".format(
                tableName=tableName)
            sqlDeleteCoursr = """DROP TABLE tablename_coursor"""

            logger("第三步：从临时表恢复数据到:" + tableName + "\nSQL语句:" + sqlCreateTable)
            self.Create(sqlCreateTable)  # 操作
            logger("从临时表恢复数据成功!!!")

            logger("第四步：删除临时表tablename_coursor" + "\nSQL语句:" + sqlDeleteCoursr)
            self.DelteOldTable(sqlDeleteCoursr)  # 操作
            logger("删除临时表tablename_coursor 成功!")

            # 给vin创建索引
            sqlIndex = """create index IND_{time}_VIN on {tableName}(VIN)""".format(
                time=str(changTime.strftime('%Y%m%d')),
                tableName=tableName)
            logger("第五步：创建索引中..." + "\nSQL语句:" + sqlIndex)
            self.Create(sqlIndex)  # 操作
            logger("创建索引完成！")

            # 最后校验临时表是否有数据
            sqlFinal = """SELECT count(vin) FROM {tableName}""".format(tableName=tableName)
            row = self.SelectTest(sqlFinal)  # 操作
            logger("数据清理前，表中行数:" + str(rowOld[0][0]))
            logger("数据清理后，表中行数:" + str(row[0][0]))

            # 计算天数，用于计数，否则不能退出循环。
            changTime = changTime + delta
            if changTime > dstTime:
                break


def logger(log_info):
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %X')
    print(time_stamp + ' ' + log_info)


if __name__ == '__main__':
    t = Ops()
    t.run()