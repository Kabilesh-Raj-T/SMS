from pathlib import Path
import os
from datetime import date

INSTALL_MARKER = Path(os.getenv("INSTALL_MARKER", "/app/data/.installed"))

def is_marked_installed():
    """Check if installation marker file exists."""
    return INSTALL_MARKER.exists()

def mark_installed():
    """Create the installation marker file."""
    INSTALL_MARKER.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_MARKER.touch()

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
    cursor = cnx.cursor()
    print("🚀 Running fresh installation...")

    # Create tables
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

    # Insert sample data
    products = [
        (1, 'LAYS_RED', 10, 9.25, 9.25, 'LAYS', 100, 92, date(2025, 12, 31)),
        (2, 'LAYS_BLUE', 10, 9.25, 9.25, 'LAYS', 100, 80, date(2025, 12, 31)),
        (3, 'MELODY', 1, 0.75, 0.75, "ECLAIR'S", 70, 120, date(2025, 12, 31))
    ]
    cursor.executemany(
        'INSERT INTO product_database (ID, NAME, MRP, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);',
        products
    )

    employees = [
        (1, 'a', 9140526856, 'M', 'Worker', 8372.97),
        (2, 'b', 9950637963, 'M', 'Part-Timer', 6420.80),
        (3, 'c', 9868466636, 'M', 'Manager', 10358.36)
    ]
    cursor.executemany(
        'INSERT INTO employee_database (ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY) VALUES (%s,%s,%s,%s,%s,%s);',
        employees
    )

    customers = [
        (1, 'a', 9141226856, 'M', 110.00),
        (2, 'b', 9956637963, 'F', 1200.00)
    ]
    cursor.executemany(
        'INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, GENDER, PURCHASES) VALUES (%s,%s,%s,%s,%s);',
        customers
    )

    sales = [
        (1, 2, date(2025, 8, 15)),
        (2, 1, date(2025, 8, 16))
    ]
    cursor.executemany(
        'INSERT INTO sales_history (product_id, quantity, sale_date) VALUES (%s,%s,%s);',
        sales
    )

    cnx.commit()
    print("🎉 Sample data inserted successfully!")

    # Mark installation as complete
    mark_installed()
