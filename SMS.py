import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", user="root", passwd="Kabilesh1!", database="sms_database"
        )
        self.cursor = self.conn.cursor()

    def execute(self, query, values=None):
        self.cursor.execute(query, values or ())
        return self.cursor

    def commit(self):
        self.conn.commit()

    def fetch_all(self):
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

class ProductManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def view_all(self):
        print(f"{'ID':<10}{'NAME':<20}{'PRICE':<10}{'BRAND':<10}{'QTY':<10}{'SOLD':<10}")
        self.cursor.execute("SELECT * FROM product_database")
        for row in self.cursor.fetchall():
            print(f"{row[0]:<10}{row[1]:<20}{row[2]:<10}{row[4]:<10}{row[5]:<10}{row[6]:<10}")

    def add_product(self, product):
        query = """INSERT INTO product_database 
        (ID, NAME, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.execute(query, product)
        self.db.commit()

    def edit_product(self):
        product_id = input("Enter the ID of the product to be edited | ")
        self.cursor.execute("SELECT ID FROM product_database")
        existing_ids = [row[0] for row in self.cursor.fetchall()]

        if product_id not in existing_ids:
            print("There is no product with this ID")
            return

        self.cursor.execute("SELECT * FROM product_database WHERE ID = %s", (product_id,))
        product = self.cursor.fetchone()
        if product:
            print("\n%-15s%-20s%-15s%-15s%-15s%-15s%-15s" %
                  ("ID", "NAME", "SELLING PRICE", "COST PRICE", "BRAND", "QUANTITY", "ITEMS SOLD"))
            print("%-15s%-20s%-15s%-15s%-15s%-15s%-15s" % product)

            field_map = {
                'items sold': 'ITEMS_SOLD',
                'selling price': 'SELLING_PRICE',
                'cost price': 'COST_PRICE',
                'name': 'NAME',
                'brand': 'BRAND',
                'quantity': 'QUANTITY',
                'id': 'ID'
            }

            field = input("Enter the field to be edited             | ").strip().lower()
            value = input("Enter the value to be set                | ").strip()

            if field not in field_map:
                print("Invalid field name.")
                return

            field_db = field_map[field]
            update_query = f"UPDATE product_database SET {field_db} = %s WHERE ID = %s"
            self.cursor.execute(update_query, (value, product_id))
            self.db.commit()

            print("\n1 row updated")
            self.cursor.execute("SELECT * FROM product_database WHERE ID = %s", (product_id,))
            updated_product = self.cursor.fetchone()
            print("\nUpdated Information -->")
            print("%-15s%-20s%-15s%-15s%-15s%-15s%-15s" %
                  ("ID", "NAME", "SELLING PRICE", "COST PRICE", "BRAND", "QUANTITY", "ITEMS SOLD"))
            print("%-15s%-20s%-15s%-15s%-15s%-15s%-15s" % updated_product)
        else:
            print("No data found.")

    def delete_product(self):
        product_id = input("Enter the Product ID to be deleted : ")
        self.cursor.execute("DELETE FROM product_database WHERE ID = %s", (product_id,))
        self.db.commit()
        print("Product Deleted")

    def make_purchase(self):
        customer_contact = input("Enter the contact number of the customer         | ")

        self.cursor.execute("SELECT CONTACT_NUMBER FROM customer_database")
        existing_contacts = [row[0] for row in self.cursor.fetchall()]
        customer_exists = int(customer_contact) in existing_contacts

        if not customer_exists:
            customer_name = input("Enter the name of the customer                   | ")
            self.cursor.execute("SELECT MAX(ID) FROM customer_database")
            customer_id = self.cursor.fetchone()[0] or 0
            customer_id += 1
        else:
            customer_id = None

        product_ids, quantities, line_totals = [], [], []
        total_price = 0

        while True:
            product_id = input("Enter the ID of the Product purchased            | ")
            if not product_id:
                break

            quantity = int(input("Enter the quantity of this purchased product     | "))
            self.cursor.execute("UPDATE product_database SET QUANTITY = QUANTITY - %s WHERE ID = %s", (quantity, product_id))
            self.cursor.execute("UPDATE product_database SET ITEMS_SOLD = ITEMS_SOLD + %s WHERE ID = %s", (quantity, product_id))
            self.db.commit()

            self.cursor.execute("SELECT SELLING_PRICE FROM product_database WHERE ID = %s", (product_id,))
            selling_price = self.cursor.fetchone()[0]
            line_total = selling_price * quantity
            total_price += line_total

            product_ids.append(product_id)
            quantities.append(quantity)
            line_totals.append(line_total)

        print("\n%-15s%-20s%-15s%-15s%-15s%-15s" % ('ID', 'NAME', 'BRAND', 'RATE', 'QUANTITY', 'AMOUNT'))
        for i, pid in enumerate(product_ids):
            self.cursor.execute("SELECT ID, NAME, BRAND, SELLING_PRICE FROM product_database WHERE ID = %s", (pid,))
            product = self.cursor.fetchone()
            print("%-15s%-20s%-15s%-15s%-15s%-15s" % (product[0], product[1], product[2], product[3], quantities[i], line_totals[i]))

        print("\nTotal amount to be paid: ", total_price)

        purchase_record = ''.join([
            f"{pid} {self.get_product_name(pid)} {self.get_price(pid)} {qty} {amt}|"
            for pid, qty, amt in zip(product_ids, quantities, line_totals)
        ]) + str(total_price) + '|'

        if not customer_exists:
            self.cursor.execute(
                "INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, PURCHASES) VALUES (%s, %s, %s, %s)",
                (customer_id, customer_name, customer_contact, purchase_record)
            )
        else:
            self.cursor.execute("SELECT PURCHASES FROM customer_database WHERE CONTACT_NUMBER = %s", (customer_contact,))
            existing_purchases = self.cursor.fetchone()[0] or ''
            updated_purchases = purchase_record + existing_purchases
            self.cursor.execute("UPDATE customer_database SET PURCHASES = %s WHERE CONTACT_NUMBER = %s", (updated_purchases, customer_contact))

        self.db.commit()
        print("Purchase recorded successfully.\n")

    def get_product_name(self, product_id):
        self.cursor.execute("SELECT NAME FROM product_database WHERE ID = %s", (product_id,))
        return self.cursor.fetchone()[0]

    def get_price(self, product_id):
        self.cursor.execute("SELECT SELLING_PRICE FROM product_database WHERE ID = %s", (product_id,))
        return self.cursor.fetchone()[0]

    def search_product(self):
        product_id = input("Enter the ID of product to be searched : ")
        self.cursor.execute("SELECT ID FROM product_database")
        all_ids = [row[0] for row in self.cursor.fetchall()]
        if product_id not in map(str, all_ids):
            print("There is no product data with this ID\n")
            return

        self.cursor.execute(
            "SELECT NAME, SELLING_PRICE, BRAND, QUANTITY, ITEMS_SOLD FROM product_database WHERE ID = %s",
            (product_id,)
        )
        result = self.cursor.fetchone()
        if result:
            print("\n%-15s%-20s%-15s%-15s%-15s%-15s" %
                  ("ID", "NAME", "PRICE", "BRAND", "QUANTITY", "ITEMS SOLD"))
            print("%-15s%-20s%-15s%-15s%-15s%-15s" %
                  (product_id, result[0], result[1], result[2], result[3], result[4]))
        else:
            print("No data found.\n")

class CustomerManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def view_all_customers(self):
        print("_" * 130)
        print("%-15s%-20s%-25s%-15s%-25s%-20s" % ("ID", "NAME", "CONTACT NUMBER", "GENDER", "EMAIL", "PURCHASES"))
        print("_" * 130)
        self.cursor.execute("SELECT * FROM customer_database")
        for row in self.cursor.fetchall():
            purchases = row[5].split('|')
            for i, purchase in enumerate(purchases):
                if i == 0:
                    print("%-15s%-20s%-25s%-15s%-25s%-20s" % (row[0], row[1], row[2], row[3], row[4], purchase))
                else:
                    print("%-15s%-20s%-25s%-15s%-25s%-20s" % ('', '', '', '', '', purchase))
            print("_" * 130)

    def add_customer(self):
        self.cursor.execute("SELECT ID FROM customer_database")
        existing_ids = [str(row[0]) for row in self.cursor.fetchall()]
        customer_id = input("Enter the Customer ID                    |  ")
        if customer_id in existing_ids:
            print("Customer already exists.\n")
            return

        name = input("Enter the Customer Name                  |  ")
        contact = input("Enter contact number of customer         |  ")
        gender = input("Enter gender of customer                 |  ")
        email = input("Enter email of customer                  |  ")

        query = """INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, GENDER, EMAIL, PURCHASES)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        self.cursor.execute(query, (customer_id, name, contact, gender, email, " "))
        self.db.commit()
        print("Customer Data Inserted")

    def edit_customer(self):
        customer_id = input("Enter the ID of the customer to be edited | ")
        self.cursor.execute("SELECT * FROM customer_database WHERE ID = %s", (customer_id,))
        data = self.cursor.fetchone()
        if not data:
            print("No customer found with this ID.")
            return

        purchases = data[5].split('|')
        print("%-15s%-20s%-25s%-15s%-25s%-20s" % ("ID", "NAME", "CONTACT NUMBER", "GENDER", "EMAIL", "PURCHASES"))
        for i, p in enumerate(purchases):
            if i == 0:
                print("%-15s%-20s%-25s%-15s%-25s%-20s" % (data[0], data[1], data[2], data[3], data[4], p))
            else:
                print("%-15s%-20s%-25s%-15s%-25s%-20s" % ('', '', '', '', '', p))

        field = input("Enter the field to be edited              | ").strip().lower()
        value = input("Enter the value to be set                 | ")

        if field == 'contact number':
            field = 'CONTACT_NUMBER'
        elif field == 'email':
            field = 'EMAIL'
        elif field == 'name':
            field = 'NAME'
        elif field == 'gender':
            field = 'GENDER'
        elif field == 'id':
            field = 'ID'
        else:
            print("Invalid field.")
            return

        query = f"UPDATE customer_database SET {field} = %s WHERE ID = %s"
        self.cursor.execute(query, (value, customer_id))
        self.db.commit()
        print("1 row updated")

    def delete_customer(self):
        customer_id = input("Enter the Customer ID to be deleted : ")
        self.cursor.execute("DELETE FROM customer_database WHERE ID = %s", (customer_id,))
        self.db.commit()
        print("Row Deleted")

    def search_customer(self):
        customer_id = input("Enter the ID of Customer to be searched : ")
        self.cursor.execute("SELECT ID FROM customer_database")
        ids = [str(row[0]) for row in self.cursor.fetchall()]
        if customer_id not in ids:
            print("No customer data with this ID.\n")
            return

        self.cursor.execute(
            "SELECT NAME, CONTACT_NUMBER, EMAIL, GENDER, PURCHASES FROM customer_database WHERE ID = %s",
            (customer_id,)
        )
        data = self.cursor.fetchone()
        if data:
            purchases = data[4].split('|')
            print("%-15s%-20s%-25s%-15s%-25s%-20s" % ("ID", "NAME", "CONTACT NUMBER", "GENDER", "EMAIL", "PURCHASES"))
            for i, p in enumerate(purchases):
                if i == 0:
                    print("%-15s%-20s%-25s%-15s%-25s%-20s" % (customer_id, data[0], data[1], data[3], data[2], p))
                else:
                    print("%-15s%-20s%-25s%-15s%-25s%-20s" % ('', '', '', '', '', p))

class EmployeeManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def view_all_employees(self):
        print("\n%-15s%-20s%-25s%-25s%-20s%-20s" %
              ("ID", "NAME", "CONTACT NUMBER", "GENDER", "POSITION", "SALARY"))
        self.cursor.execute("SELECT * FROM employee_database")
        for row in self.cursor.fetchall():
            print("%-15s%-20s%-25s%-25s%-20s%-20s" %
                  (row[0], row[1], row[2], row[3], row[4], row[5]))
        print()

    def add_employee(self):
        self.cursor.execute("SELECT ID FROM employee_database")
        ids = [str(row[0]) for row in self.cursor.fetchall()]
        emp_id = input("Enter the employee ID                    |  ")
        if emp_id in ids:
            print("Employee already exists.")
            return

        name = input("Enter the employee Name                  |  ")
        contact = input("Enter contact number of employee         |  ")
        gender = input("Enter gender of employee                 |  ")
        position = input("Enter position of employee               |  ")
        salary = input("Enter salary of employee                 |  ")

        query = """
        INSERT INTO employee_database (ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (emp_id, name, contact, gender, position, salary))
        self.db.commit()
        print("Employee Data Inserted")

    def edit_employee(self):
        emp_id = input("Enter the ID of the employee to be edited | ")
        self.cursor.execute("SELECT * FROM employee_database WHERE ID = %s", (emp_id,))
        data = self.cursor.fetchone()
        if not data:
            print("No employee found with this ID.")
            return

        print("\n%-15s%-20s%-25s%-25s%-20s%-20s" %
              ("ID", "NAME", "CONTACT NUMBER", "GENDER", "POSITION", "SALARY"))
        print("%-15s%-20s%-25s%-25s%-20s%-20s" % data)

        field = input("Enter the field to be edited              | ").strip().lower()
        value = input("Enter the value to be set                 | ")

        field_map = {
            'name': 'NAME',
            'contact number': 'CONTACT_NUMBER',
            'gender': 'GENDER',
            'position': 'POSITION',
            'salary': 'SALARY',
            'id': 'ID'
        }

        if field not in field_map:
            print("Invalid field.")
            return

        query = f"UPDATE employee_database SET {field_map[field]} = %s WHERE ID = %s"
        self.cursor.execute(query, (value, emp_id))
        self.db.commit()

        self.cursor.execute("SELECT * FROM employee_database WHERE ID = %s", (value if field == 'id' else emp_id,))
        data = self.cursor.fetchone()
        print("\nUpdated Information -->")
        print("%-15s%-20s%-25s%-25s%-20s%-20s" %
              ("ID", "NAME", "CONTACT NUMBER", "GENDER", "POSITION", "SALARY"))
        print("%-15s%-20s%-25s%-25s%-20s%-20s" % data)

    def delete_employee(self):
        emp_id = input("Enter the employee ID to be deleted : ")
        self.cursor.execute("DELETE FROM employee_database WHERE ID = %s", (emp_id,))
        self.db.commit()
        print("Employee Deleted")

    def search_employee(self):
        emp_id = input("Enter the ID of employee to be searched : ")
        self.cursor.execute("SELECT ID FROM employee_database")
        ids = [str(row[0]) for row in self.cursor.fetchall()]
        if emp_id not in ids:
            print("No employee data with this ID.")
            return

        self.cursor.execute(
            "SELECT NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY FROM employee_database WHERE ID = %s", (emp_id,))
        row = self.cursor.fetchone()
        print("%-15s%-20s%-25s%-25s%-20s%-20s" %
              ("ID", "NAME", "CONTACT NUMBER", "GENDER", "POSITION", "SALARY"))
        print("%-15s%-20s%-25s%-25s%-20s%-20s" %
              (emp_id, row[0], row[1], row[2], row[3], row[4]))

class FinanceManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def profit_by_product(self):
        print("%-15s%-20s%-15s%-15s%-15s" %
              ("ID", "NAME", "SELLING PRICE", "COST PRICE", "PROFIT/LOSS"))

        self.cursor.execute("SELECT ID, NAME, SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD FROM product_database")
        for row in self.cursor.fetchall():
            product_id, name, selling_price, cost_price, quantity, items_sold = row
            revenue = selling_price * items_sold
            cost = (quantity + items_sold) * cost_price
            profit_loss = revenue - cost
            print("%-15s%-20s%-15.2f%-15.2f%-15.2f" %
                  (product_id, name, selling_price, cost_price, profit_loss))

    def total_profit_or_loss(self):
        self.cursor.execute("SELECT SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD FROM product_database")
        total = 0
        for s_price, c_price, qty, sold in self.cursor.fetchall():
            revenue = s_price * sold
            cost = (qty + sold) * c_price
            profit_loss = revenue - cost
            total += profit_loss

        if total < 0:
            print(f"LOSS   = {abs(total):.2f}")
        else:
            print(f"PROFIT = {total:.2f}")

class StatManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def best_selling_product(self):
        self.cursor.execute(
            "SELECT ID, NAME, ITEMS_SOLD FROM product_database ORDER BY ITEMS_SOLD DESC LIMIT 1"
        )
        product = self.cursor.fetchone()
        if product:
            print("\n📈 Best-Selling Product")
            print(f"ID: {product[0]}, NAME: {product[1]}, ITEMS SOLD: {product[2]}")
        else:
            print("No products found.")

    def most_profitable_product(self):
        self.cursor.execute("SELECT ID, NAME, SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD FROM product_database")

        max_profit = float('-inf')
        best_product = None

        for row in self.cursor.fetchall():
            product_id, name, s_price, c_price, qty, sold = row
            s_price = s_price or 0
            c_price = c_price or 0
            qty = qty or 0
            sold = sold or 0

            revenue = s_price * sold
            cost = (qty + sold) * c_price
            profit = revenue - cost

            if profit > max_profit:
                max_profit = profit
                best_product = (product_id, name, profit)

        if best_product:
            print("\n💰 Most Profitable Product")
            print(f"ID: {best_product[0]}, NAME: {best_product[1]}, PROFIT: {best_product[2]:.2f}")
        else:
            print("No products found.")

    def least_selling_product(self):
        self.cursor.execute(
            "SELECT ID, NAME, ITEMS_SOLD FROM product_database ORDER BY ITEMS_SOLD ASC LIMIT 1"
        )
        product = self.cursor.fetchone()
        if product:
            print("\n📉 Least-Selling Product")
            print(f"ID: {product[0]}, NAME: {product[1]}, ITEMS SOLD: {product[2]}")
        else:
            print("No products found.")

db = Database()
cursor = db.cursor
product_mgr = ProductManager(db.conn, cursor)
customer_mgr = CustomerManager(db.conn, cursor)
employee_mgr = EmployeeManager(db.conn, cursor)
finance_mgr = FinanceManager(db.conn, cursor)
stat_mgr = StatManager(db.conn, cursor)

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

if __name__ == "__main__":
    menu = Menu(product_mgr, customer_mgr, employee_mgr, finance_mgr, stat_mgr)
    menu.main_menu()
