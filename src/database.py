from mysql.connector import Error

import mysql.connector

class Database:
    def __init__(self,
                 host="localhost",
                 user="root",
                 passwd="Kabilesh1!",
                 database="sms_database"):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                passwd=passwd,
                database=database
            )
            self.cursor = self.conn.cursor(buffered=True)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.conn = None
            self.cursor = None

    def execute(self, query, values=None):
        """Execute a query and return cursor."""
        if self.cursor is None:
            print("No database connection.")
            return None
        try:
            if values is None:
                values = ()
            self.cursor.execute(query, values)
            return self.cursor
        except Error as e:
            print(f"Error executing query: {e}")
            return None

    def commit(self):
        if self.conn:
            try:
                self.conn.commit()
            except Error as e:
                print(f"Error during commit: {e}")

    def fetch_all(self):
        if self.cursor:
            try:
                return self.cursor.fetchall()
            except Error as e:
                print(f"Error fetching data: {e}")
                return None
        return None

    def close(self):
        if self.cursor:
            try:
                self.cursor.close()
            except Exception as e:
                print(f"Error closing cursor: {e}")
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
