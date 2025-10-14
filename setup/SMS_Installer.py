from pathlib import Path
import os
from datetime import date
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# === Load Environment ===
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Configuration
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 3306))
USER = os.getenv("USER", "root")
PASSWORD = os.getenv("PASSWORD", "")
DATABASE = os.getenv("DATABASE", "inventory_db")
SSL_CA = os.getenv("SSL_CA")

# === Installation Marker ===
INSTALL_MARKER = Path(os.getenv("INSTALL_MARKER", "/app/data/.installed"))


def is_marked_installed():
    """Check if installation marker file exists."""
    return INSTALL_MARKER.exists()


def mark_installed():
    """Create the installation marker file."""
    INSTALL_MARKER.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_MARKER.touch()


# === Database Installation ===
def is_already_installed(cnx):
    """Check if database tables already exist."""
    try:
        cursor = cnx.cursor()
        cursor.execute("SHOW TABLES LIKE 'product_database';")
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists
    except Exception as e:
        print("Error checking installation:", e)
        return False


def run_installer(cnx):
    """Run first-time setup: create tables and insert initial data."""
    marker_exists = is_marked_installed()
    tables_exist = is_already_installed(cnx)

    if tables_exist:
        if not marker_exists:
            print("⚠️ Database tables already exist — skipping install.")
            mark_installed()
        else:
            print("✅ Already marked as installed.")
        return

    if marker_exists:
        print("⚠️ Installation marker exists but tables are missing — re-running install.")

    cursor = cnx.cursor()

    # Ensure database exists and is selected
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE}`;")
        cursor.execute(f"USE `{DATABASE}`;")
    except Exception as e:
        print(f"Warning: Could not create/select database '{DATABASE}' from current connection:", e)
        try:
            tmp = mysql.connector.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                port=PORT,
                ssl_ca=SSL_CA if SSL_CA else None,
                ssl_disabled=(SSL_CA is None)
            )
            tcur = tmp.cursor()
            tcur.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE}`;")
            tmp.commit()
            tcur.close()
            tmp.close()
            cursor.execute(f"USE `{DATABASE}`;")
        except Exception as e2:
            print("❌ Failed to ensure database exists:", e2)

    print("🚀 Running fresh installation...")

    try:
        # === Create Tables (idempotent) ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_database(
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
            CREATE TABLE IF NOT EXISTS customer_database(
                ID INT NOT NULL PRIMARY KEY,
                NAME VARCHAR(25),
                CONTACT_NUMBER BIGINT,
                GENDER VARCHAR(15),
                PURCHASES DECIMAL(10,2)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_database(
                ID INT NOT NULL PRIMARY KEY,
                NAME VARCHAR(25),
                CONTACT_NUMBER BIGINT,
                GENDER VARCHAR(15),
                POSITION VARCHAR(50),
                SALARY DECIMAL(10,2)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_history(
                product_id INT,
                quantity INT,
                sale_date DATE
            );
        """)

        cnx.commit()
        print("✅ Tables created (if not existing).")

        # === Insert Sample Data ===
        cursor.executemany("""
            INSERT IGNORE INTO product_database
            (ID, NAME, MRP, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """, [
            (1, 'LAYS_RED', 10, 9.25, 9.25, 'LAYS', 100, 92, date(2025, 12, 31)),
            (2, 'LAYS_BLUE', 10, 9.25, 9.25, 'LAYS', 100, 80, date(2025, 12, 31)),
            (3, 'MELODY', 1, 0.75, 0.75, "ECLAIR'S", 70, 120, date(2025, 12, 31))
        ])

        cursor.executemany("""
            INSERT IGNORE INTO employee_database
            (ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY)
            VALUES (%s,%s,%s,%s,%s,%s);
        """, [
            (1, 'a', 9140526856, 'M', 'Worker', 8372.97),
            (2, 'b', 9950637963, 'M', 'Part-Timer', 6420.80),
            (3, 'c', 9868466636, 'M', 'Manager', 10358.36)
        ])

        cursor.executemany("""
            INSERT IGNORE INTO customer_database
            (ID, NAME, CONTACT_NUMBER, GENDER, PURCHASES)
            VALUES (%s,%s,%s,%s,%s);
        """, [
            (1, 'a', 9141226856, 'M', 110.00),
            (2, 'b', 9956637963, 'F', 1200.00)
        ])

        cursor.executemany("""
            INSERT IGNORE INTO sales_history
            (product_id, quantity, sale_date)
            VALUES (%s,%s,%s);
        """, [
            (1, 2, date(2025, 8, 15)),
            (2, 1, date(2025, 8, 16))
        ])

        cnx.commit()
        print("🎉 Sample data inserted successfully!")

        # === Add Recommended Indexes ===
        add_indexes(cursor)
        cnx.commit()

        # === Optionally make ID auto-increment ===
        safely_add_auto_increment(cursor, cnx)

        # === Optionally enforce unique customer contact ===
        safely_add_unique_customer_contact(cursor, cnx)

        # === Done ===
        mark_installed()
        print("✅ Installation completed and marked as installed.")

    except Exception as e:
        cnx.rollback()
        print("❌ Installation failed:", e)
    finally:
        cursor.close()


# === Index Creation ===
def add_indexes(cursor):
    """Add performance indexes (safe incremental approach)."""
    print("📊 Adding recommended indexes...")

    index_commands = [
        ("idx_sales_sale_date_product",
         "CREATE INDEX idx_sales_sale_date_product ON sales_history (sale_date, product_id);"),
        ("idx_product_items_sold",
         "CREATE INDEX idx_product_items_sold ON product_database (ITEMS_SOLD);"),
        ("idx_customer_purchases",
         "CREATE INDEX idx_customer_purchases ON customer_database (PURCHASES);"),
        ("idx_product_expiry_date",
         "CREATE INDEX idx_product_expiry_date ON product_database (EXPIRY_DATE);"),
        ("idx_customer_contact",
         "CREATE INDEX idx_customer_contact ON customer_database (CONTACT_NUMBER);")
    ]

    for name, query in index_commands:
        table = query.split(" ON ")[1].split(" ")[0]
        cursor.execute(f"SHOW INDEX FROM {table} WHERE Key_name='{name}';")
        if not cursor.fetchall():
            cursor.execute(query)
            print(f"✅ Index created: {name}")
        else:
            print(f"ℹ️ Index already exists: {name}")


# === Optional: Add AUTO_INCREMENT safely ===
def safely_add_auto_increment(cursor, cnx):
    """Convert ID columns to AUTO_INCREMENT if safe."""
    print("⚙️ Ensuring AUTO_INCREMENT IDs...")

    try:
        cursor.execute("ALTER TABLE product_database MODIFY COLUMN ID INT NOT NULL AUTO_INCREMENT;")
        cursor.execute("ALTER TABLE customer_database MODIFY COLUMN ID INT NOT NULL AUTO_INCREMENT;")
        cursor.execute("ALTER TABLE employee_database MODIFY COLUMN ID INT NOT NULL AUTO_INCREMENT;")
        cnx.commit()
        print("✅ AUTO_INCREMENT added to ID columns.")
    except Exception as e:
        print("⚠️ Skipping AUTO_INCREMENT:", e)


# === Optional: Enforce unique customer contacts ===
def safely_add_unique_customer_contact(cursor, cnx):
    """Add unique index to customer contact numbers (after duplicate check)."""
    print("🔍 Checking for duplicate customer contact numbers...")
    cursor.execute("""
        SELECT CONTACT_NUMBER, COUNT(*) c 
        FROM customer_database 
        GROUP BY CONTACT_NUMBER HAVING c > 1;
    """)
    duplicates = cursor.fetchall()

    if duplicates:
        print("⚠️ Duplicate contact numbers found — skipping UNIQUE constraint.")
        for num, count in duplicates:
            print(f"   CONTACT_NUMBER {num} appears {count} times")
        return

    try:
        cursor.execute("ALTER TABLE customer_database ADD UNIQUE INDEX uq_customer_contact (CONTACT_NUMBER);")
        cnx.commit()
        print("✅ Unique constraint added on CONTACT_NUMBER.")
    except Exception as e:
        print("⚠️ Skipping UNIQUE constraint:", e)
