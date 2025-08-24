class Dynamic_Price:
    def __init__(self, db, min_price_ratio=0.75, min_days_left=31):
        self.db = db
        self.cursor = db.cursor
        self.min_price_ratio = min_price_ratio
        self.min_days_left = min_days_left
        self.sales_subquery = """
            SELECT product_id, IFNULL(SUM(quantity), 0) AS sold_last_month
            FROM sales_history
            WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
            GROUP BY product_id
        """

    def _get_user_input(self):
        try:
            min_price_ratio = float(input(f"Enter minimum price ratio (default {self.min_price_ratio}): ").strip() or self.min_price_ratio)
            min_days_left = int(input(f"Enter minimum days left (default {self.min_days_left}): ").strip() or self.min_days_left)
            return min_price_ratio, min_days_left
        except ValueError:
            print("Invalid input. Using default values.")
            return self.min_price_ratio, self.min_days_left

    def _calculate_price(self, mrp, days_until_expiry, sold_last_month, quantity, min_price_ratio, min_days_left):
        if days_until_expiry >= min_days_left:
            return mrp

        expiry_factor = max(0, min(1, days_until_expiry / min_days_left))
        demand_factor = sold_last_month / (sold_last_month + quantity) if (sold_last_month + quantity) > 0 else 0
        return round(mrp * (min_price_ratio + (1 - min_price_ratio) * expiry_factor * demand_factor), 2)

    def update_prices(self):
        min_price_ratio, min_days_left = self._get_user_input()
        query = f"""
        UPDATE product_database p
        LEFT JOIN ({self.sales_subquery}) s ON p.ID = s.product_id
        SET p.SELLING_PRICE = ROUND(
            CASE
                WHEN DATEDIFF(p.EXPIRY_DATE, CURDATE()) >= %s THEN p.MRP
                ELSE p.MRP * (
                    %s + (1 - %s) *
                    GREATEST(0, LEAST(1, DATEDIFF(p.EXPIRY_DATE, CURDATE()) / %s)) *
                    (IFNULL(s.sold_last_month, 0) / NULLIF((IFNULL(s.sold_last_month, 0) + p.QUANTITY), 0))
                )
            END
        , 2)
        """
        try:
            self.cursor.execute(query, (min_days_left, min_price_ratio, min_price_ratio, min_days_left))
            self.db.commit()
            print("Selling prices updated successfully.")
        except Exception as e:
            self.db.rollback()
            print(f"Error updating prices: {e}")

    def get_dynamic_price(self, product_id):
        query = f"""
            SELECT
                p.MRP,
                DATEDIFF(p.EXPIRY_DATE, CURDATE()) as days_left,
                p.QUANTITY,
                IFNULL(s.sold_last_month, 0) as sold_last_month
            FROM product_database p
            LEFT JOIN ({self.sales_subquery}) s ON p.ID = s.product_id
            WHERE p.ID = %s
        """
        try:
            self.cursor.execute(query, (product_id,))
            result = self.cursor.fetchone()
            if not result:
                return None

            mrp, days_left, quantity, sold_last_month = result
            # Convert Decimal to float for calculation
            mrp = float(mrp)
            quantity = float(quantity)
            sold_last_month = float(sold_last_month)
            return self._calculate_price(
                mrp, days_left, sold_last_month, quantity,
                self.min_price_ratio, self.min_days_left
            )
        except Exception as e:
            print(f"Error fetching dynamic price: {e}")
            return None