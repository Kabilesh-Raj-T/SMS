from mysql.connector import Error
import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

# Get credentials from the environment
db_host = os.getenv("MYSQLHOST")
db_user = os.getenv("MYSQLUSER")
db_password = os.getenv("MYSQLPASSWORD")
db_name = os.getenv("MYSQLDATABASE")
db_port = os.getenv("MYSQLPORT")

class Database:
    def __init__(self,
                 host=db_host,
                 user=db_user,
                 passwd=db_password,
                 database=db_name):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                passwd=passwd,
                database=database,
                port=int(db_port)
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