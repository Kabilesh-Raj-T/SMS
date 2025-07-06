import mysql.connector
from flask import g

# Database Configuration (centralized, could be from app.config)
# For simplicity, keeping it here, but ideally, Flask app config would be the source.
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWD = "Kabilesh1!" # Consider environment variables for sensitive data
DB_NAME = "sms_database"

def get_db_connection():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db_conn' not in g:
        g.db_conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWD,
            database=DB_NAME
        )
    return g.db_conn

def close_db_connection(error=None):
    """Closes the database connection at the end of the request."""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

def init_app(app):
    """Register database functions with the Flask app. This is called by the application factory."""
    app.teardown_appcontext(close_db_connection)

# The old Database class is refactored into connection management functions (get_db_connection, close_db_connection)
# and direct cursor usage within manager methods.

# Manager classes will be moved here and adapted.
# For now, this file sets up the database connection helpers.

class ProductManager:
    def __init__(self):
        # Manager classes will now get the db connection from Flask's g object
        # or have it passed if that pattern is preferred.
        # For simplicity, methods will call get_db_connection() directly.
        pass

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, is_commit=False):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) # Using dictionary=True for easier JSON conversion
        try:
            cursor.execute(query, params or ())
            if is_commit:
                conn.commit()
                return cursor.rowcount # Return affected rows for CUD operations

            if fetch_one:
                result = cursor.fetchone()
                return result
            elif fetch_all:
                result = cursor.fetchall()
                return result
            return cursor # Should not happen if fetch_one/all or is_commit is true
        finally:
            cursor.close() # Ensure cursor is closed after operation

    def view_all(self):
        """Retrieves all products from the database."""
        query = "SELECT ID, NAME, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD FROM product_database"
        # Using dictionary=True in _execute_query will make products a list of dicts
        products = self._execute_query(query, fetch_all=True)
        return products if products else []

    def add_product(self, product_data):
        """Adds a new product to the database.
        product_data is a dictionary like:
        {
            "ID": "P101", "NAME": "New Laptop", "SELLING_PRICE": 1200.00, "COST_PRICE": 800.00,
            "BRAND": "TechCo", "QUANTITY": 50, "ITEMS_SOLD": 0
        }
        """
        required_fields = ['ID', 'NAME', 'SELLING_PRICE', 'COST_PRICE', 'BRAND', 'QUANTITY', 'ITEMS_SOLD']
        if not all(field in product_data and product_data[field] is not None for field in required_fields):
            # Basic validation for presence of fields
            missing_fields = [field for field in required_fields if field not in product_data or product_data[field] is None]
            return {"error": f"Missing or null required fields: {', '.join(missing_fields)}"}, 400


        # Check if product ID already exists
        if self.get_product_by_id(product_data['ID']):
            return {"error": f"Product with ID {product_data['ID']} already exists."}, 409 # Conflict

        query = """INSERT INTO product_database
                   (ID, NAME, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        params = (
            product_data['ID'], product_data['NAME'], float(product_data['SELLING_PRICE']),
            float(product_data['COST_PRICE']), product_data['BRAND'], int(product_data['QUANTITY']),
            int(product_data['ITEMS_SOLD'])
        )

        try:
            rowcount = self._execute_query(query, params, is_commit=True)
            if rowcount > 0:
                return {"message": "Product added successfully.", "product_id": product_data['ID']}, 201 # Created
            else:
                # This case should ideally not be reached if DB constraints are well-defined
                # and ID uniqueness is checked beforehand.
                return {"error": "Failed to add product, no rows affected."}, 500
        except mysql.connector.Error as err:
            # Specific database errors can be caught here if needed
            return {"error": f"Database error: {err}"}, 500


    def get_product_by_id(self, product_id):
        """Retrieves a single product by its ID."""
        query = "SELECT ID, NAME, SELLING_PRICE, COST_PRICE, BRAND, QUANTITY, ITEMS_SOLD FROM product_database WHERE ID = %s"
        product = self._execute_query(query, (product_id,), fetch_one=True)
        return product # Returns dict or None

    def edit_product(self, product_id, update_data):
        """Edits a product's details.
        product_id: The ID of the product to edit.
        update_data: A dictionary containing fields to update, e.g., {"NAME": "New Name", "SELLING_PRICE": 1250.00}
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return {"error": "Product not found."}, 404

        field_map = {
            'name': 'NAME',
            'selling_price': 'SELLING_PRICE',
            'cost_price': 'COST_PRICE',
            'brand': 'BRAND',
            'quantity': 'QUANTITY',
            'items_sold': 'ITEMS_SOLD',
            # 'id': 'ID' # Generally, changing PKs is discouraged. If allowed, needs careful handling.
        }

        update_fields = []
        params = []

        for key, value in update_data.items():
            db_field = field_map.get(key.lower())
            if db_field:
                update_fields.append(f"{db_field} = %s")
                # Apply type conversion based on expected field type
                if db_field in ['SELLING_PRICE', 'COST_PRICE']:
                    params.append(float(value))
                elif db_field in ['QUANTITY', 'ITEMS_SOLD']:
                    params.append(int(value))
                else:
                    params.append(value)
            # else:
                # Optionally, log or return an error for unrecognized fields in update_data
                # return {"error": f"Invalid field '{key}' for product update."}, 400


        if not update_fields:
            return {"error": "No valid fields provided for update."}, 400

        params.append(product_id) # For the WHERE clause

        query = f"UPDATE product_database SET {', '.join(update_fields)} WHERE ID = %s"

        try:
            rowcount = self._execute_query(query, tuple(params), is_commit=True)
            if rowcount > 0:
                updated_product = self.get_product_by_id(product_id)
                return {"message": "Product updated successfully.", "product": updated_product}, 200
            else:
                # This might happen if the new values are the same as the old ones
                # or if the product_id was valid but somehow the update failed at DB level (rare)
                # For consistency, we can return the current state of the product.
                current_product = self.get_product_by_id(product_id)
                return {"message": "Product update did not change any data, or no rows affected.", "product": current_product}, 200
        except mysql.connector.Error as err:
            return {"error": f"Database error during update: {err}"}, 500


    def delete_product(self, product_id):
        """Deletes a product by its ID."""
        product = self.get_product_by_id(product_id)
        if not product:
            return {"error": "Product not found."}, 404

        query = "DELETE FROM product_database WHERE ID = %s"
        try:
            rowcount = self._execute_query(query, (product_id,), is_commit=True)
            if rowcount > 0:
                return {"message": "Product deleted successfully.", "product_id": product_id}, 200 # Or 204 No Content
            else:
                # This should ideally not happen if the existence check passed.
                return {"error": "Failed to delete product, no rows affected."}, 500
        except mysql.connector.Error as err:
            # Handle potential foreign key constraints if products are referenced elsewhere
            return {"error": f"Database error during deletion: {err}"}, 500

    def make_purchase(self, customer_contact, purchase_items, customer_name_if_new=None):
        """
        Records a purchase, updating product quantities and customer purchase history.
        customer_contact: string
        purchase_items: list of dictionaries, each with {'product_id': id, 'quantity': qty}
        customer_name_if_new: string, required if customer_contact doesn't exist.
        """
        conn = get_db_connection()
        # Start a transaction
        # Note: mysql.connector does not support context managers for transactions directly on connection.
        # We need to explicitly call commit or rollback.
        # _execute_query handles cursor creation and closing, but transaction is managed here.

        try:
            # Check customer existence
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT ID, CONTACT_NUMBER, PURCHASES FROM customer_database WHERE CONTACT_NUMBER = %s", (customer_contact,))
            customer = cursor.fetchone()

            customer_id = None
            is_new_customer = False

            if customer:
                customer_id = customer['ID']
                existing_purchases_str = customer['PURCHASES'] or ''
            else:
                is_new_customer = True
                if not customer_name_if_new:
                    # This check should ideally be in the route handler before calling this.
                    return {"error": "Customer name is required for new customers."}, 400

                cursor.execute("SELECT MAX(ID) as max_id FROM customer_database")
                max_id_row = cursor.fetchone()
                customer_id = (max_id_row['max_id'] or 0) + 1
                existing_purchases_str = ''

                # Insert new customer - simplified, assumes other fields like GENDER, EMAIL are optional or handled elsewhere
                # The original script's add_customer is more comprehensive.
                # For a purchase, we might only need minimal info for the customer record.
                # Other customer details could be added/updated via a separate customer endpoint.
                insert_customer_query = """
                    INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, PURCHASES)
                    VALUES (%s, %s, %s, %s)
                """
                # Initial purchase string is empty, will be updated later
                cursor.execute(insert_customer_query, (customer_id, customer_name_if_new, customer_contact, ''))

            # Process items
            total_purchase_price = 0.0
            purchase_details_for_receipt = [] # For constructing the purchase record string

            for item in purchase_items:
                product_id = item['product_id']
                quantity_purchased = int(item['quantity'])

                if quantity_purchased <= 0:
                    conn.rollback()
                    return {"error": f"Quantity for product ID {product_id} must be positive."}, 400

                # Lock product row for update to prevent race conditions on quantity
                cursor.execute("SELECT ID, NAME, SELLING_PRICE, QUANTITY FROM product_database WHERE ID = %s FOR UPDATE", (product_id,))
                product = cursor.fetchone()

                if not product:
                    conn.rollback()
                    return {"error": f"Product with ID {product_id} not found."}, 404

                if product['QUANTITY'] < quantity_purchased:
                    conn.rollback()
                    return {"error": f"Not enough stock for product {product['NAME']} (ID: {product_id}). Available: {product['QUANTITY']}"}, 400

                # Update product stock and items sold
                cursor.execute("UPDATE product_database SET QUANTITY = QUANTITY - %s, ITEMS_SOLD = ITEMS_SOLD + %s WHERE ID = %s",
                               (quantity_purchased, quantity_purchased, product_id))

                line_total = product['SELLING_PRICE'] * quantity_purchased
                total_purchase_price += line_total

                purchase_details_for_receipt.append(
                    f"{product['ID']} {product['NAME']} {product['SELLING_PRICE']} {quantity_purchased} {line_total}"
                )

            # Construct the purchase record string for the customer
            current_purchase_record_str = "|".join(purchase_details_for_receipt) + f"|{total_purchase_price}|"

            # Prepend new purchase to existing ones
            updated_purchases_str = current_purchase_record_str + existing_purchases_str

            cursor.execute("UPDATE customer_database SET PURCHASES = %s WHERE ID = %s", (updated_purchases_str, customer_id))

            conn.commit()
            return {
                "message": "Purchase recorded successfully.",
                "customer_id": customer_id,
                "total_price": total_purchase_price,
                "items_purchased": purchase_details_for_receipt # Or a more structured list of items
            }, 200

        except mysql.connector.Error as err:
            conn.rollback()
            return {"error": f"Database transaction failed: {err}"}, 500
        except Exception as e: # Catch any other unexpected errors
            conn.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def search_product_by_id_manager(self, product_id): # Renamed to avoid conflict with get_product_by_id
        """Searches for a product by ID and returns its details.
           This mirrors the original search_product functionality.
        """
        # The original search_product checked if ID exists in a list of all IDs.
        # self.get_product_by_id already does this more efficiently.
        product = self.get_product_by_id(product_id)
        if product:
            # Original script selected specific fields, get_product_by_id returns all needed ones.
            # Format is already a dictionary due to dictionary=True cursor.
            return product, 200
        else:
            return {"error": "Product not found."}, 404

    # get_product_name and get_price are helper methods used by the original make_purchase.
    # The refactored make_purchase fetches these details directly.
    # If they are needed for other API endpoints, they can be exposed.
    # For now, they are effectively inlined into make_purchase.
    # def get_product_name(self, product_id):
    #     query = "SELECT NAME FROM product_database WHERE ID = %s"
    #     result = self._execute_query(query, (product_id,), fetch_one=True)
    #     return result['NAME'] if result else None

    # def get_price(self, product_id):
    #     query = "SELECT SELLING_PRICE FROM product_database WHERE ID = %s"
    #     result = self._execute_query(query, (product_id,), fetch_one=True)
    #     return result['SELLING_PRICE'] if result else None


