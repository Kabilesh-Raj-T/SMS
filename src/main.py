import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from src import sms_installer  # installer module
from src.database import Database
from src.product import ProductManager
from src.customer import CustomerManager
from src.employee import EmployeeManager
from src.fin_and_stats import FinanceManager, StatManager
from src.menu import Menu
from src.dynamic_price import Dynamic_Price

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
SSL_CA = os.getenv("SSL_CA")

# --------------------------
# Connect to database
# --------------------------
def connect_db():
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
        print("✅ Successfully connected to Azure MySQL!")
        return cnx
    except Error as e:
        print(f"❌ Connection failed: {e}")
        return None

# --------------------------
# Run installer only once
# --------------------------
cnx = connect_db()
if cnx:
    if not sms_installer.is_marked_installed() and not sms_installer.is_already_installed(cnx):
        print("🚀 Running installer for the first time...")
        import setup.SMS_Installer
        setup.SMS_Installer.run_installer(cnx)
    else:
        print("⚡ Installer already run. Skipping...")
    cnx.close()

# --------------------------
# Main application
# --------------------------
def main():
    """Main function to initialize and run the application."""
    db = Database()
    if not db.conn:
        print("Could not connect to the database. Exiting.")
        return

    dynamic_price = Dynamic_Price(db)
    customer_mgr = CustomerManager(db)
    product_mgr = ProductManager(db.conn, dynamic_price, customer_mgr)
    employee_mgr = EmployeeManager(db)
    finance_mgr = FinanceManager(db)
    stat_mgr = StatManager(db)

    menu = Menu(product_mgr, customer_mgr, employee_mgr, finance_mgr, stat_mgr, dynamic_price)

    try:
        menu.main_menu()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
