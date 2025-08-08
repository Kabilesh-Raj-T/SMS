from .database import Database
from .product import ProductManage
from .customer import CustomerManager
from .employee import EmployeeManager
from .fin_n_stats import FinanceManager
from .menu import Menu

if __name__ == "__main__":
    db = Database()
    cursor = db.cursor

    product_mgr = ProductManager(db.conn, cursor)
    customer_mgr = CustomerManager(db.conn, cursor)
    employee_mgr = EmployeeManager(db.conn, cursor)
    finance_mgr = FinanceManager(db.conn, cursor)
    stat_mgr = StatManager(db.conn, cursor)

    menu = Menu(product_mgr, customer_mgr, employee_mgr, finance_mgr, stat_mgr)
    menu.main_menu()