class CustomerManager:
    def __init__(self):
        pass

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, is_commit=False):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) # Ensure dictionary cursor for consistent output
        try:
            cursor.execute(query, params or ())
            if is_commit:
                conn.commit()
                return cursor.rowcount

            if fetch_one:
                result = cursor.fetchone()
                return result
            elif fetch_all:
                result = cursor.fetchall()
                return result
            # This path should ideally not be taken if one of the above flags is True
            return cursor # Or raise an error if no operation type is specified
        finally:
            cursor.close()

    def view_all_customers(self):
        """Retrieves all customers and their purchase histories."""
        query = "SELECT ID, NAME, CONTACT_NUMBER, GENDER, EMAIL, PURCHASES FROM customer_database"
        customers = self._execute_query(query, fetch_all=True)
        if not customers:
            return []

        # Process purchases string into a more structured list
        for customer in customers:
            if customer.get('PURCHASES'):
                # The original format was: "pid name price qty amt|pid name price qty amt|total|"
                # We need to parse this. A simple split by '|' might be too naive if names/etc contain '|'.
                # Assuming simple split for now, but this might need a more robust parsing if data is complex.
                # Or better, store purchases in a related table or as JSON in DB.
                # For now, let's keep it as a list of strings.
                customer['PURCHASES_LIST'] = [p for p in customer['PURCHASES'].split('|') if p]
            else:
                customer['PURCHASES_LIST'] = []
        return customers

    def get_customer_by_id(self, customer_id):
        """Retrieves a single customer by ID."""
        query = "SELECT ID, NAME, CONTACT_NUMBER, GENDER, EMAIL, PURCHASES FROM customer_database WHERE ID = %s"
        customer = self._execute_query(query, (customer_id,), fetch_one=True)
        if customer and customer.get('PURCHASES'):
             customer['PURCHASES_LIST'] = [p for p in customer['PURCHASES'].split('|') if p]
        elif customer:
            customer['PURCHASES_LIST'] = []
        return customer

    def add_customer(self, customer_data):
        """Adds a new customer.
        customer_data: dict with ID, NAME, CONTACT_NUMBER, GENDER, EMAIL. PURCHASES is init as empty.
        """
        required_fields = ['ID', 'NAME', 'CONTACT_NUMBER'] # GENDER, EMAIL are optional based on original
        if not all(field in customer_data for field in required_fields):
            return {"error": "Missing required fields (ID, NAME, CONTACT_NUMBER)."}, 400

        if self.get_customer_by_id(customer_data['ID']):
            return {"error": f"Customer with ID {customer_data['ID']} already exists."}, 409

        query = """INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, GENDER, EMAIL, PURCHASES)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        params = (
            customer_data['ID'],
            customer_data['NAME'],
            customer_data['CONTACT_NUMBER'],
            customer_data.get('GENDER'), # Use .get for optional fields
            customer_data.get('EMAIL'),
            "" # Initialize purchases as empty string or NULL
        )
        try:
            rowcount = self._execute_query(query, params, is_commit=True)
            if rowcount > 0:
                return {"message": "Customer added successfully.", "customer_id": customer_data['ID']}, 201
            else:
                return {"error": "Failed to add customer."}, 500
        except mysql.connector.Error as err:
            return {"error": f"Database error: {err}"}, 500

    def edit_customer(self, customer_id, update_data):
        """Edits customer details.
        update_data: dict of fields to change.
        """
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return {"error": "Customer not found."}, 404

        field_map = {
            'name': 'NAME',
            'contact_number': 'CONTACT_NUMBER',
            'gender': 'GENDER',
            'email': 'EMAIL',
            # 'id': 'ID' # Changing ID is generally not recommended.
            # 'purchases': 'PURCHASES' # Purchases are usually managed by make_purchase.
        }

        update_fields = []
        params = []

        for key, value in update_data.items():
            db_field = field_map.get(key.lower())
            if db_field:
                update_fields.append(f"{db_field} = %s")
                params.append(value)
            # else:
                # return {"error": f"Invalid field '{key}' for customer update."}, 400


        if not update_fields:
            return {"error": "No valid fields provided for update."}, 400

        params.append(customer_id) # For the WHERE clause
        query = f"UPDATE customer_database SET {', '.join(update_fields)} WHERE ID = %s"

        try:
            rowcount = self._execute_query(query, tuple(params), is_commit=True)
            if rowcount > 0:
                updated_customer = self.get_customer_by_id(customer_id)
                return {"message": "Customer updated successfully.", "customer": updated_customer}, 200
            else:
                current_customer = self.get_customer_by_id(customer_id)
                return {"message": "Customer update did not change any data or failed.", "customer": current_customer}, 200
        except mysql.connector.Error as err:
            return {"error": f"Database error: {err}"}, 500

    def delete_customer(self, customer_id):
        """Deletes a customer by ID."""
        if not self.get_customer_by_id(customer_id):
            return {"error": "Customer not found."}, 404

        query = "DELETE FROM customer_database WHERE ID = %s"
        try:
            rowcount = self._execute_query(query, (customer_id,), is_commit=True)
            if rowcount > 0:
                return {"message": "Customer deleted successfully.", "customer_id": customer_id}, 200
            else:
                return {"error": "Failed to delete customer."}, 500
        except mysql.connector.Error as err:
            # Consider if there are related records that might prevent deletion (e.g. sales orders)
            # The current schema stores purchases as a string, so direct FKs might not be an issue here.
            return {"error": f"Database error: {err}"}, 500

    def search_customer_by_id_manager(self, customer_id): # Renamed for clarity
        """Searches for a customer by ID."""
        customer = self.get_customer_by_id(customer_id)
        if customer:
            # PURCHASES_LIST is already added by get_customer_by_id
            return customer, 200
        else:
            return {"error": "Customer not found."}, 404


class EmployeeManager:
    def __init__(self):
        pass

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, is_commit=False):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if is_commit:
                conn.commit()
                return cursor.rowcount

            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return cursor # Should generally not be reached if flags are used properly
        finally:
            cursor.close()

    def view_all_employees(self):
        """Retrieves all employees."""
        query = "SELECT ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY FROM employee_database"
        employees = self._execute_query(query, fetch_all=True)
        return employees if employees else []

    def get_employee_by_id(self, emp_id):
        """Retrieves a single employee by ID."""
        query = "SELECT ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY FROM employee_database WHERE ID = %s"
        employee = self._execute_query(query, (emp_id,), fetch_one=True)
        return employee

    def add_employee(self, emp_data):
        """Adds a new employee.
        emp_data: dict with ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY.
        """
        required_fields = ['ID', 'NAME', 'CONTACT_NUMBER', 'GENDER', 'POSITION', 'SALARY']
        if not all(field in emp_data and emp_data[field] is not None for field in required_fields):
            missing = [f for f in required_fields if f not in emp_data or emp_data[f] is None]
            return {"error": f"Missing or null required fields: {', '.join(missing)}"}, 400

        if self.get_employee_by_id(emp_data['ID']):
            return {"error": f"Employee with ID {emp_data['ID']} already exists."}, 409

        query = """
        INSERT INTO employee_database (ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            emp_data['ID'], emp_data['NAME'], emp_data['CONTACT_NUMBER'],
            emp_data['GENDER'], emp_data['POSITION'], emp_data['SALARY']
        )
        try:
            rowcount = self._execute_query(query, params, is_commit=True)
            if rowcount > 0:
                return {"message": "Employee added successfully.", "employee_id": emp_data['ID']}, 201
            else:
                return {"error": "Failed to add employee."}, 500
        except mysql.connector.Error as err:
            return {"error": f"Database error: {err}"}, 500

    def edit_employee(self, emp_id, update_data):
        """Edits employee details.
        update_data: dict of fields to change.
        """
        employee = self.get_employee_by_id(emp_id)
        if not employee:
            return {"error": "Employee not found."}, 404

        field_map = {
            'name': 'NAME',
            'contact_number': 'CONTACT_NUMBER',
            'gender': 'GENDER',
            'position': 'POSITION',
            'salary': 'SALARY',
            # 'id': 'ID' # Changing ID usually not done via generic edit.
        }

        update_fields = []
        params = []

        for key, value in update_data.items():
            db_field = field_map.get(key.lower())
            if db_field:
                update_fields.append(f"{db_field} = %s")
                params.append(value)
            # else:
                # return {"error": f"Invalid field '{key}' for employee update."}, 400

        if not update_fields:
            return {"error": "No valid fields provided for update."}, 400

        params.append(emp_id) # For the WHERE ID = %s
        query = f"UPDATE employee_database SET {', '.join(update_fields)} WHERE ID = %s"

        try:
            rowcount = self._execute_query(query, tuple(params), is_commit=True)
            if rowcount > 0:
                updated_employee = self.get_employee_by_id(emp_id) # Fetch the updated record
                return {"message": "Employee updated successfully.", "employee": updated_employee}, 200
            else:
                # If no rows affected, could mean data was same or ID not found (though checked)
                current_employee = self.get_employee_by_id(emp_id)
                return {"message": "Employee update did not change any data or failed.", "employee": current_employee}, 200
        except mysql.connector.Error as err:
            return {"error": f"Database error: {err}"}, 500

    def delete_employee(self, emp_id):
        """Deletes an employee by ID."""
        if not self.get_employee_by_id(emp_id):
            return {"error": "Employee not found."}, 404

        query = "DELETE FROM employee_database WHERE ID = %s"
        try:
            rowcount = self._execute_query(query, (emp_id,), is_commit=True)
            if rowcount > 0:
                return {"message": "Employee deleted successfully.", "employee_id": emp_id}, 200
            else:
                return {"error": "Failed to delete employee."}, 500
        except mysql.connector.Error as err:
            return {"error": f"Database error: {err}"}, 500

    def search_employee_by_id_manager(self, emp_id): # Renamed for clarity
        """Searches for an employee by ID."""
        employee = self.get_employee_by_id(emp_id)
        if employee:
            return employee, 200
        else:
            return {"error": "Employee not found."}, 404

