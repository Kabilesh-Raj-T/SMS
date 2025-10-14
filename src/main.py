import os
from pathlib import Path
import sys
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# -----------------------------------------------------
# Fix imports for setup module
# -----------------------------------------------------
# Add parent directory (/app) to sys.path so 'setup' is importable
sys.path.append(str(Path(__file__).resolve().parent.parent))

# -----------------------------------------------------
# Imports
# -----------------------------------------------------
from setup import sms_Installer
from src.database import Database
from src.product import ProductManager
from src.customer import CustomerManager
from src.employee import EmployeeManager
from src.fin_and_stats import FinanceManager, StatManager
from src.menu import Menu
from src.dynamic_price import Dynamic_Price

# -----------------------------------------------------
# Load environment variables
# -----------------------------------------------------
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT", "3306"))
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
SSL_CA = os.getenv("SSL_CA")  # Must be /app/DigiCertGlobalRootCA.crt.pem in Docker

# -----------------------------------------------------
# Connect to database
# -----------------------------------------------------
def connect_db():
    """Establish a connection to the MySQL database."""
    try:
        cnx = mysql.connector.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE,
            ssl_ca=SSL_CA if SSL_CA else None,
            ssl_disabled=(SSL_CA is None)
        )
        cnx.autocommit = False
        print("✅ Successfully connected to MySQL!")
        return cnx
    except Error as e:
        # If the database does not exist (ER_BAD_DB_ERROR / 1049), try to create it
        try:
            if getattr(e, 'errno', None) == 1049 or 'Unknown database' in str(e):
                print(f"Database '{DATABASE}' not found. Attempting to create it...")
                # Connect without specifying database
                tmp = mysql.connector.connect(
                    user=USER,
                    password=PASSWORD,
                    host=HOST,
                    port=PORT,
                    ssl_ca=SSL_CA if SSL_CA else None,
                    ssl_disabled=(SSL_CA is None)
                )
                cur = tmp.cursor()
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE}`;")
                tmp.commit()
                cur.close()
                tmp.close()
                # Try connecting again, now that database should exist
                cnx = mysql.connector.connect(
                    user=USER,
                    password=PASSWORD,
                    host=HOST,
                    port=PORT,
                    database=DATABASE,
                    ssl_ca=SSL_CA if SSL_CA else None,
                    ssl_disabled=(SSL_CA is None)
                )
                cnx.autocommit = False
                print(f"✅ Created and connected to database '{DATABASE}'.")
                return cnx
        except Exception as e2:
            print(f"❌ Failed to create database '{DATABASE}': {e2}")
        print(f"❌ Connection failed: {e}")
        return None

# -----------------------------------------------------
# Run installer only once
# -----------------------------------------------------
cnx = connect_db()
if cnx:
    # Prefer actual database state over a filesystem marker. If tables are missing,
    # run the installer to (re)create them. This handles cases where the marker
    # file exists but the DB tables were not created or were deleted.
    if not sms_Installer.is_already_installed(cnx):
        print("🚀 Running installer to create missing tables...")
        sms_Installer.run_installer(cnx)
    else:
        print("⚡ Tables already exist. Skipping installer.")
    cnx.close()

# -----------------------------------------------------
# Main application
# -----------------------------------------------------
def main():
    """Main function to initialize and run the application."""
    db = Database()
    if not db.conn:
        print("Could not connect to the database. Exiting.")
        return

    # Initialize components
    dynamic_price = Dynamic_Price(db)
    customer_mgr = CustomerManager(db)
    product_mgr = ProductManager(db.conn, dynamic_price, customer_mgr)
    employee_mgr = EmployeeManager(db)
    finance_mgr = FinanceManager(db)
    stat_mgr = StatManager(db)

    menu = Menu(
        product_mgr,
        customer_mgr,
        employee_mgr,
        finance_mgr,
        stat_mgr,
        dynamic_price
    )

    # Run main menu loop
    try:
        menu.main_menu()
    except EOFError:
        # Handles Ctrl+D / EOF in Docker interactive terminal
        print("\nInput terminated. Exiting application.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        db.close()

# -----------------------------------------------------
# Entry point
# -----------------------------------------------------
if __name__ == "__main__":
    main()
