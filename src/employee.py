class EmployeeManager:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor

    def view_all_employees(self):
        print(f"\n{'ID':<15}{'NAME':<20}{'CONTACT NUMBER':<25}{'GENDER':<25}{'POSITION':<20}{'SALARY':<20}")
        self.cursor.execute("SELECT * FROM employee_database")
        for row in self.cursor.fetchall():
            # No change needed here, f-string formatting handles integers correctly
            print(f"{row[0]:<15}{row[1]:<20}{row[2]:<25}{row[3]:<25}{row[4]:<20}{row[5]:<20}")
        print()

    def add_employee(self):
        try:
            # CHANGED: Convert input ID to integer with error handling
            emp_id_str = input("Enter the employee ID (integer)            |  ").strip()
            emp_id = int(emp_id_str)
        except ValueError:
            print("Invalid ID. Please enter a numeric value.")
            return

        self.cursor.execute("SELECT ID FROM employee_database WHERE ID = %s", (emp_id,))
        if self.cursor.fetchone():
            print("Employee with this ID already exists.")
            return

        name = input("Enter the employee Name                    |  ").strip()
        while True:
            contact = input("Enter 10-digit contact number            |  ").strip()
            if contact.isdigit() and len(contact) == 10:
                break
            print("Invalid contact number. Please enter 10 digits.")

        gender = input("Enter gender of employee                   |  ").strip()
        position = input("Enter position of employee                 |  ").strip()
        while True:
            try:
                salary = float(input("Enter salary of employee                   |  ").strip())
                break
            except ValueError:
                print("Invalid salary. Please enter a numeric value.")

        query = """
        INSERT INTO employee_database (ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (emp_id, name, contact, gender, position, salary))
        self.db.commit()
        print("Employee Data Inserted Successfully.")

    def edit_employee(self):
        try:
            # CHANGED: Convert input ID to integer with error handling
            emp_id_str = input("Enter the ID of the employee to be edited | ").strip()
            emp_id = int(emp_id_str)
        except ValueError:
            print("Invalid ID. Please enter a numeric value.")
            return
            
        self.cursor.execute("SELECT * FROM employee_database WHERE ID = %s", (emp_id,))
        data = self.cursor.fetchone()
        if not data:
            print("No employee found with this ID.")
            return

        print(f"\n{'ID':<15}{'NAME':<20}{'CONTACT NUMBER':<25}{'GENDER':<25}{'POSITION':<20}{'SALARY':<20}")
        print(f"{data[0]:<15}{data[1]:<20}{data[2]:<25}{data[3]:<25}{data[4]:<20}{data[5]:<20}")

        field_map = {
            'name': 'NAME', 'contact number': 'CONTACT_NUMBER', 'gender': 'GENDER',
            'position': 'POSITION', 'salary': 'SALARY', 'id': 'ID'
        }
        field = input("\nEnter the field to be edited              | ").strip().lower()
        if field not in field_map:
            print("Invalid field.")
            return

        value_str = input("Enter the value to be set                 | ").strip()
        
        # ADDED: Convert value to the correct type based on the field being edited
        try:
            if field == 'id':
                value = int(value_str)
            elif field == 'salary':
                value = float(value_str)
            else:
                value = value_str
        except ValueError:
            print(f"Invalid value for field '{field}'. Please enter a numeric value.")
            return

        db_field = field_map[field]

        query = f"UPDATE employee_database SET {db_field} = %s WHERE ID = %s"
        self.cursor.execute(query, (value, emp_id))
        self.db.commit()

        current_id = value if field == 'id' else emp_id
        self.cursor.execute("SELECT * FROM employee_database WHERE ID = %s", (current_id,))
        data = self.cursor.fetchone()

        print("\nUpdated Information -->")
        print(f"{'ID':<15}{'NAME':<20}{'CONTACT NUMBER':<25}{'GENDER':<25}{'POSITION':<20}{'SALARY':<20}")
        if data:
            print(f"{data[0]:<15}{data[1]:<20}{data[2]:<25}{data[3]:<25}{data[4]:<20}{data[5]:<20}")
        print("Employee updated successfully.")


    def delete_employee(self):
        try:
            # CHANGED: Convert input ID to integer with error handling
            emp_id_str = input("Enter the employee ID to be deleted : ").strip()
            emp_id = int(emp_id_str)
        except ValueError:
            print("Invalid ID. Please enter a numeric value.")
            return

        self.cursor.execute("DELETE FROM employee_database WHERE ID = %s", (emp_id,))
        if self.cursor.rowcount > 0:
            self.db.commit()
            print("Employee Deleted Successfully.")
        else:
            print("No employee found with that ID.")

    def search_employee(self):
        try:
            # CHANGED: Convert input ID to integer with error handling
            emp_id_str = input("Enter the ID of employee to be searched : ").strip()
            emp_id = int(emp_id_str)
        except ValueError:
            print("Invalid ID. Please enter a numeric value.")
            return

        self.cursor.execute("SELECT * FROM employee_database WHERE ID = %s", (emp_id,))
        row = self.cursor.fetchone()
        if not row:
            print("No employee data with this ID.")
            return

        print(f"\n{'ID':<15}{'NAME':<20}{'CONTACT NUMBER':<25}{'GENDER':<25}{'POSITION':<20}{'SALARY':<20}")
        print(f"{row[0]:<15}{row[1]:<20}{row[2]:<25}{row[3]:<25}{row[4]:<20}{row[5]:<20}")