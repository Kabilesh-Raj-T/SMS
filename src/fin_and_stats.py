class FinanceManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def profit_by_product(self):
        print("%-15s%-20s%-15s%-15s%-15s" %
              ("ID", "NAME", "SELLING PRICE", "COST PRICE", "PROFIT/LOSS"))

        self.cursor.execute("""
            SELECT ID, NAME, SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD,
                (SELLING_PRICE * ITEMS_SOLD) - ((QUANTITY + ITEMS_SOLD) * COST_PRICE) AS PROFIT
            FROM product_database
            ORDER BY PROFIT DESC
        """)

        for row in self.cursor.fetchall():
            product_id, name, selling_price, cost_price, quantity, items_sold, profit_loss = row
            print("%-15s%-20s%-15.2f%-15.2f%-15.2f" %
                (product_id, name, selling_price, cost_price, profit_loss))

    def total_profit_or_loss(self):
        self.cursor.execute("SELECT SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD FROM product_database")
        total = 0
        for s_price, c_price, qty, sold in self.cursor.fetchall():
            revenue = s_price * sold
            cost = (qty + sold) * c_price
            profit_loss = revenue - cost
            total += profit_loss

        if total < 0:
            print(f"LOSS   = {abs(total):.2f}")
        else:
            print(f"PROFIT = {total:.2f}")

class StatManager:
    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

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
        self.cursor.execute("SELECT ID, NAME, SELLING_PRICE, COST_PRICE, QUANTITY, ITEMS_SOLD FROM product_database")

        max_profit = float('-inf')
        best_product = None

        for row in self.cursor.fetchall():
            product_id, name, s_price, c_price, qty, sold = row
            s_price = s_price or 0
            c_price = c_price or 0
            qty = qty or 0
            sold = sold or 0

            revenue = s_price * sold
            cost = (qty + sold) * c_price
            profit = revenue - cost

            if profit > max_profit:
                max_profit = profit
                best_product = (product_id, name, profit)

        if best_product:
            print("\n💰 Most Profitable Product")
            print(f"ID: {best_product[0]}, NAME: {best_product[1]}, PROFIT: {best_product[2]:.2f}")
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