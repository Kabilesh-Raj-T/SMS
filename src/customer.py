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
