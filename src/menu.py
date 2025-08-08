
class Menu:
    def __init__(self, product_mgr, customer_mgr, employee_mgr, finance_mgr, stat_mgr):
        self.product_mgr = product_mgr
        self.customer_mgr = customer_mgr
        self.employee_mgr = employee_mgr
        self.finance_mgr = finance_mgr
        self.stat_mgr = stat_mgr

    def collect_product_data(self):
        print("Enter Product Details:")
        pid = input("ID: ")
        name = input("Name: ")
        price = float(input("Selling Price: "))
        cost = float(input("Cost Price: "))
        brand = input("Brand: ")
        qty = int(input("Quantity: "))
        sold = int(input("Items Sold: "))
        return (pid, name, price, cost, brand, qty, sold)

    def main_menu(self):
        while True:
            print("\n====== Store Management Console Menu ======")
            print("1. Product Operations")
            print("2. Customer Operations")
            print("3. Employee Operations")
            print("4. Finance & Stats")
            print("0. Exit")
            choice = input("Select an option: ")

            if choice == "1":
                self.product_menu()
            elif choice == "2":
                self.customer_menu()
            elif choice == "3":
                self.employee_menu()
            elif choice == "4":
                self.finance_menu()
            elif choice == "0":
                print("Exiting system.")
                break
            else:
                print("Invalid choice. Try again.")

    def product_menu(self):
        while True:
            print("\n-- Product Operations --")
            print("1. View Products")
            print("2. Add Product")
            print("3. Edit Product")
            print("4. Delete Product")
            print("5. Search Product")
            print("6. Purchase Product")
            print("0. Back to Main Menu")
            choice = input("Select an option: ")

            if choice == "1":
                self.product_mgr.view_all()
            elif choice == "2":
                self.product_mgr.add_product(self.collect_product_data())
            elif choice == "3":
                self.product_mgr.edit_product()
            elif choice == "4":
                self.product_mgr.delete_product()
            elif choice == "5":
                self.product_mgr.search_product()
            elif choice == "6":
                self.product_mgr.make_purchase()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def customer_menu(self):
        while True:
            print("\n-- Customer Operations --")
            print("1. View Customers")
            print("2. Add Customer")
            print("3. Edit Customer")
            print("4. Delete Customer")
            print("5. Search Customer")
            print("0. Back to Main Menu")
            choice = input("Select an option: ")

            if choice == "1":
                self.customer_mgr.view_all_customers()
            elif choice == "2":
                self.customer_mgr.add_customer()
            elif choice == "3":
                self.customer_mgr.edit_customer()
            elif choice == "4":
                self.customer_mgr.delete_customer()
            elif choice == "5":
                self.customer_mgr.search_customer()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def employee_menu(self):
        while True:
            print("\n-- Employee Operations --")
            print("1. View Employees")
            print("2. Add Employee")
            print("3. Edit Employee")
            print("4. Delete Employee")
            print("5. Search Employee")
            print("0. Back to Main Menu")
            choice = input("Select an option: ")

            if choice == "1":
                self.employee_mgr.view_all_employees()
            elif choice == "2":
                self.employee_mgr.add_employee()
            elif choice == "3":
                self.employee_mgr.edit_employee()
            elif choice == "4":
                self.employee_mgr.delete_employee()
            elif choice == "5":
                self.employee_mgr.search_employee()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def finance_menu(self):
        while True:
            print("\n-- Finance & Stats --")
            print("1. Profit by Product")
            print("2. Total Profit/Loss")
            print("3. Best Seller")
            print("4. Most Profitable Product")
            print("5. Least Seller")
            print("0. Back to Main Menu")
            choice = input("Select an option: ")

            if choice == "1":
                self.finance_mgr.profit_by_product()
            elif choice == "2":
                self.finance_mgr.total_profit_or_loss()
            elif choice == "3":
                self.stat_mgr.best_selling_product()
            elif choice == "4":
                self.stat_mgr.most_profitable_product()
            elif choice == "5":
                self.stat_mgr.least_selling_product()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
