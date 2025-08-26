class CustomerManager:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor

    def _print_table_header(self):
        print("_" * 105)
        print(f"{'ID':<15}{'NAME':<20}{'CONTACT NUMBER':<25}{'GENDER':<15}{'TOTAL SPENT':<20}")
        print("_" * 105)

    def view_all_customers(self):
        self._print_table_header()
        try:
            self.cursor.execute("SELECT ID, NAME, CONTACT_NUMBER, GENDER, PURCHASES FROM customer_database")
            for row in self.cursor.fetchall():
                id_, name, contact, gender, purchases = row
                id_ = '' if id_ is None else id_
                name = '' if name is None else name
                contact = '' if contact is None else contact
                gender = '' if gender is None else gender
                total_spent = purchases if purchases is not None and purchases != '' else '0'
                # Convert id_ to string for consistent formatting
                print(f"{str(id_):<15}{name:<20}{contact:<25}{gender:<15}{total_spent:<20}")
        except Exception as e:
            print(f"Error viewing customers: {e}")

    def add_customer(self, name=None, contact=None, gender=None):
        # Automatically assign ID = max(ID) + 1
        self.cursor.execute("SELECT COALESCE(MAX(ID), 0) + 1 FROM customer_database")
        new_id = self.cursor.fetchone()[0]

        if not contact:
            while True:
                contact = input("Enter contact number of customer (10 digits) |  ").strip()
                if contact.isdigit() and len(contact) == 10:
                    break
                print("Invalid contact number format. Please enter a 10-digit number.")

        # Check if this contact already exists
        self.cursor.execute("SELECT ID FROM customer_database WHERE CONTACT_NUMBER = %s", (contact,))
        if self.cursor.fetchone():
            print("A customer with this contact number already exists.")
            return

        if not name:
            name = input("Enter name of customer                       |  ").strip()
        if not gender:
            gender = input("Enter gender of customer                     |  ").strip()

        try:
            query = """INSERT INTO customer_database (ID, NAME, CONTACT_NUMBER, GENDER, PURCHASES)
                    VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (new_id, name, contact, gender, "0"))
            self.db.commit()
            print(f"✅ Customer Data Inserted with ID {new_id}")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error adding customer: {e}")


    def edit_customer(self):
        try:
            # CHANGED: Input handling for integer ID
            customer_id_str = input("Enter the ID of the customer to be edited | ").strip()
            try:
                customer_id = int(customer_id_str)
            except ValueError:
                print("Invalid ID format. Please enter a valid integer.")
                return

            self.cursor.execute("SELECT * FROM customer_database WHERE ID = %s", (customer_id,))
            if not self.cursor.fetchone():
                print("No customer found with this ID.")
                return

            allowed_fields = {'contact number': 'CONTACT_NUMBER', 'name': 'NAME', 'gender': 'GENDER'}
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
            # CHANGED: Input handling for integer ID
            customer_id_str = input("Enter the Customer ID to be deleted : ").strip()
            try:
                customer_id = int(customer_id_str)
            except ValueError:
                print("Invalid ID format. Please enter a valid integer.")
                return

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
            # CHANGED: Input handling for integer ID
            customer_id_str = input("Enter the ID of Customer to be searched : ").strip()
            try:
                customer_id = int(customer_id_str)
            except ValueError:
                print("Invalid ID format. Please enter a valid integer.")
                return

            self.cursor.execute(
                "SELECT ID, NAME, CONTACT_NUMBER, GENDER, PURCHASES FROM customer_database WHERE ID = %s",
                (customer_id,)
            )
            data = self.cursor.fetchone()
            if data:
                self._print_table_header()
                id_, name, contact, gender, purchases = data
                id_ = '' if id_ is None else id_
                name = '' if name is None else name
                contact = '' if contact is None else contact
                gender = '' if gender is None else gender
                total_spent = purchases if purchases is not None and purchases != '' else '0'
                # Convert id_ to string for consistent formatting
                print(f"{str(id_):<15}{name:<20}{contact:<25}{gender:<15}{total_spent:<20}")
            else:
                print("No customer data with this ID.\n")
        except Exception as e:
            print(f"Error searching customer: {e}")