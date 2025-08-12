from .database import Database
from .product import ProductManager
from .customer import CustomerManager
from .employee import EmployeeManager
from .fin_and_stats import FinanceManager, StatManager
from .menu import Menu
from .dynamic_price import Dynamic_Price

if __name__ == "__main__":
    db = Database()
    cursor = db.cursor
    dynamic_price = Dynamic_Price(db, cursor)
    product_mgr = ProductManager(db, dynamic_price, cursor)
    customer_mgr = CustomerManager(db, cursor)
    employee_mgr = EmployeeManager(db, cursor)
    finance_mgr = FinanceManager(db, cursor)
    stat_mgr = StatManager(db, cursor)

    menu = Menu(product_mgr, customer_mgr, employee_mgr, finance_mgr, stat_mgr, dynamic_price)
    try:
        menu.main_menu()
    finally:
        db.close()
