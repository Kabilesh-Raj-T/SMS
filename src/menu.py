class Menu:
    def __init__(self, product_mgr, customer_mgr, employee_mgr, finance_mgr, stat_mgr, dynamic_price):
        self.product_mgr = product_mgr
        self.customer_mgr = customer_mgr
        self.employee_mgr = employee_mgr
        self.finance_mgr = finance_mgr
        self.stat_mgr = stat_mgr
        self.dynamic_price = dynamic_price

    def collect_product_data(self):
        print("Enter Product Details:")
        try:
            pid = input("ID: ").strip()
            name = input("Name: ").strip()
            price = float(input("MRP: "))
            cost = float(input("Cost Price: "))
            brand = input("Brand: ").strip()
            qty = int(input("Quantity: "))
            sold = int(input("Items Sold: "))
            expiry_date = input("Expiry Date (YYYY-MM-DD): ").strip()
            return (pid, name, price, cost, brand, qty, sold, expiry_date)
        except ValueError:
            print("Invalid input. Please enter correct data types.")
            return self.collect_product_data()

    def main_menu(self):
        menu_options = {
            "1": self.product_menu,
            "2": self.customer_menu,
            "3": self.employee_menu,
            "4": self.finance_menu,
            "5": self.dynamic_price_menu,
            "0": self.exit_system
        }
        while True:
            print("\n====== Store Management Console Menu ======")
            print("1. Product Operations")
            print("2. Customer Operations")
            print("3. Employee Operations")
            print("4. Finance & Stats")
            print("5. Dynamic Price Update")
            print("0. Exit")
            choice = input("Select an option: ").strip()
            action = menu_options.get(choice)
            if action:
                action()
                if choice == "0":
                    break
            else:
                print("Invalid choice. Try again.")

    def exit_system(self):
        print("Exiting system.")

    def product_menu(self):
        options = {
            "1": self.product_mgr.view_all,
            "2": lambda: self.product_mgr.add_product(self.collect_product_data()),
            "3": self.product_mgr.edit_product,
            "4": self.product_mgr.delete_product,
            "5": self.product_mgr.search_product,
            "6": self.product_mgr.make_purchase,
            "0": None
        }
        while True:
            print("\n-- Product Operations --")
            print("1. View Products")
            print("2. Add Product")
            print("3. Edit Product")
            print("4. Delete Product")
            print("5. Search Product")
            print("6. Purchase Product")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            action = options.get(choice)
            if action:
                action()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def customer_menu(self):
        options = {
            "1": self.customer_mgr.view_all_customers,
            "2": self.customer_mgr.add_customer,
            "3": self.customer_mgr.edit_customer,
            "4": self.customer_mgr.delete_customer,
            "5": self.customer_mgr.search_customer,
            "0": None
        }
        while True:
            print("\n-- Customer Operations --")
            print("1. View Customers")
            print("2. Add Customer")
            print("3. Edit Customer")
            print("4. Delete Customer")
            print("5. Search Customer")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            action = options.get(choice)
            if action:
                action()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def employee_menu(self):
        options = {
            "1": self.employee_mgr.view_all_employees,
            "2": self.employee_mgr.add_employee,
            "3": self.employee_mgr.edit_employee,
            "4": self.employee_mgr.delete_employee,
            "5": self.employee_mgr.search_employee,
            "0": None
        }
        while True:
            print("\n-- Employee Operations --")
            print("1. View Employees")
            print("2. Add Employee")
            print("3. Edit Employee")
            print("4. Delete Employee")
            print("5. Search Employee")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            action = options.get(choice)
            if action:
                action()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def finance_menu(self):
        options = {
            "1": self.finance_mgr.profit_by_product,
            "2": self.finance_mgr.total_profit_or_loss,
            "3": self.stat_mgr.best_selling_product,
            "4": self.stat_mgr.most_profitable_product,
            "5": self.stat_mgr.least_selling_product,
            "0": None
        }
        while True:
            print("\n-- Finance & Stats --")
            print("1. Profit by Product")
            print("2. Total Profit/Loss")
            print("3. Best Seller")
            print("4. Most Profitable Product")
            print("5. Least Seller")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            action = options.get(choice)
            if action:
                action()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def dynamic_price_menu(self):
        while True:
            print("\n-- Dynamic Price Update --")
            print("1. Update Prices")
            print("2. Get Dynamic Price for Product")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.dynamic_price.update_prices()
            elif choice == "2":
                product_id = input("Enter Product ID: ").strip()
                price = self.dynamic_price.get_dynamic_price(product_id)
                if price is not None:
                    print(f"Dynamic Price for Product ID {product_id}: {price}")
                else:
                    print("Product not found or price unavailable.")
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

