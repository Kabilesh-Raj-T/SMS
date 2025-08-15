class Menu:
    def __init__(self, product_mgr, customer_mgr, employee_mgr, finance_mgr, stat_mgr, dynamic_price):
        self.product_mgr = product_mgr
        self.customer_mgr = customer_mgr
        self.employee_mgr = employee_mgr
        self.finance_mgr = finance_mgr
        self.stat_mgr = stat_mgr
        self.dynamic_price = dynamic_price

    def get_validated_input(self, prompt, cast_type):
        """A helper function to get validated user input."""
        while True:
            try:
                return cast_type(input(prompt))
            except ValueError:
                print(f"Invalid input. Please enter a valid {cast_type.__name__}.")
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

    def collect_product_data(self):
        print("Enter Product Details:")
        pid = input("ID: ").strip()
        name = input("Name: ").strip()
        price = self.get_validated_input("MRP: ", float)
        cost = self.get_validated_input("Cost Price: ", float)
        brand = input("Brand: ").strip()
        qty = self.get_validated_input("Quantity: ", int)
        sold = self.get_validated_input("Items Sold: ", int)
        expiry_date = input("Expiry Date (YYYY-MM-DD): ").strip()
        # Basic validation can be added here for date format if needed
        return (pid, name, price, cost, brand, qty, sold, expiry_date)

    def main_menu(self):
        menu_options = {
            "1": self.product_menu, "2": self.customer_menu,
            "3": self.employee_menu, "4": self.finance_menu,
            "5": self.dynamic_price_menu, "0": self.exit_system
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
                if choice == "0":
                    action()
                    break
                action()
            else:
                print("Invalid choice. Try again.")

    def exit_system(self):
        print("Exiting system.")

    def _run_menu(self, title, options):
        while True:
            print(f"\n-- {title} --")
            for key, value in options.items():
                if key != "0":
                    print(f"{key}. {value[0]}")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            if choice == "0":
                break
            action = options.get(choice)
            if action:
                action[1]()
            else:
                print("Invalid choice.")

    def product_menu(self):
        options = {
            "1": ("View Products", self.product_mgr.view_all),
            "2": ("Add Product", lambda: self.product_mgr.add_product(self.collect_product_data())),
            "3": ("Edit Product", self.product_mgr.edit_product),
            "4": ("Delete Product", self.product_mgr.delete_product),
            "5": ("Search Product", self.product_mgr.search_product),
            "6": ("Make Purchase", self.product_mgr.make_purchase),
        }
        self._run_menu("Product Operations", options)

    def customer_menu(self):
        options = {
            "1": ("View Customers", self.customer_mgr.view_all_customers),
            "2": ("Add Customer", self.customer_mgr.add_customer),
            "3": ("Edit Customer", self.customer_mgr.edit_customer),
            "4": ("Delete Customer", self.customer_mgr.delete_customer),
            "5": ("Search Customer", self.customer_mgr.search_customer),
        }
        self._run_menu("Customer Operations", options)

    def employee_menu(self):
        options = {
            "1": ("View Employees", self.employee_mgr.view_all_employees),
            "2": ("Add Employee", self.employee_mgr.add_employee),
            "3": ("Edit Employee", self.employee_mgr.edit_employee),
            "4": ("Delete Employee", self.employee_mgr.delete_employee),
            "5": ("Search Employee", self.employee_mgr.search_employee),
        }
        self._run_menu("Employee Operations", options)

    def finance_menu(self):
        options = {
            "1": ("Profit by Product", self.finance_mgr.profit_by_product),
            "2": ("Total Profit/Loss", self.finance_mgr.total_profit_or_loss),
            "3": ("Best Seller", self.stat_mgr.best_selling_product),
            "4": ("Most Profitable", self.stat_mgr.most_profitable_product),
            "5": ("Least Seller", self.stat_mgr.least_selling_product),
        }
        self._run_menu("Finance & Stats", options)

    def dynamic_price_menu(self):
        while True:
            print("\n-- Dynamic Price Update --")
            print("1. Update All Product Prices")
            print("2. Get Dynamic Price for a Product")
            print("0. Back to Main Menu")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.dynamic_price.update_prices()
            elif choice == "2":
                product_id = input("Enter Product ID: ").strip()
                price = self.dynamic_price.get_dynamic_price(product_id)
                if price is not None:
                    print(f"Calculated Dynamic Price for Product ID {product_id}: {price}")
                else:
                    print("Product not found or price unavailable.")
            elif choice == "0":
                break
            else:
                print("Invalid choice.")