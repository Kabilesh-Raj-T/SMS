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
        # 1. Handle Customer (only contact number required)
        customer_contact = input("Customer contact number (10 digits): ").strip()
        self.cursor.execute(
            "SELECT ID, CONTACT_NUMBER, PURCHASES FROM customer_database WHERE CONTACT_NUMBER = %s",
            (customer_contact,),
        )
        customer_data = self.cursor.fetchone()

        if not customer_data:
            print("This is a new customer. Adding with contact only.")
            # Auto-generate ID = max(ID)+1
            self.cursor.execute("SELECT COALESCE(MAX(ID), 0) + 1 FROM customer_database")
            new_id = self.cursor.fetchone()[0]

            self.cursor.execute(
                "INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, GENDER, PURCHASES) "
                "VALUES (%s, %s, %s, %s, %s)",
                (new_id, None, customer_contact, None, 0),
            )
            self.db.commit()

            customer_data = (new_id, customer_contact, 0.0)

        customer_id, _, current_total_spent = customer_data
        current_total_spent = float(current_total_spent or 0.0)

        # 2. Collect items one by one with immediate stock check
        invoice_items = []
        product_update_data = []
        total_price = 0.0

        while True:
            product_id = input("Enter Product ID to purchase (or leave blank to finish) | ").strip()
            if not product_id:
                break

            # Get product info
            self.cursor.execute(
                "SELECT ID, NAME, BRAND, QUANTITY FROM product_database WHERE ID = %s", (product_id,)
            )
            product = self.cursor.fetchone()

            if not product:
                print(f"❌ Product ID {product_id} not found. Try again.")
                continue

            _, name, brand, available_qty = product

            try:
                quantity = int(input(f"Enter quantity for {name} (Available: {available_qty}) | ").strip())
            except ValueError:
                print("❌ Invalid quantity. Skipping.")
                continue

            if quantity <= 0:
                print("❌ Quantity must be positive. Skipping.")
                continue

            if quantity > available_qty:
                print(f"⚠️ Not enough stock for {name}. Requested: {quantity}, Available: {available_qty}.")
                continue

            # Get dynamic price
            dynamic_price = self.dynamic_price.get_dynamic_price(product_id)
            if dynamic_price is None:
                print(f"❌ Could not retrieve price for {name}. Skipping.")
                continue

            line_total = dynamic_price * quantity
            total_price += line_total

            # Collect info
            invoice_items.append(
                {"id": product_id, "name": name, "brand": brand, "rate": dynamic_price,
                "qty": quantity, "amount": line_total}
            )
            product_update_data.append((quantity, quantity, product_id))

        if not invoice_items:
            print("No valid products entered for purchase.")
            return

        # 3. Execute DB updates
        try:
            # Update stock
            self.cursor.executemany(
                "UPDATE product_database SET QUANTITY = QUANTITY - %s, ITEMS_SOLD = ITEMS_SOLD + %s WHERE ID = %s",
                product_update_data,
            )

            # Update customer’s total spent (cumulative add)
            self.cursor.execute(
                "UPDATE customer_database SET PURCHASES = PURCHASES + %s WHERE CONTACT_NUMBER = %s",
                (total_price, customer_contact),
            )

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"❌ An error occurred during database update: {e}. Purchase cancelled.")
            return

        # 4. Print Invoice
        print("\n--- INVOICE ---")
        print(f"{'ID':<5}{'NAME':<20}{'BRAND':<15}{'RATE':<10}{'QTY':<10}{'AMOUNT':<10}")
        for item in invoice_items:
            print(f"{item['id']:<5}{item['name']:<20}{item['brand']:<15}{item['rate']:<10.2f}{item['qty']:<10}{item['amount']:<10.2f}")

        print(f"\nTotal amount to be paid: {total_price:.2f}\n")
        print("✅ Purchase recorded successfully.\n")

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