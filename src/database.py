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
            print("Database connection successful.")
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
            self.cursor.execute(query, values or ())
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

    def fetchone(self):
        if self.cursor:
            try:
                return self.cursor.fetchone()
            except Error as e:
                print(f"Error fetching data: {e}")
        return None

    def fetchall(self):
        if self.cursor:
            try:
                return self.cursor.fetchall()
            except Error as e:
                print(f"Error fetching data: {e}")
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
                print("Database connection closed.")
            except Exception as e:
                print(f"Error closing connection: {e}")