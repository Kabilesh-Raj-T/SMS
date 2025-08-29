import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT", 3306))   # default 3306 if not set
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
SSL_CA = os.getenv("SSL_CA")

class Database:
    def __init__(self,
                 host=HOST,
                 user=USER,
                 password=PASSWORD,
                 database=DATABASE,
                 port=PORT,
                 ssl_ca=SSL_CA):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                ssl_ca=ssl_ca,
                ssl_disabled=False
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