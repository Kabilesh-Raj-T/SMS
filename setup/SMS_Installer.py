import os
import mysql.connector
from dotenv import load_dotenv
from datetime import date

# --- Load Environment Variables ---
script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
env_path = os.path.join(parent_dir, '.env')
print(f"Attempting to load .env file from: {env_path}")
if not os.path.exists(env_path):
    print(f"❌ ERROR: The .env file was NOT found at the path above.")
else:
    print("✅ .env file found.")
load_dotenv(dotenv_path=env_path)

db_port_str = os.getenv("MYSQLPORT")
if not db_port_str:
    raise ValueError("MYSQLPORT environment variable is not set.")

try:
    with mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        port=int(db_port_str),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    ) as mydb:
        mydb.autocommit = False
        print("✅ Successfully connected to the database!")

        with mydb.cursor(buffered=True) as cur:
            print("Dropping old tables if they exist...")
            cur.execute("DROP TABLE IF EXISTS sales_history;")
            cur.execute("DROP TABLE IF EXISTS employee_database;")
            cur.execute("DROP TABLE IF EXISTS customer_database;")
            cur.execute("DROP TABLE IF EXISTS product_database;")
            mydb.commit()

            print("Creating tables fresh...")
            cur.execute("""
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

            cur.execute("""
                CREATE TABLE customer_database(
                    ID INT NOT NULL PRIMARY KEY,
                    NAME VARCHAR(25),
                    CONTACT_NUMBER BIGINT,
                    GENDER VARCHAR(15),
                    PURCHASES DECIMAL(10,2)
                );
            """)

            cur.execute("""
                CREATE TABLE employee_database(
                    ID INT NOT NULL PRIMARY KEY,
                    NAME VARCHAR(25),
                    CONTACT_NUMBER BIGINT,
                    GENDER VARCHAR(15),
                    POSITION VARCHAR(50),
                    SALARY DECIMAL(10,2)
                );
            """)

            # ✅ sales_history without PK / FK
            cur.execute("""
                CREATE TABLE sales_history(
                    product_id INT,
                    quantity INT,
                    sale_date DATE
                );
            """)
            print("✅ Tables created.")

            # --- Insert product data ---
            print("Inserting product data...")
            a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            b = ['LAYS_RED', 'LAYS_BLUE', 'MELODY', 'CHOCOBAR', 'MUNCH', 'LAYS_MAXX', 'OREO', 'COKE', 'ORBIT', 'POPCORN']
            c = [10, 10, 1, 40, 5, 20, 50, 70, 45, 85]
            g = [9.25, 9.25, 0.75, 38.75, 4.5, 19.25, 48, 65.5, 44, 80.90]
            d = ['LAYS', 'LAYS', "ECLAIR'S", 'ARUN', 'MUNCH', 'LAYS', 'OREO', 'COKE', 'ORBIT', 'POP']
            e = [100, 100, 70, 25, 50, 40, 75, 20, 30, 25]
            f = [92, 80, 120, 67, 23, 40, 30, 80, 50, 34]
            expiry_dates = [date(2025, 12, 31)] * len(a)

            sq = ('INSERT INTO product_database '
                  '(ID, NAME, MRP, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE) '
                  'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)')
            cur.executemany(sq, list(zip(a, b, c, g, g, d, e, f, expiry_dates)))
            mydb.commit()
            print("✅ product_database inserted.")

            # --- Insert employee data ---
            print("Inserting employee data...")
            aa = [1, 2, 3, 4, 5, 6]
            ba = ['a', 'b', 'c','d','e','f']
            ca = [9140526856, 9950637963, 9868466636, 9823462461, 9987567326, 9486542466]
            da = ['M', 'M', 'M','F','F','M']
            ea = ['Worker','Part-Timer', 'Manager','Worker','Worker','Part-Timer']
            fa = [8372.97, 6420.80, 10358.36, 8372.94, 8372.94, 6420.80]

            sqa = ('INSERT INTO employee_database '
                   '(ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY) '
                   'VALUES (%s,%s,%s,%s,%s,%s)')
            cur.executemany(sqa, list(zip(aa, ba, ca, da, ea, fa)))
            mydb.commit()
            print("✅ employee_database inserted.")

            # --- Insert customer data ---
            print("Inserting customer data...")
            ab = [1, 2, 3, 4, 5, 6]
            bb = ['a', 'b', 'c','d','e','f']
            cb = [9141226856, 9956637963, 9818466636, 9833462461, 9987669326, 9486542466]
            db_ = ['M', 'F', 'M', 'F', 'M', 'F']
            fb = [110.00, 1200.00, 50.00, 140.00, 100.00, 290.00]

            sqb = ('INSERT INTO customer_database '
                   '(ID, NAME, CONTACT_NUMBER, GENDER, PURCHASES) '
                   'VALUES (%s,%s,%s,%s,%s)')
            cur.executemany(sqb, list(zip(ab, bb, cb, db_, fb)))
            mydb.commit()
            print("✅ customer_database inserted.")

            # --- Insert sales history data ---
            print("Inserting sales history data...")
            sales_product_ids = [1, 2, 3, 1, 5, 8, 10, 3, 7, 2]
            sales_quantities  = [2, 1, 5, 3, 1, 4, 2, 1, 6, 2]
            sales_dates = [
                date(2025, 8, 15), date(2025, 8, 16), date(2025, 9, 1), date(2025, 9, 10),
                date(2025,10, 5),  date(2025,10,10),  date(2025,11, 1), date(2025,11, 2),
                date(2025,11,15),  date(2025,12, 1)
            ]

            sqs = 'INSERT INTO sales_history (product_id, quantity, sale_date) VALUES (%s,%s,%s)'
            cur.executemany(sqs, list(zip(sales_product_ids, sales_quantities, sales_dates)))
            mydb.commit()
            print("✅ sales_history inserted.")

            # Check row counts
            cur.execute("SELECT COUNT(*) FROM sales_history")
            print("sales_history rows:", cur.fetchone()[0])

            print("🎉 All data inserted successfully!")

except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
