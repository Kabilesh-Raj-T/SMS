from datetime import date, datetime

def sanitize(value):
    """Convert value to string and strip whitespace."""
    return str(value).strip() if value is not None else ""

class ProductManager:
    def __init__(self, db, dynamic_price, cursor):
        self.db = db
        self.dynamic_price = dynamic_price
        self.cursor = cursor

    def view_all(self):
        headers = f"{'ID':<10}{'NAME':<20}{'MRP':<10}{'SELLING_PRICE':<15}{'COST_PRICE':<15}{'BRAND':<15}{'QUANTITY':<10}{'ITEMS_SOLD':<12}{'EXPIRY_DATE':<12}"
        print(headers)
        self.cursor.execute("SELECT ID, NAME, MRP, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE FROM product_database")
        for row in self.cursor.fetchall():
            displayed = [str(col) if col is not None else "N/A" for col in row]
            print(f"{displayed[0]:<10}{displayed[1]:<20}{displayed[2]:<10}{displayed[3]:<15}{displayed[4]:<15}{displayed[5]:<15}{displayed[6]:<10}{displayed[7]:<12}{displayed[8]:<12}")

    def add_product(self, product):
        product_id = product[0]
        self.cursor.execute("SELECT ID FROM product_database WHERE ID = %s", (product_id,))
        if self.cursor.fetchone():
            print(f"Product with ID {product_id} already exists.")
            return
        query = """INSERT INTO product_database 
        (ID, NAME, MRP, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.execute(query, product)
        self.db.commit()
        print("Product added successfully.")
        dynamic_price = self.dynamic_price.get_dynamic_price(product_id)
        if dynamic_price is not None:
            update_query = "UPDATE product_database SET SELLING_PRICE = %s WHERE ID = %s"
            self.cursor.execute(update_query, (dynamic_price, product_id))
            self.db.commit()
            print(f"Dynamic selling price set to {dynamic_price} for product ID {product_id}")
        else:
            print("Could not calculate dynamic price for the product.")

    def edit_product(self):
        product_id = input("Enter the ID of the product to be edited | ").strip()

        self.cursor.execute("SELECT ID FROM product_database")
        existing_ids = [str(row[0]) for row in self.cursor.fetchall()]

        if product_id not in existing_ids:
            print("There is no product with this ID")
            return

        self.cursor.execute(
            "SELECT ID, NAME, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE "
            "FROM product_database WHERE ID = %s", (product_id,)
        )
        product = self.cursor.fetchone()
        if not product:
            print("No data found.")
            return

        print("\n%-15s%-20s%-15s%-15s%-15s%-15s%-15s%-15s" %
              ("ID", "NAME", "SELLING PRICE", "COST PRICE", "BRAND", "QUANTITY", "ITEMS SOLD", "EXPIRY DATE"))

        expiry_display = product[7].strftime('%Y-%m-%d') if isinstance(product[7], (datetime, date)) else (str(product[7]) if product[7] else 'N/A')
        sell_price_display = f"{product[2]:.2f}" if isinstance(product[2], (int, float)) else str(product[2])
        cost_price_display = f"{product[3]:.2f}" if isinstance(product[3], (int, float)) else str(product[3])
        print("%-15s%-20s%-15s%-15s%-15s%-15s%-15s%-15s" % (
            product[0], product[1], sell_price_display, cost_price_display, product[4], product[5], product[6], expiry_display
        ))

        field_map = {
            'items sold': 'ITEMS_SOLD',
            'selling price': 'SELLING_PRICE',
            'cost price': 'COST_PRICE',
            'name': 'NAME',
            'brand': 'BRAND',
            'quantity': 'QUANTITY',
            'id': 'ID',
            'mrp': 'MRP',
            'expiry date': 'EXPIRY_DATE'
        }

        field = input("Enter the field to be edited             | ").strip().lower()
        if field not in field_map:
            print("Invalid field name.")
            return

        value = input("Enter the value to be set                | ").strip()
        field_db = field_map[field]

        numeric_float_fields = {'SELLING_PRICE', 'COST_PRICE', 'MRP'}
        numeric_int_fields = {'ID', 'QUANTITY', 'ITEMS_SOLD'}
        date_fields = {'EXPIRY_DATE'}

        try:
            if field_db in numeric_float_fields:
                value_cast = float(value)
            elif field_db in numeric_int_fields:
                value_cast = int(value)
            elif field_db in date_fields:
                value_cast = datetime.strptime(value, '%Y-%m-%d').date()
            else:
                value_cast = value
        except ValueError:
            print(f"Invalid value type for field '{field}'. Expected {field_db} compatible format.")
            return

        update_query = f"UPDATE product_database SET {field_db} = %s WHERE ID = %s"
        self.cursor.execute(update_query, (value_cast, product_id))
        self.db.commit()

        if field_db != 'SELLING_PRICE':
            dynamic_price = self.dynamic_price.get_dynamic_price(product_id)
            if dynamic_price is not None:
                self.cursor.execute("UPDATE product_database SET SELLING_PRICE = %s WHERE ID = %s", (dynamic_price, product_id))
                self.db.commit()

        self.cursor.execute(
            "SELECT ID, NAME, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE "
            "FROM product_database WHERE ID = %s", (product_id,)
        )
        updated_product = self.cursor.fetchone()
        expiry_display = updated_product[7].strftime('%Y-%m-%d') if isinstance(updated_product[7], (datetime, date)) else (str(updated_product[7]) if updated_product[7] else 'N/A')
        sell_price_display = f"{updated_product[2]:.2f}" if isinstance(updated_product[2], (int, float)) else str(updated_product[2])
        cost_price_display = f"{updated_product[3]:.2f}" if isinstance(updated_product[3], (int, float)) else str(updated_product[3])

        print("\nUpdated Product Details:")
        print("\n%-15s%-20s%-15s%-15s%-15s%-15s%-15s%-15s" %
              ("ID", "NAME", "SELLING PRICE", "COST PRICE", "BRAND", "QUANTITY", "ITEMS SOLD", "EXPIRY DATE"))
        print("%-15s%-20s%-15s%-15s%-15s%-15s%-15s%-15s" % (
            updated_product[0], updated_product[1], sell_price_display, cost_price_display,
            updated_product[4], updated_product[5], updated_product[6], expiry_display
        ))

    def delete_product(self):
        product_id = input("Enter the Product ID to be deleted : ").strip()
        self.cursor.execute("SELECT ID FROM product_database WHERE ID = %s", (product_id,))
        if not self.cursor.fetchone():
            print("There is no product with this ID")
            return
        self.cursor.execute("DELETE FROM product_database WHERE ID = %s", (product_id,))
        self.db.commit()
        print("Product Deleted")

    def make_purchase(self):
        customer_contact = input("Customer contact number: ").strip()
        if not customer_contact:
            print("Invalid contact number.")
            return
        self.cursor.execute("SELECT CONTACT_NUMBER FROM customer_database")
        existing_contacts = [str(row[0]) for row in self.cursor.fetchall()]
        customer_exists = customer_contact in existing_contacts
        if not customer_exists:
            input("Enter the name of the customer                   | ").strip()
            self.cursor.execute("SELECT COALESCE(MAX(CAST(ID AS UNSIGNED)), 0) FROM customer_database")
            self.cursor.fetchone()[0] + 1
            # Continue with purchase logic for new customer
        product_ids, quantities, line_totals = [], [], []
        total_price = 0.0
        while True:
            product_id = input("Enter the ID of the Product purchased (blank to finish) | ").strip()
            if not product_id:
                break
            self.cursor.execute("SELECT QUANTITY FROM product_database WHERE ID = %s", (product_id,))
            row_qty = self.cursor.fetchone()
            if not row_qty:
                print(f"Product ID {product_id} not found. Skipping.")
                continue
            available_qty = int(row_qty[0])
            query_price = """
            SELECT p.ID,
                ROUND(
                        CASE
                            WHEN DATEDIFF(p.EXPIRY_DATE, CURDATE()) >= %s 
                                THEN p.MRP
                            ELSE 
                                p.MRP * (
                                    %s + (1 - %s) *
                                    GREATEST(0, LEAST(1, DATEDIFF(p.EXPIRY_DATE, CURDATE()) / %s)) *
                                    (IFNULL(s.sold_last_month, 0) / NULLIF((IFNULL(s.sold_last_month, 0) + p.QUANTITY), 0))
                                )
                        END
                , 2) AS dynamic_price
            FROM product_database p
            LEFT JOIN (
                SELECT product_id, IFNULL(SUM(quantity), 0) AS sold_last_month
                FROM sales_history
                WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
                GROUP BY product_id
            ) s ON p.ID = s.product_id
            WHERE p.ID = %s
            """
            self.cursor.execute(query_price, (self.dynamic_price.min_days_left, self.dynamic_price.min_price_ratio, self.dynamic_price.min_price_ratio, self.dynamic_price.min_days_left, product_id))
            result = self.cursor.fetchone()
            if not result or result[1] is None:
                print(f"Dynamic price not found for product {product_id}. Skipping.")
                continue
            dynamic_price = float(result[1])
            try:
                quantity = int(input("Enter the quantity of this purchased product | ").strip())
                if quantity <= 0 or quantity > available_qty:
                    print(f"Invalid quantity. Available: {available_qty}. Skipping.")
                    continue
            except ValueError:
                print(f"Invalid quantity input. Available: {available_qty}. Skipping.")
                continue
            self.cursor.execute("INSERT INTO sales_history (product_id, quantity, sale_date) VALUES (%s, %s, %s)", (product_id, quantity, date.today()))
            self.cursor.execute("UPDATE product_database SET QUANTITY = QUANTITY - %s, ITEMS_SOLD = ITEMS_SOLD + %s WHERE ID = %s", (quantity, quantity, product_id))
            self.db.commit()
            line_total = dynamic_price * quantity
            total_price += line_total
            product_ids.append(product_id)
            quantities.append(quantity)
            line_totals.append(line_total)
        if not product_ids:
            print("No products purchased.")
            return
        print("\n%-15s%-20s%-15s%-10s%-10s%-10s" % ('ID', 'NAME', 'BRAND', 'RATE', 'QUANTITY', 'AMOUNT'))
        if product_ids:
            format_strings = ','.join(['%s'] * len(product_ids))
            self.cursor.execute(f"SELECT ID, NAME, BRAND, SELLING_PRICE FROM product_database WHERE ID IN ({format_strings})", tuple(product_ids))
        format_strings = ','.join(['%s'] * len(product_ids))
        self.cursor.execute(f"SELECT ID, NAME, BRAND, SELLING_PRICE FROM product_database WHERE ID IN ({format_strings})", tuple(product_ids))
        product_info = {str(row[0]): row for row in self.cursor.fetchall()}
        for pid, qty, amt in zip(product_ids, quantities, line_totals):
            product = product_info[str(pid)]
            rate = float(product[3]) if product[3] is not None else 0.0
            print("%-15s%-20s%-15s%-10s%-10s%-10s" % (product[0], product[1], product[2], rate, qty, amt))
        print(f"\nTotal amount to be paid: {total_price:.2f}\n")
        purchase_record = ''.join([
            f"{sanitize(pid)} {sanitize(product_info[str(pid)][1])} {sanitize(product_info[str(pid)][3])} {sanitize(qty)} {sanitize(amt)}|"
            for pid, qty, amt in zip(product_ids, quantities, line_totals)
        ])
        self.cursor.execute("SELECT PURCHASES FROM customer_database WHERE CONTACT_NUMBER = %s", (customer_contact,))
        row = self.cursor.fetchone()
        existing_purchases = row[0] if row and row[0] else ''
        separator = '\n' if existing_purchases else ''
        updated_purchases = existing_purchases + separator + purchase_record
        self.cursor.execute("UPDATE customer_database SET PURCHASES = %s WHERE CONTACT_NUMBER = %s", (updated_purchases, customer_contact))
        self.db.commit()
        print("Purchase recorded successfully.\n")

    def search_product(self):
        search_term = input("Enter product name or brand to search: ").strip()
        if not search_term:
            print("Search term cannot be empty.")
            return
        query = """
            SELECT ID, NAME, MRP, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE
            FROM product_database
            WHERE NAME LIKE %s OR BRAND LIKE %s
        """
        like_term = f"%{search_term}%"
        self.cursor.execute(query, (like_term, like_term))
        results = self.cursor.fetchall()
        if not results:
            print("No products found matching your search.")
            return
        headers = f"{'ID':<10}{'NAME':<20}{'MRP':<10}{'SELLING_PRICE':<15}{'COST_PRICE':<15}{'BRAND':<15}{'QUANTITY':<10}{'ITEMS_SOLD':<12}{'EXPIRY_DATE':<12}"
        print(headers)
        for row in results:
            displayed = [str(col) if col is not None else "N/A" for col in row]
            print(f"{displayed[0]:<10}{displayed[1]:<20}{displayed[2]:<10}{displayed[3]:<15}{displayed[4]:<15}{displayed[5]:<15}{displayed[6]:<10}{displayed[7]:<12}{displayed[8]:<12}")
