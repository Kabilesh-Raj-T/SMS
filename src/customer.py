import re
class CustomerManager:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor

    def _print_table_header(self):
        print("_" * 130)
        print(f"{'ID':<15}{'NAME':<20}{'CONTACT NUMBER':<25}{'GENDER':<15}{'EMAIL':<25}{'PURCHASES':<20}")
        print("_" * 130)

    def view_all_customers(self):
        self._print_table_header()
        try:
            self.cursor.execute("SELECT * FROM customer_database")
            for row in self.cursor.fetchall():
                purchases = (row[5] or '').split('|')
                for i, purchase in enumerate(purchases):
                    if purchase:
                        if i == 0:
                            print(f"{row[0]:<15}{row[1]:<20}{row[2]:<25}{row[3]:<15}{row[4]:<25}{purchase:<20}")
                        else:
                            print(f"{'':<15}{'':<20}{'':<25}{'':<15}{'':<25}{purchase:<20}")
        except Exception as e:
            print(f"Error viewing customers: {e}")

    def add_customer(self, customer_id=None, name=None, contact=None, gender=None, email=None):
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not customer_id:
            customer_id = input("Enter the Customer ID (5-10 alphanum)    |  ").strip()
        if not (customer_id.isalnum() and 5 <= len(customer_id) <= 10):
            print("Invalid Customer ID format. Please enter an alphanumeric ID (5-10 characters).")
            return

        if not contact:
            while True:
                contact = input("Enter contact number of customer (10 digits) |  ").strip()
                if contact.isdigit() and len(contact) == 10:
                    break
                print("Invalid contact number format. Please enter a 10-digit number.")
        
        self.cursor.execute("SELECT ID, CONTACT_NUMBER FROM customer_database WHERE ID = %s OR CONTACT_NUMBER = %s", (customer_id, contact))
        if self.cursor.fetchone():
            print("A customer with this ID or Contact Number already exists.")
            return

        if not name: name = input("Enter name of customer                   |  ").strip()
        if not gender: gender = input("Enter gender of customer                 |  ").strip()
        if not email:
            while True:
                email = input("Enter email of customer                  |  ").strip()
                if re.match(email_pattern, email):
                    break
                print("Invalid email format (e.g., user@example.com).")

        try:
            query = """INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, GENDER, EMAIL, PURCHASES)
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (customer_id, name, contact, gender, email, ""))
            self.db.commit()
            print("Customer Data Inserted")
        except Exception as e:
            self.db.rollback()
            print(f"Error adding customer: {e}")

    def edit_customer(self):
        try:
            customer_id = input("Enter the ID of the customer to be edited | ").strip()
            self.cursor.execute("SELECT * FROM customer_database WHERE ID = %s", (customer_id,))
            if not self.cursor.fetchone():
                print("No customer found with this ID.")
                return

            allowed_fields = {'contact number': 'CONTACT_NUMBER', 'email': 'EMAIL', 'name': 'NAME', 'gender': 'GENDER'}
            print("Allowed fields to edit: " + ", ".join(allowed_fields.keys()))

            field = input("Enter the field to be edited              | ").strip().lower()
            if field not in allowed_fields:
                print("Invalid field.")
                return

            value = input("Enter the value to be set                 | ").strip()
            db_field = allowed_fields[field]
            query = f"UPDATE customer_database SET {db_field} = %s WHERE ID = %s"
            self.cursor.execute(query, (value, customer_id))
            self.db.commit()
            print("Customer record updated successfully.")

        except Exception as e:
            self.db.rollback()
            print(f"Error editing customer: {e}")

    def delete_customer(self):
        try:
            customer_id = input("Enter the Customer ID to be deleted : ").strip()
            self.cursor.execute("DELETE FROM customer_database WHERE ID = %s", (customer_id,))
            if self.cursor.rowcount > 0:
                self.db.commit()
                print("Customer Deleted Successfully.")
            else:
                print("No customer found with that ID.")
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting customer: {e}")

    def search_customer(self):
        try:
            customer_id = input("Enter the ID of Customer to be searched : ").strip()
            self.cursor.execute(
                "SELECT ID, NAME, CONTACT_NUMBER, GENDER, EMAIL, PURCHASES FROM customer_database WHERE ID = %s",
                (customer_id,)
            )
            data = self.cursor.fetchone()
            if data:
                self._print_table_header()
                purchases = (data[5] or '').split('|')
                for i, p in enumerate(purchases):
                    if i == 0:
                        print(f"{data[0]:<15}{data[1]:<20}{data[2]:<25}{data[3]:<15}{data[4]:<25}{p:<20}")
                    elif p:
                        print(f"{'':<15}{'':<20}{'':<25}{'':<15}{'':<25}{p:<20}")
            else:
                print("No customer data with this ID.\n")
        except Exception as e:
            print(f"Error searching customer: {e}")