class FinanceManager:
    def __init__(self):
        pass

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, is_commit=False):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if is_commit: # Should not be used for finance reads, but kept for helper consistency
                conn.commit()
                return cursor.rowcount

            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return None # Explicitly return None if no fetch type matches
        finally:
            cursor.close()

    def profit_by_product(self):
        """Calculates profit or loss for each product."""
        query = """
            SELECT
                ID, NAME, SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD
            FROM product_database
        """
        products = self._execute_query(query, fetch_all=True)

        if not products:
            return []

        results = []
        for p in products:
            selling_price = p.get('SELLING_PRICE', 0.0) or 0.0
            cost_price = p.get('COST_PRICE', 0.0) or 0.0
            # quantity = p.get('QUANTITY', 0) or 0 # Current stock
            items_sold = p.get('ITEMS_SOLD', 0) or 0

            # Profit calculation in the original script was:
            # revenue = selling_price * items_sold
            # cost = (quantity + items_sold) * cost_price  -- This implies cost of total stock ever held
            # profit_loss = revenue - cost
            # This calculation of 'cost' seems to be based on total units that *were* available,
            # not just the cost of goods sold.
            # Let's calculate Cost of Goods Sold (COGS) for items sold.
            cogs = cost_price * items_sold
            revenue = selling_price * items_sold
            profit_loss = revenue - cogs

            results.append({
                "ID": p['ID'],
                "NAME": p['NAME'],
                "SELLING_PRICE": selling_price,
                "COST_PRICE": cost_price,
                "ITEMS_SOLD": items_sold,
                "REVENUE": revenue,
                "COGS": cogs,
                "PROFIT_LOSS": profit_loss
            })
        return results

    def total_profit_or_loss(self):
        """Calculates the total profit or loss across all products."""
        query = """
            SELECT SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD
            FROM product_database
        """
        products_data = self._execute_query(query, fetch_all=True)

        if not products_data:
            return {"total_profit_loss": 0.0, "status": "neutral"}

        total_overall_profit_loss = 0.0

        for p in products_data:
            selling_price = p.get('SELLING_PRICE', 0.0) or 0.0
            cost_price = p.get('COST_PRICE', 0.0) or 0.0
            # quantity = p.get('QUANTITY', 0) or 0 # Current stock
            items_sold = p.get('ITEMS_SOLD', 0) or 0

            # Using COGS approach for consistency
            revenue_from_product = selling_price * items_sold
            cogs_for_product = cost_price * items_sold
            profit_loss_for_product = revenue_from_product - cogs_for_product
            total_overall_profit_loss += profit_loss_for_product

        status = "profit" if total_overall_profit_loss >= 0 else "loss"
        return {
            "total_profit_loss": round(total_overall_profit_loss, 2),
            "status": status
        }

