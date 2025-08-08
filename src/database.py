import mysql.connector
class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", user="root", passwd="Kabilesh1!", database="sms_database"
        )
        self.cursor = self.conn.cursor()

    def execute(self, query, values=None):
        self.cursor.execute(query, values or ())
        return self.cursor

    def commit(self):
        self.conn.commit()

    def fetch_all(self):
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
