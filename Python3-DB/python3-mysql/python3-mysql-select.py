import datetime
import xlwt
import pymysql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def sql():
    table = '数据库的表'    # 我这里就是简单的查一张表
    # 打开数据库连接
    db = pymysql.connect("服务器ip", "数据库用户", "数据库密码", "数据库名")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute()  方法执行 SQL 查询
    cursor.execute("SELECT * FROM {table};".format(table=table))
    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchall()
    # 关闭数据库连接
    db.close()
    return data, table


def writ_to_excel(data, database):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet(database, cell_overwrite_ok=True)
    # i为索引，j为内容
    for i, j in enumerate(data):
        # m为j里面内容的索引，n为j里单独的每个内容
        for m, n in enumerate(j):
            sheet.write(i, m, n)
    url = r'C:\Users\cj\Desktop\{}.xls'.format(database)
    book.save(url)
    return url


def send_eamil(url, table):
    # 第三方 SMTP 服务
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "123456789@qq.com"  # 用户名
    mail_pass = "45678jkjlsfds"  # 口令
    # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    receivers = ['dfadsafdsaf@qq.com']

    content = MIMEText(table)  # 邮件内容
    message = MIMEMultipart()
    message.attach(content)
    # message['From'] = Header("MySql查询结果-附件", 'utf-8')
    # message['To'] = Header(receivers, 'utf-8')
    subject = "MySql查询结果-附件-" + table + str(datetime.datetime.now())
    message['Subject'] = Header(subject, 'utf-8')
    xlsx = MIMEApplication(open(url, 'rb').read())
    xlsx["Content-Type"] = 'application/octet-stream'
    xlsx.add_header('Content-Disposition', 'attachment', filename=url.split('\\')[-1])
    message.attach(xlsx)
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        # smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(mail_user, receivers, message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    data, table = sql()
    url = writ_to_excel(data, table)
    send_eamil(url, table)