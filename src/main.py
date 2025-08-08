from src.database import Database
from src.product import ProductManage
from src.customer import CustomerManager
from src.employee import EmployeeManager
from src.fin_n_stats import FinanceManager
from src.menu import Menu

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
