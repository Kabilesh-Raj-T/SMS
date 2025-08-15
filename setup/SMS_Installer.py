import mysql.connector
y = input('Enter Username of your Mysql Server : ')
x = input('Enter Password of your Mysql server : ')
mydb = mysql.connector.connect(host="localhost",user=y,passwd=x)
mycursor=mydb.cursor()
mycursor.execute('CREATE DATABASE IF NOT EXISTS sms_database;')
mycursor.execute('use sms_database')
mycursor.execute('create table if not exists product_database(ID varchar(20) primary key,NAME varchar(25),SELLING_PRICE decimal(10,2),COST_PRICE decimal(10,2),BRAND varchar(20),QUANTITY int(11),ITEMS_SOLD int(11));')
mycursor.execute('create table if not exists customer_database(ID varchar(20) primary key,NAME varchar(25),CONTACT_NUMBER bigint,GENDER varchar(15),EMAIL varchar(40),PURCHASES mediumtext);')
mycursor.execute('create table if not exists employee_database(ID varchar(11) primary key,NAME varchar(25),CONTACT_NUMBER bigint,GENDER varchar(15),POSITION varchar(50),SALARY decimal(10,2));')

a = ['1','2','3', '4', '5', '6', '7','8', '9', '10',]
b = ['LAYS_RED', 'LAYS_BLUE', 'MELODY', 'CHOCOBAR', 'MUNCH', 'LAYS_MAXX', 'OREO', 'COKE', 'ORBIT', 'POPCORN']
c = [10, 10, 1, 40, 5, 20, 50, 70, 45, 85]
g = [9.25,9.25,0.75,38.75,4.5,19.25,48,65.5,44,80.90]
d = ['LAYS', 'LAYS', "ECLAIR'S", 'ARUN', 'MUNCH', 'LAYS', 'OREO', 'COKE', 'ORBIT', 'POP']
e = [100, 100, 70, 25, 50, 40, 75, 20, 30, 25]
f = [92, 80, 120, 67, 23, 40, 30, 80, 50, 34]
sq = 'insert into product_database values(%s, %s, %s, %s, %s, %s, %s)'
for i in range(len(a)):
    mycursor.execute(sq, (a[i], b[i], c[i], g[i], d[i], e[i], f[i]))
mydb.commit()
    
aa = ['1', '2', '3','4','5','6']
ba = ['a', 'b', 'c','d','e','f']
ca = [9140526856, 9950637963, 9868466636,9823462461,9987567326,9486542466]
da = ['M', 'M', 'M','F','F','M']
ea = ['Worker','Part-Timer', 'Manager','Worker','Worker','Part-Timer']
fa = [8372.97,6420.80,10358.36,8372.94,8372.94,6420.80]

sqa = 'insert into employee_database values(%s, %s, %s, %s, %s, %s)'
for ia in range(len(aa)):
    mycursor.execute(sqa, (aa[ia], ba[ia], ca[ia], da[ia], ea[ia], fa[ia]))
mydb.commit()

ab = ['1', '2', '3','4','5','6']
bb = ['a', 'b', 'c','d','e','f']
cb = [9141226856, 9956637963, 9818466636,9833462461,9987669326,9486542466]
dib = ['M', 'M', 'M','F','F','M']
eb = ['a@a.com', 'b@b.com', 'c@c.com', 'd@d.com', 'e@e.com', 'f@f.com']
fb = ['11 Perk 10 1 10|2 LAYS_BLUE 10 2 20|30', '6 LAYS_MAXX 20 6 120|120', '5 MUNCH 5 1 5|5', '8 COKE 70 2 140|140', '1 LAYS_RED 10 1 10|10', '2 LAYS_BLUE 10 2 20|20']
sqa = 'insert into customer_database values(%s, %s, %s, %s, %s, %s)'
for ib in range(len(ab)):
    mycursor.execute(sqa, (ab[ib], bb[ib], cb[ib], dib[ib], eb[ib], fb[ib]))
mydb.commit()
