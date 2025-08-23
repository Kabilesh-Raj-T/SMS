# product.py

from datetime import date, datetime

def sanitize(value):
    """Convert value to string and strip whitespace."""
    return str(value).strip() if value is not None else ""

class ProductManager:
    def __init__(self, db, dynamic_price, customer_mgr):
        self.db = db
        self.cursor = db.cursor()
        self.dynamic_price = dynamic_price
        self.customer_mgr = customer_mgr # Needed for adding customers during purchase

    def view_all(self):
        headers = f"{'ID':<10}{'NAME':<20}{'MRP':<10}{'SELLING_PRICE':<15}{'COST_PRICE':<15}{'BRAND':<15}{'QUANTITY':<10}{'ITEMS_SOLD':<12}{'EXPIRY_DATE':<12}"
        print(headers)
        self.cursor.execute("SELECT ID, NAME, MRP, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE FROM product_database ORDER BY CAST(ID AS UNSIGNED)")
        for row in self.cursor.fetchall():
            displayed = [str(col) if col is not None else "N/A" for col in row]
            print(f"{displayed[0]:<10}{displayed[1]:<20}{displayed[2]:<10}{displayed[3]:<15}{displayed[4]:<15}{displayed[5]:<15}{displayed[6]:<10}{displayed[7]:<12}{displayed[8]:<12}")

    def add_product(self, product=None):
        """
        Add a product. If 'product' is None, prompt interactively. Otherwise, expects a tuple:
        (ID, NAME, MRP, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE)
        """
        try:
            if product is None:
                product_id = sanitize(input("Product ID         | "))
                name = sanitize(input("Product Name       | "))
                mrp = float(sanitize(input("MRP                | ")))
                cost_price = float(sanitize(input("Cost Price         | ")))
                brand = sanitize(input("Brand              | "))
                quantity = int(sanitize(input("Quantity           | ")))
                items_sold = int(sanitize(input("Items Sold         | ")))
                expiry_date_str = sanitize(input("Expiry Date (YYYY-MM-DD)| "))
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date() if expiry_date_str else None
            else:
                # Accept tuple or list from menu.collect_product_data()
                product_id, name, mrp, cost_price, brand, quantity, items_sold, expiry_date = product
                product_id = sanitize(product_id)
                name = sanitize(name)
                mrp = float(mrp)
                cost_price = float(cost_price)
                brand = sanitize(brand)
                quantity = int(quantity)
                items_sold = int(items_sold)
                if expiry_date:
                    if isinstance(expiry_date, str):
                        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                else:
                    expiry_date = None

            # Check if product already exists
            self.cursor.execute("SELECT ID FROM product_database WHERE ID = %s", (product_id,))
            if self.cursor.fetchone():
                print(f"Product with ID {product_id} already exists.")
                return

            # Set initial selling price to MRP, will be updated by dynamic price
            initial_selling_price = mrp

            query = """INSERT INTO product_database
            (ID, NAME, MRP, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD, EXPIRY_DATE, SELLING_PRICE)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            product_data = (product_id, name, mrp, cost_price, brand, quantity, items_sold, expiry_date, initial_selling_price)
            self.cursor.execute(query, product_data)
            self.db.commit()
            print("Product added successfully.")

            # Now, calculate and set the dynamic price
            self.update_single_product_price(product_id)

        except ValueError:
            print("Invalid input. Please check data types (e.g., numbers for prices/quantities).")
        except Exception as e:
            print(f"An error occurred: {e}")


    def update_single_product_price(self, product_id):
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
        self.cursor.execute("SELECT * FROM product_database WHERE ID = %s", (product_id,))
        product = self.cursor.fetchone()
        if not product:
            print("There is no product with this ID.")
            return

        print(f"\nEditing Product ID: {product[0]}, Name: {product[1]}")
        field_map = {
            'name': ('NAME', str), 'mrp': ('MRP', float), 'cost price': ('COST_PRICE', float),
            'brand': ('BRAND', str), 'quantity': ('QUANTITY', int),
            'items sold': ('ITEMS_SOLD', int), 'expiry date': ('EXPIRY_DATE', str)
        }
        print(f"Editable fields: {', '.join(field_map.keys())}")
        field = input("Enter the field to be edited             | ").strip().lower()

        if field not in field_map:
            print("Invalid field name.")
            return

        value_str = input(f"Enter the new value for {field}          | ").strip()
        field_db, type_cast = field_map[field]

        try:
            value_cast = type_cast(value_str)
        except ValueError:
            print(f"Invalid value. Please enter a valid {type_cast.__name__}.")
            return

        update_query = f"UPDATE product_database SET {field_db} = %s WHERE ID = %s"
        self.cursor.execute(update_query, (value_cast, product_id))
        self.db.commit()
        print("Product updated successfully.")

        # Recalculate dynamic price after any relevant change
        self.update_single_product_price(product_id)

    def delete_product(self):
        product_id = input("Enter the Product ID to be deleted : ").strip()
        self.cursor.execute("DELETE FROM product_database WHERE ID = %s", (product_id,))
        if self.cursor.rowcount > 0:
            self.db.commit()
            print("Product Deleted Successfully.")
        else:
            print("No product with this ID found.")

    def make_purchase(self):
        customer_contact = input("Customer contact number (10 digits): ").strip()
        self.cursor.execute("SELECT CONTACT_NUMBER FROM customer_database WHERE CONTACT_NUMBER = %s", (customer_contact,))
        if not self.cursor.fetchone():
            print("This is a new customer. Adding with contact only.")
            self.cursor.execute("INSERT INTO customer_database (CONTACT_NUMBER) VALUES (%s)", (customer_contact,))
            self.db.commit()

        product_ids, quantities, line_totals, prices = [], [], [], []
        total_price = 0.0

        while True:
            product_id = input("Enter Product ID to purchase (or leave blank to finish) | ").strip()
            if not product_id:
                break

            self.cursor.execute("SELECT QUANTITY FROM product_database WHERE ID = %s", (product_id,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Product ID {product_id} not found. Skipping.")
                continue

            available_qty = result[0]
            if available_qty <= 0:
                print(f"Product {product_id} is out of stock. Skipping.")
                continue

            try:
                quantity = int(input(f"Enter quantity (Available: {available_qty}) | ").strip())
                if not (0 < quantity <= available_qty):
                    print(f"Invalid quantity. Please enter a number between 1 and {available_qty}. Skipping.")
                    continue
            except ValueError:
                print("Invalid quantity input. Skipping.")
                continue

            # Use the dynamic price module instead of duplicating the query
            dynamic_price = self.dynamic_price.get_dynamic_price(product_id)
            if dynamic_price is None:
                print(f"Could not retrieve price for product {product_id}. Skipping.")
                continue

            # Record sale in history for dynamic pricing later
            self.cursor.execute("INSERT INTO sales_history (product_id, quantity, sale_date) VALUES (%s, %s, %s)", (product_id, quantity, date.today()))
            # Update inventory
            self.cursor.execute("UPDATE product_database SET QUANTITY = QUANTITY - %s, ITEMS_SOLD = ITEMS_SOLD + %s WHERE ID = %s", (quantity, quantity, product_id))

            line_total = dynamic_price * quantity
            total_price += line_total
            product_ids.append(product_id)
            quantities.append(quantity)
            prices.append(dynamic_price)
            line_totals.append(line_total)

        if not product_ids:
            print("No products purchased.")
            self.db.commit() # Commit any sales history changes even if purchase is empty
            return

        print("\n--- INVOICE ---")
        print(f"{'ID':<15}{'NAME':<20}{'BRAND':<15}{'RATE':<10}{'QUANTITY':<10}{'AMOUNT':<10}")
        if product_ids:
            format_strings = ','.join(['%s'] * len(product_ids))
            self.cursor.execute(f"SELECT ID, NAME, BRAND FROM product_database WHERE ID IN ({format_strings})", tuple(product_ids))
            product_info = {str(row[0]): row for row in self.cursor.fetchall()}
            for pid, qty, rate, amt in zip(product_ids, quantities, prices, line_totals):
                product = product_info.get(str(pid), ('N/A', 'N/A', 'N/A'))
                print(f"{product[0]:<15}{product[1]:<20}{product[2]:<15}{rate:<10.2f}{qty:<10}{amt:<10.2f}")

        print(f"\nTotal amount to be paid: {total_price:.2f}\n")
        # NOTE: Saving purchase history to the customer table is not ideal.
        # This is kept to match the original structure, but a separate 'sales' table is recommended.
        purchase_record_items = [
            f"{sanitize(pid)} {sanitize(product_info.get(str(pid), ['','N/A'])[1])} {sanitize(rate)} {sanitize(qty)} {sanitize(amt)}"
            for pid, qty, rate, amt in zip(product_ids, quantities, prices, line_totals)
        ]
        purchase_record = '|'.join(purchase_record_items)

        self.cursor.execute("UPDATE customer_database SET PURCHASES = CONCAT_WS('\\n', PURCHASES, %s) WHERE CONTACT_NUMBER = %s", (purchase_record, customer_contact))
        self.db.commit()
        print("Purchase recorded successfully.\n")

    def search_product(self):
        search_term = input("Enter product ID to search: ").strip()
        if not search_term:
            print("Search term cannot be empty.")
            return

        query = "SELECT * FROM product_database WHERE ID = %s"
        self.cursor.execute(query, (search_term,))
        results = self.cursor.fetchall()

        if not results:
            print("No products found matching your search.")
            return

        headers = f"{'ID':<10}{'NAME':<20}{'MRP':<10}{'SELLING_PRICE':<15}{'COST_PRICE':<15}{'BRAND':<15}{'QUANTITY':<10}{'ITEMS_SOLD':<12}{'EXPIRY_DATE':<12}"
        print(headers)
        for row in results:
            displayed = [str(col) if col is not None else "N/A" for col in row]
            print(f"{displayed[0]:<10}{displayed[1]:<20}{displayed[2]:<10}{displayed[3]:<15}{displayed[4]:<15}{displayed[5]:<15}{displayed[6]:<10}{displayed[7]:<12}{displayed[8]:<12}")