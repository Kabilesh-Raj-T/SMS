import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()
mydb = None
try:
    mydb = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    mycursor = mydb.cursor()
    print("✅ Successfully connected to your Railway database!")
    print("Creating tables...")
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS product_database(
            ID VARCHAR(20) PRIMARY KEY,
            NAME VARCHAR(25),
            SELLING_PRICE DECIMAL(10,2),
            COST_PRICE DECIMAL(10,2),
            BRAND VARCHAR(20),
            QUANTITY INT,
            ITEMS_SOLD INT
        );
    """)
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_database(
            ID VARCHAR(20) PRIMARY KEY,
            NAME VARCHAR(25),
            CONTACT_NUMBER BIGINT,
            GENDER VARCHAR(15),
            EMAIL VARCHAR(40),
            PURCHASES MEDIUMTEXT
        );
    """)
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_database(
            ID VARCHAR(11) PRIMARY KEY,
            NAME VARCHAR(25),
            CONTACT_NUMBER BIGINT,
            GENDER VARCHAR(15),
            POSITION VARCHAR(50),
            SALARY DECIMAL(10,2)
        );
    """)
    print("Tables are ready.")
    print("Inserting product data...")
    a = ['1','2','3', '4', '5', '6', '7','8', '9', '10']
    b = ['LAYS_RED', 'LAYS_BLUE', 'MELODY', 'CHOCOBAR', 'MUNCH', 'LAYS_MAXX', 'OREO', 'COKE', 'ORBIT', 'POPCORN']
    c = [10, 10, 1, 40, 5, 20, 50, 70, 45, 85]
    g = [9.25,9.25,0.75,38.75,4.5,19.25,48,65.5,44,80.90]
    d = ['LAYS', 'LAYS', "ECLAIR'S", 'ARUN', 'MUNCH', 'LAYS', 'OREO', 'COKE', 'ORBIT', 'POP']
    e = [100, 100, 70, 25, 50, 40, 75, 20, 30, 25]
    f = [92, 80, 120, 67, 23, 40, 30, 80, 50, 34]
    sq = 'INSERT INTO product_database VALUES(%s, %s, %s, %s, %s, %s, %s)'
    for i in range(len(a)):
        mycursor.execute(sq, (a[i], b[i], c[i], g[i], d[i], e[i], f[i]))

    print("Inserting employee data...")
    aa = ['1', '2', '3','4','5','6']
    ba = ['a', 'b', 'c','d','e','f']
    ca = [9140526856, 9950637963, 9868466636,9823462461,9987567326,9486542466]
    da = ['M', 'M', 'M','F','F','M']
    ea = ['Worker','Part-Timer', 'Manager','Worker','Worker','Part-Timer']
    fa = [8372.97,6420.80,10358.36,8372.94,8372.94,6420.80]
    sqa = 'INSERT INTO employee_database VALUES(%s, %s, %s, %s, %s, %s)'
    for ia in range(len(aa)):
        mycursor.execute(sqa, (aa[ia], ba[ia], ca[ia], da[ia], ea[ia], fa[ia]))


    print("Inserting customer data...")
    ab = ['1', '2', '3','4','5','6']
    bb = ['a', 'b', 'c','d','e','f']
    cb = [9141226856, 9956637963, 9818466636,9833462461,9987669326,9486542466]
    dib = ['M', 'M', 'M','F','F','M']
    eb = ['a@a.com', 'b@b.com', 'c@c.com', 'd@d.com', 'e@e.com', 'f@f.com']
    fb = ['11 Perk 10 1 10|2 LAYS_BLUE 10 2 20|30', '6 LAYS_MAXX 20 6 120|120', '5 MUNCH 5 1 5|5', '8 COKE 70 2 140|140', '1 LAYS_RED 10 1 10|10', '2 LAYS_BLUE 10 2 20|20']
    sqb = 'INSERT INTO customer_database VALUES(%s, %s, %s, %s, %s, %s)'
    for ib in range(len(ab)):
        mycursor.execute(sqb, (ab[ib], bb[ib], cb[ib], dib[ib], eb[ib], fb[ib]))


    mydb.commit()
    print("✅ All data has been inserted and saved successfully!")

except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
finally:
    if mydb and mydb.is_connected():
        mycursor.close()
        mydb.close()
        print("MySQL connection is closed.")