class StatManager:
    def __init__(self):
        pass

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, is_commit=False):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if is_commit: # Should not be used for stats reads
                conn.commit()
                return cursor.rowcount

            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return None # Explicitly return None if no fetch type matches
        finally:
            cursor.close()

    def best_selling_product(self):
        """Identifies the best-selling product based on ITEMS_SOLD."""
        query = """
            SELECT ID, NAME, ITEMS_SOLD
            FROM product_database
            ORDER BY ITEMS_SOLD DESC
            LIMIT 1
        """
        product = self._execute_query(query, fetch_one=True)
        if product:
            # Ensure ITEMS_SOLD is an int if it's None/null in DB for some reason
            items_sold = product.get('ITEMS_SOLD', 0) or 0
            return {
                "id": product['ID'],
                "name": product['NAME'],
                "items_sold": items_sold
            }
        else:
            return {"message": "No products found or no sales data available."}

    def most_profitable_product(self):
        """Identifies the most profitable product."""
        # This requires fetching all products and calculating profit for each, similar to FinanceManager.profit_by_product
        # but then finding the max.
        query = """
            SELECT ID, NAME, SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD
            FROM product_database
        """
        products = self._execute_query(query, fetch_all=True)

        if not products:
            return {"message": "No products found to calculate profitability."}

        max_profit = float('-inf')
        best_product_info = None

        for p in products:
            selling_price = p.get('SELLING_PRICE', 0.0) or 0.0
            cost_price = p.get('COST_PRICE', 0.0) or 0.0
            # quantity = p.get('QUANTITY', 0) or 0 # Current stock, not directly used in COGS for this item's profit
            items_sold = p.get('ITEMS_SOLD', 0) or 0

            if items_sold > 0: # Only consider products that have been sold
                revenue = selling_price * items_sold
                cogs = cost_price * items_sold # Cost of goods sold for this product
                profit = revenue - cogs

                if profit > max_profit:
                    max_profit = profit
                    best_product_info = {
                        "id": p['ID'],
                        "name": p['NAME'],
                        "profit": round(profit, 2),
                        "items_sold": items_sold,
                        "revenue": round(revenue, 2),
                        "cogs": round(cogs, 2)
                    }

        if best_product_info:
            return best_product_info
        else:
            return {"message": "No profitable products found or no sales data available."}

    def least_selling_product(self):
        """Identifies the least-selling product based on ITEMS_SOLD."""
        # Considers only products that have been sold at least once, if any.
        # If all products have 0 sales, it might pick one arbitrarily or based on other criteria.
        # The original query `ORDER BY ITEMS_SOLD ASC LIMIT 1` would pick one with 0 sales if many exist.
        query_sold_products = """
            SELECT ID, NAME, ITEMS_SOLD
            FROM product_database
            WHERE ITEMS_SOLD > 0
            ORDER BY ITEMS_SOLD ASC, ID ASC -- Added ID for deterministic sort if multiple have same min sales
            LIMIT 1
        """
        product = self._execute_query(query_sold_products, fetch_one=True)

        if product:
            return {
                "id": product['ID'],
                "name": product['NAME'],
                "items_sold": product.get('ITEMS_SOLD', 0) # Should be > 0 here
            }
        else:
            # If no products have any sales, check for any product (even with 0 sales)
            query_any_product = """
                SELECT ID, NAME, ITEMS_SOLD
                FROM product_database
                ORDER BY ITEMS_SOLD ASC, ID ASC
                LIMIT 1
            """
            any_product = self._execute_query(query_any_product, fetch_one=True)
            if any_product:
                 return {
                    "id": any_product['ID'],
                    "name": any_product['NAME'],
                    "items_sold": any_product.get('ITEMS_SOLD', 0)
                }
            else:
                return {"message": "No products found in the database."}

# The original global instances like:
# db = Database()
# cursor = db.cursor
# product_mgr = ProductManager(db.conn, cursor)
# ... are no longer needed in this structure.
# Flask routes will instantiate manager classes as needed, or we can make them singletons if preferred.
# For now, instantiate per request or keep them as module-level instances if state is not an issue.
# Let's instantiate them in app.py for now for simplicity, and they will use get_db_connection().

product_mgr = ProductManager()
customer_mgr = CustomerManager()
employee_mgr = EmployeeManager()
finance_mgr = FinanceManager()
stat_mgr = StatManager()
