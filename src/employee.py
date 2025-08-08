class EmployeeManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def view_all_employees(self):
        print("\n%-15s%-20s%-25s%-25s%-20s%-20s" %
              ("ID", "NAME", "CONTACT NUMBER", "GENDER", "POSITION", "SALARY"))
        self.cursor.execute("SELECT * FROM employee_database")
        for row in self.cursor.fetchall():
            print("%-15s%-20s%-25s%-25s%-20s%-20s" %
                  (row[0], row[1], row[2], row[3], row[4], row[5]))
        print()

    def add_employee(self):
        self.cursor.execute("SELECT ID FROM employee_database")
        ids = [str(row[0]) for row in self.cursor.fetchall()]
        emp_id = input("Enter the employee ID                    |  ")
        if emp_id in ids:
            print("Employee already exists.")
            return

        name = input("Enter the employee Name                  |  ")
        contact = input("Enter contact number of employee         |  ")
        gender = input("Enter gender of employee                 |  ")
        position = input("Enter position of employee               |  ")
        salary = input("Enter salary of employee                 |  ")

        query = """
        INSERT INTO employee_database (ID, NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (emp_id, name, contact, gender, position, salary))
        self.db.commit()
        print("Employee Data Inserted")

    def edit_employee(self):
        emp_id = input("Enter the ID of the employee to be edited | ")
        self.cursor.execute("SELECT * FROM employee_database WHERE ID = %s", (emp_id,))
        data = self.cursor.fetchone()
        if not data:
            print("No employee found with this ID.")
            return

        print("\n%-15s%-20s%-25s%-25s%-20s%-20s" %
              ("ID", "NAME", "CONTACT NUMBER", "GENDER", "POSITION", "SALARY"))
        print("%-15s%-20s%-25s%-25s%-20s%-20s" % data)

        field = input("Enter the field to be edited              | ").strip().lower()
        value = input("Enter the value to be set                 | ")

        field_map = {
            'name': 'NAME',
            'contact number': 'CONTACT_NUMBER',
            'gender': 'GENDER',
            'position': 'POSITION',
            'salary': 'SALARY',
            'id': 'ID'
        }

        if field not in field_map:
            print("Invalid field.")
            return

        query = f"UPDATE employee_database SET {field_map[field]} = %s WHERE ID = %s"
        self.cursor.execute(query, (value, emp_id))
        self.db.commit()

        self.cursor.execute("SELECT * FROM employee_database WHERE ID = %s", (value if field == 'id' else emp_id,))
        data = self.cursor.fetchone()
        print("\nUpdated Information -->")
        print("%-15s%-20s%-25s%-25s%-20s%-20s" %
              ("ID", "NAME", "CONTACT NUMBER", "GENDER", "POSITION", "SALARY"))
        print("%-15s%-20s%-25s%-25s%-20s%-20s" % data)

    def delete_employee(self):
        emp_id = input("Enter the employee ID to be deleted : ")
        self.cursor.execute("DELETE FROM employee_database WHERE ID = %s", (emp_id,))
        self.db.commit()
        print("Employee Deleted")

    def search_employee(self):
        emp_id = input("Enter the ID of employee to be searched : ")
        self.cursor.execute("SELECT ID FROM employee_database")
        ids = [str(row[0]) for row in self.cursor.fetchall()]
        if emp_id not in ids:
            print("No employee data with this ID.")
            return

        self.cursor.execute(
            "SELECT NAME, CONTACT_NUMBER, GENDER, POSITION, SALARY FROM employee_database WHERE ID = %s", (emp_id,))
        row = self.cursor.fetchone()
        print("%-15s%-20s%-25s%-25s%-20s%-20s" %
              ("ID", "NAME", "CONTACT NUMBER", "GENDER", "POSITION", "SALARY"))
        print("%-15s%-20s%-25s%-25s%-20s%-20s" %
              (emp_id, row[0], row[1], row[2], row[3], row[4]))
