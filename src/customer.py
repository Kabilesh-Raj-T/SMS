class CustomerManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def _print_table_header(self):
        print("_" * 130)
        print("%-15s%-20s%-25s%-15s%-25s%-20s" % ("ID", "NAME", "CONTACT NUMBER", "GENDER", "EMAIL", "PURCHASES"))
        print("_" * 130)

    def _print_table_separator(self):
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
                            print("%-15s%-20s%-25s%-15s%-25s%-20s" % (row[0], row[1], row[2], row[3], row[4], purchase))
        except Exception as e:
            print(f"Error viewing customers: {e}")

    def add_customer(self):
        import re
        try:
            self.cursor.execute("SELECT ID, CONTACT_NUMBER FROM customer_database")
            existing = self.cursor.fetchall()
            existing_ids = [str(row[0]) for row in existing]
            existing_contacts = [str(row[1]) for row in existing]
        except Exception as e:
            print(f"Error fetching existing customers: {e}")
            return

        customer_id = input("Enter the Customer ID                    |  ").strip()
        # Example: Customer ID must be alphanumeric and 5-10 characters long
        if not (customer_id.isalnum() and 5 <= len(customer_id) <= 10):
            print("Invalid Customer ID format. Please enter an alphanumeric ID (5-10 characters).")
            return
        while True:
            contact = input("Enter contact number of customer         |  ").strip()
            if not contact.isdigit() or len(contact) != 10:
                print("Invalid contact number format. Please enter a 10-digit number.")
                continue
            if contact in existing_contacts:
                print("Contact number already exists.")
                return
            break
        name = input("Enter name of customer                    |  ").strip()
        gender = input("Enter gender of customer                  |  ").strip()
        email = input("Enter email of customer                  |  ").strip()
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            print("Invalid email format. Please enter a valid email address (e.g., user@example.com).")
            return
        try:
            query = """INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, GENDER, EMAIL, PURCHASES)
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (customer_id, name, contact, gender, email, ""))
            self.db.commit()
            print("Customer Data Inserted")
        except Exception as e:
            self.db.rollback()
            print(f"Error adding customer: {e}")
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
            data = self.cursor.fetchone()
            if not data:
                print("No customer found with this ID.")
                return

            purchases = (data[5] or '').split('|')
            allowed_fields = {
                'contact number': 'CONTACT_NUMBER',
                'email': 'EMAIL',
                'name': 'NAME',
                'gender': 'GENDER'
            }
            print("Allowed fields to edit: " + ", ".join(allowed_fields.keys()))
            field = input("Enter the field to be edited              | ").strip().lower()
            value = input("Enter the value to be set                 | ")

            allowed_fields = {
                'contact number': 'contact_number',
                'email': 'email',
                'name': 'name',
                'gender': 'gender'
            }

            if field not in allowed_fields:
                print("Invalid field.")
                return

            db_field = allowed_fields[field]
            # Use uppercase in SQL if required by your database schema
            query = f"UPDATE customer_database SET {db_field.upper()} = %s WHERE ID = %s"
            self.cursor.execute(query, (value, customer_id))
            self.db.commit()
            print("1 row updated")
        except Exception as e:
            self.db.rollback()
            print(f"Error editing customer: {e}")

    def delete_customer(self):
        try:
            customer_id = input("Enter the Customer ID to be deleted : ").strip()
            self.cursor.execute("SELECT ID FROM customer_database WHERE ID = %s", (customer_id,))
            if not self.cursor.fetchone():
                print("No such customer.")
                return
            self.cursor.execute("DELETE FROM customer_database WHERE ID = %s", (customer_id,))
            self.db.commit()
            print("Row Deleted")
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting customer: {e}")

    def search_customer(self):
        try:
            customer_id = input("Enter the ID of Customer to be searched : ").strip()
            self.cursor.execute("SELECT ID FROM customer_database")
            ids = [str(row[0]) for row in self.cursor.fetchall()]
            if customer_id not in ids:
                print("No customer data with this ID.\n")
                return

            self.cursor.execute(
                "SELECT ID, NAME, CONTACT_NUMBER, GENDER, EMAIL, PURCHASES FROM customer_database WHERE ID = %s",
                (customer_id,)
            )
            data = self.cursor.fetchone()
            if data:
                purchases = (data[5] or '').split('|')
                self._print_table_header()
                for i, p in enumerate(purchases):
                    if i == 0:
                        print("%-15s%-20s%-25s%-15s%-25s%-20s" % (data[0], data[1], data[2], data[3], data[4], p))
                    else:
                        print("%-15s%-20s%-25s%-15s%-25s%-20s" % ('', '', '', '', '', p))
        except Exception as e:
            print(f"Error searching customer: {e}")