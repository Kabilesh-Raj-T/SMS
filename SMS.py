import mysql.connector
from tkinter import *

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", user="root", passwd="bts613", database="sms_database"
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

class Product:
    def __init__(self, db: Database):
        self.db = db

    def view_all(self):
        print(f"{'ID':<10}{'NAME':<20}{'PRICE':<10}{'BRAND':<10}{'QTY':<10}{'SOLD':<10}")
        self.db.execute("SELECT * FROM product_database")
        for row in self.db.fetch_all():
            print(f"{row[0]:<10}{row[1]:<20}{row[2]:<10}{row[4]:<10}{row[5]:<10}{row[6]:<10}")

    def add_product(self, product):
        query = """INSERT INTO product_database 
        (ID, NAME, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        self.db.execute(query, product)
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

        # Check if customer exists
        self.cursor.execute("SELECT CONTACT_NUMBER FROM customer_database")
        existing_contacts = [row[0] for row in self.cursor.fetchall()]

        customer_exists = int(customer_contact) in existing_contacts
        if not customer_exists:
            customer_name = input("Enter the name of the customer                   | ")
            self.cursor.execute("SELECT MAX(ID) FROM customer_database")
            customer_id = self.cursor.fetchone()[0] or 0
            customer_id += 1
        else:
            customer_id = None  # Will not be used

        product_ids = []
        quantities = []
        line_totals = []
        total_price = 0

        while True:
            product_id = input("Enter the ID of the Product purchased            | ")
            if not product_id:
                break

            quantity = int(input("Enter the quantity of this purchased product     | "))
            
            # Update DB
            update_qty_query = "UPDATE product_database SET QUANTITY = QUANTITY - %s WHERE ID = %s"
            update_sold_query = "UPDATE product_database SET ITEMS_SOLD = ITEMS_SOLD + %s WHERE ID = %s"
            self.cursor.execute(update_qty_query, (quantity, product_id))
            self.cursor.execute(update_sold_query, (quantity, product_id))
            self.db.commit()

            self.cursor.execute("SELECT SELLING_PRICE FROM product_database WHERE ID = %s", (product_id,))
            selling_price = self.cursor.fetchone()[0]
            line_total = selling_price * quantity
            total_price += line_total

            product_ids.append(product_id)
            quantities.append(quantity)
            line_totals.append(line_total)

        # Print receipt
        print("\n%-15s%-20s%-15s%-15s%-15s%-15s" % ('ID', 'NAME', 'BRAND', 'RATE', 'QUANTITY', 'AMOUNT'))
        for i, product_id in enumerate(product_ids):
            self.cursor.execute(
                "SELECT ID, NAME, BRAND, SELLING_PRICE FROM product_database WHERE ID = %s", (product_id,))
            product = self.cursor.fetchone()
            print("%-15s%-20s%-15s%-15s%-15s%-15s" % (
                product[0], product[1], product[2], product[3], quantities[i], line_totals[i]))

        print("\nTotal amount to be paid: ", total_price)

        # Prepare purchase record
        purchase_record = ''.join([
            f"{pid} {self.get_product_name(pid)} {self.get_price(pid)} {qty} {amt}|"
            for pid, qty, amt in zip(product_ids, quantities, line_totals)
        ]) + str(total_price) + '|'

        if not customer_exists:
            insert_customer = """
                INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, PURCHASES)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(insert_customer, (customer_id, customer_name, customer_contact, purchase_record))
        else:
            self.cursor.execute("SELECT PURCHASES FROM customer_database WHERE CONTACT_NUMBER = %s", (customer_contact,))
            existing_purchases = self.cursor.fetchone()[0] or ''
            updated_purchases = purchase_record + existing_purchases
            self.cursor.execute(
                "UPDATE customer_database SET PURCHASES = %s WHERE CONTACT_NUMBER = %s",
                (updated_purchases, customer_contact)
            )

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
