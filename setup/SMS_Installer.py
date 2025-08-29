import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from datetime import date

# --------------------------
# Load environment variables
# --------------------------
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT", "3306"))
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
SSL_CA = os.getenv("SSL_CA")   # ✅ FIXED (was missing!)

try:
    cnx = mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DATABASE,
        ssl_ca=SSL_CA,
        ssl_disabled=False
    )

    cnx.autocommit = False
    cursor = cnx.cursor(buffered=True)
    print("✅ Successfully connected to Azure MySQL!")

    # --------------------------
    # Drop old tables if exist
    # --------------------------
    print("Dropping old tables if they exist...")
    for table in ["sales_history", "employee_database", "customer_database", "product_database"]:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
    cnx.commit()

    # --------------------------
    # Create tables
    # --------------------------
    print("Creating tables fresh...")

    cursor.execute("""
        CREATE TABLE product_database(
            ID INT NOT NULL PRIMARY KEY,
            NAME VARCHAR(25),
            MRP DECIMAL(10,2),
            SELLING_PRICE DECIMAL(10,2),
            COST_PRICE DECIMAL(10,2),
            BRAND VARCHAR(20),
            QUANTITY INT,
            ITEMS_SOLD INT,
            EXPIRY_DATE DATE
        );
    """)

    cursor.execute("""
        CREATE TABLE customer_database(
            ID INT NOT NULL PRIMARY KEY,
            NAME VARCHAR(25),
            CONTACT_NUMBER BIGINT,
            GENDER VARCHAR(15),
            PURCHASES DECIMAL(10,2)
        );
    """)

    cursor.execute("""
        CREATE TABLE employee_database(
            ID INT NOT NULL PRIMARY KEY,
            NAME VARCHAR(25),
            CONTACT_NUMBER BIGINT,
            GENDER VARCHAR(15),
            POSITION VARCHAR(50),
            SALARY DECIMAL(10,2)
        );
    """)

    cursor.execute("""
        CREATE TABLE sales_history(
            product_id INT,
            quantity INT,
            sale_date DATE
        );
    """)
    cnx.commit()
    print("✅ Tables created.")

    # --------------------------
    # Insert sample data
    # --------------------------
    print("Inserting product data...")
    products = [
        (1, 'LAYS_RED', 10, 9.25, 9.25, 'LAYS', 100, 92, date(2025,12,31)),
        (2, 'LAYS_BLUE', 10, 9.25, 9.25, 'LAYS', 100, 80, date(2025,12,31)),
        (3, 'MELODY', 1, 0.75, 0.75, "ECLAIR'S", 70, 120, date(2025,12,31)),
        (4, 'CHOCOBAR', 40, 38.75, 38.75, 'ARUN', 25, 67, date(2025,12,31)),
        (5, 'MUNCH', 5, 4.5, 4.5, 'MUNCH', 50, 23, date(2025,12,31)),
        (6, 'LAYS_MAXX', 20, 19.25, 19.25, 'LAYS', 40, 40, date(2025,12,31)),
        (7, 'OREO', 50, 48, 48, 'OREO', 75, 30, date(2025,12,31)),
        (8, 'COKE', 70, 65.5, 65.5, 'COKE', 20, 80, date(2025,12,31)),
        (9, 'ORBIT', 45, 44, 44, 'ORBIT', 30, 50, date(2025,12,31)),
        (10,'POPCORN', 85, 80.9, 80.9, 'POP', 25, 34, date(2025,12,31))
    ]
    cursor.executemany(
        'INSERT INTO product_database (ID, NAME, MRP, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);',
        products
    )
    cnx.commit()
    print("✅ product_database inserted.")

    # Employee data
    employees = [
        (1,'a',9140526856,'M','Worker',8372.97),
        (2,'b',9950637963,'M','Part-Timer',6420.80),
        (3,'c',9868466636,'M','Manager',10358.36),
        (4,'d',9823462461,'F','Worker',8372.94),
        (5,'e',9987567326,'F','Worker',8372.94),
        (6,'f',9486542466,'M','Part-Timer',6420.80)
    ]
    cursor.executemany(
        'INSERT INTO employee_database (ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY) VALUES (%s,%s,%s,%s,%s,%s);',
        employees
    )
    cnx.commit()
    print("✅ employee_database inserted.")

    # Customer data
    customers = [
        (1,'a',9141226856,'M',110.00),
        (2,'b',9956637963,'F',1200.00),
        (3,'c',9818466636,'M',50.00),
        (4,'d',9833462461,'F',140.00),
        (5,'e',9987669326,'M',100.00),
        (6,'f',9486542466,'F',290.00)
    ]
    cursor.executemany(
        'INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, GENDER, PURCHASES) VALUES (%s,%s,%s,%s,%s);',
        customers
    )
    cnx.commit()
    print("✅ customer_database inserted.")

    # Sales history
    sales = [
        (1,2,date(2025,8,15)),
        (2,1,date(2025,8,16)),
        (3,5,date(2025,9,1)),
        (1,3,date(2025,9,10)),
        (5,1,date(2025,10,5)),
        (8,4,date(2025,10,10)),
        (10,2,date(2025,11,1)),
        (3,1,date(2025,11,2)),
        (7,6,date(2025,11,15)),
        (2,2,date(2025,12,1))
    ]
    cursor.executemany(
        'INSERT INTO sales_history (product_id, quantity, sale_date) VALUES (%s,%s,%s);',
        sales
    )
    cnx.commit()
    print("✅ sales_history inserted.")

    # Check row counts
    cursor.execute("SELECT COUNT(*) FROM sales_history")
    print("sales_history rows:", cursor.fetchone()[0])

    print("🎉 All data inserted successfully!")

except Error as e:
    print(f"❌ Connection failed: {e}")

finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'cnx' in locals() and cnx.is_connected():
        cnx.close()
        print("Connection closed.")
