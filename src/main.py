from database import Database
from product import ProductManager
from customer import CustomerManager
from employee import EmployeeManager
from fin_and_stats import FinanceManager, StatManager
from menu import Menu
from dynamic_price import Dynamic_Price

def main():
    """Main function to initialize and run the application."""
    db = Database()
    if not db.conn:
        print("Could not connect to the database. Exiting.")
        return

    dynamic_price = Dynamic_Price(db)
    customer_mgr = CustomerManager(db)
    product_mgr = ProductManager(db, dynamic_price, customer_mgr)
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