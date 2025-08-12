class Dynamic_Price:
    def __init__(self, db, cursor, min_price_ratio=0.75, min_days_left=31):
        self.db = db
        self.cursor = cursor
        self.min_price_ratio = min_price_ratio
        self.min_days_left = min_days_left

    def update_prices(self):
        try:
            min_price_ratio_input = input(f"Enter minimum price ratio (default {self.min_price_ratio}): ").strip()
            min_days_left_input = input(f"Enter minimum days left (default {self.min_days_left}): ").strip()

            min_price_ratio = float(min_price_ratio_input) if min_price_ratio_input else self.min_price_ratio
            min_days_left = int(min_days_left_input) if min_days_left_input else self.min_days_left
        except ValueError:
            print("Invalid input. Using default values.")
            min_price_ratio = self.min_price_ratio
            min_days_left = self.min_days_left

        query = """
        UPDATE product_database p
        LEFT JOIN (
            SELECT
                product_id,
                IFNULL(SUM(quantity), 0) AS sold_last_month
            FROM sales_history
            WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
            GROUP BY product_id
        ) s ON p.ID = s.product_id
        SET p.SELLING_PRICE = ROUND(
            CASE
                WHEN DATEDIFF(p.EXPIRY_DATE, CURDATE()) >= %s
                    THEN p.MRP
                ELSE
                    p.MRP * (
                        %s + (1 - %s) *
                        GREATEST(0, LEAST(1, DATEDIFF(p.EXPIRY_DATE, CURDATE()) / %s)) *
                        (IFNULL(s.sold_last_month, 0) / NULLIF((IFNULL(s.sold_last_month, 0) + p.QUANTITY), 0))
                    )
            END
        , 2);
        """
        self.cursor.execute(query, (min_days_left, min_price_ratio, min_price_ratio, min_days_left))
        self.db.commit()
        print("Selling prices updated successfully.")

    def get_dynamic_price(self, product_id):
        """
        Return computed dynamic price for a single product (None if not found).
        product_id may be str or int; we leave DB to coerce it.
        """
        query_price = """
            SELECT 
                ROUND(
                    CASE
                        WHEN DATEDIFF(p.EXPIRY_DATE, CURDATE()) >= %s 
                            THEN p.MRP
                        ELSE 
                            p.MRP * (
                                %s + (1 - %s) *
                                GREATEST(0, LEAST(1, DATEDIFF(p.EXPIRY_DATE, CURDATE()) / %s)) *
                                (IFNULL(s.sold_last_month, 0) / NULLIF((IFNULL(s.sold_last_month, 0) + p.QUANTITY), 0))
                            )
                    END
                , 2) AS dynamic_price
            FROM product_database p
            LEFT JOIN (
                SELECT product_id, IFNULL(SUM(quantity), 0) AS sold_last_month
                FROM sales_history
                WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
                GROUP BY product_id
            ) s ON p.ID = s.product_id
            WHERE p.ID = %s
        """

        self.cursor.execute(query_price, (self.min_days_left, self.min_price_ratio, self.min_price_ratio, self.min_days_left, product_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None
