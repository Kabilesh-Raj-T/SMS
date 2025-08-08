from datetime import date
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
            customer_id = int(customer_id)+ 1
        else:
            customer_id = None

        product_ids, quantities, line_totals = [], [], []
        total_price = 0

        while True:
            product_id = input("Enter the ID of the Product purchased | ").strip()
            if not product_id:
                break

            self.cursor.execute("SELECT SELLING_PRICE FROM product_database WHERE BINARY ID = %s", (product_id,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Product with ID {product_id} not found. Purchase aborted for this item.")
                continue

            quantity = int(input("Enter the quantity of this purchased product | "))

            selling_price = result[0]

            self.cursor.execute(
                "INSERT INTO sales_history (product_id, quantity, sale_date) VALUES (%s, %s, %s)",
                (product_id, quantity, date.today())
            )
            self.cursor.execute("UPDATE product_database SET QUANTITY = QUANTITY - %s WHERE ID = %s", (quantity, product_id))
            self.cursor.execute("UPDATE product_database SET ITEMS_SOLD = ITEMS_SOLD + %s WHERE ID = %s", (quantity, product_id))
            self.db.commit()

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
