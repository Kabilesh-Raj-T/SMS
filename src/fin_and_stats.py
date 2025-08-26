class FinanceManager:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor

    def profit_by_product(self):
        print(f"{'ID':<15}{'NAME':<20}{'SELLING PRICE':<15}{'COST PRICE':<15}{'PROFIT/LOSS':<15}")

        self.cursor.execute("""
            SELECT ID, NAME, SELLING_PRICE, COST_PRICE,
                (SELLING_PRICE * ITEMS_SOLD) - ((QUANTITY + ITEMS_SOLD) * COST_PRICE) AS PROFIT
            FROM product_database
            ORDER BY PROFIT DESC
        """)

        for row in self.cursor.fetchall():
            product_id, name, selling_price, cost_price, profit_loss = row
            print(f"{product_id:<15}{name:<20}{selling_price:<15.2f}{cost_price:<15.2f}{profit_loss:<15.2f}")

    def total_profit_or_loss(self):
        self.cursor.execute("""
            SELECT SUM((SELLING_PRICE * ITEMS_SOLD) - ((QUANTITY + ITEMS_SOLD) * COST_PRICE))
            FROM product_database
        """)
        result = self.cursor.fetchone()
        total = result[0] if result and result[0] is not None else 0

        if total < 0:
            print(f"TOTAL LOSS = {abs(total):.2f}")
        else:
            print(f"TOTAL PROFIT = {total:.2f}")

class StatManager:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor

    def best_selling_product(self):
        self.cursor.execute(
            "SELECT ID, NAME, ITEMS_SOLD FROM product_database ORDER BY ITEMS_SOLD DESC LIMIT 1"
        )
        product = self.cursor.fetchone()
        if product:
            print("\n📈 Best-Selling Product")
            print(f"ID: {product[0]}, NAME: {product[1]}, ITEMS SOLD: {product[2]}")
        else:
            print("No products found.")

    def most_profitable_product(self):
        # This calculation is now done in SQL for much better performance.
        query = """
            SELECT ID, NAME, ((SELLING_PRICE * ITEMS_SOLD) - ((QUANTITY + ITEMS_SOLD) * COST_PRICE)) AS PROFIT
            FROM product_database
            ORDER BY PROFIT DESC
            LIMIT 1
        """
        self.cursor.execute(query)
        product = self.cursor.fetchone()
        if product:
            print("\n💰 Most Profitable Product")
            print(f"ID: {product[0]}, NAME: {product[1]}, PROFIT: {product[2]:.2f}")
        else:
            print("No products found.")

    def least_selling_product(self):
        self.cursor.execute(
            "SELECT ID, NAME, ITEMS_SOLD FROM product_database ORDER BY ITEMS_SOLD ASC LIMIT 1"
        )
        product = self.cursor.fetchone()
        if product:
            print("\n📉 Least-Selling Product")
            print(f"ID: {product[0]}, NAME: {product[1]}, ITEMS SOLD: {product[2]}")
        else:
            print("No products found.")

    def customer_statistics(self):
        self.cursor.execute("SELECT COUNT(*) FROM customer_database")
        total_customers = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT SUM(PURCHASES) FROM customer_database")
        total_revenue = self.cursor.fetchone()[0] or 0

        print(f"\n👥 Total Customers: {total_customers}")
        print(f"💵 Total Revenue from Customers: {total_revenue:.2f}")
    
    def employee_statistics(self):
        self.cursor.execute("SELECT COUNT(*) FROM employee_database")
        total_employees = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT SUM(SALARY) FROM employee_database")
        total_salaries = self.cursor.fetchone()[0] or 0

        print(f"\n👷 Total Employees: {total_employees}")
        print(f"💰 Total Salaries Paid: {total_salaries:.2f}")
    
    def best_customer(self):
        self.cursor.execute(
            "SELECT ID, NAME, PURCHASES FROM customer_database ORDER BY PURCHASES DESC LIMIT 1"
        )
        best_customer = self.cursor.fetchone()
        if best_customer:
            print("\n🏆 Best Customer")
            print(f"ID: {best_customer[0]}, NAME: {best_customer[1]}, PURCHASES: {best_customer[2]}")
        else:
            print("No customers found.")
