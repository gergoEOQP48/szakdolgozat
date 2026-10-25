import sqlite3
from datetime import datetime, timedelta

DB_NAME = "hardware_prices.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            url TEXT NOT NULL,
            target_price INTEGER DEFAULT 0
        )""")


    cursor.execute("""CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            shop_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            checked_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )""")

    conn.commit()
    conn.close()



    def save_scraped_data(product_data: dict, target_price: int = 0):
        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
        INSERT INTO products (name, category, url, target_price)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            url = excluded.url,
            target_price = CASE 
                WHEN excluded.target_price > 0 THEN excluded.target_price 
                ELSE products.target_price 
            END
    """, (
        product_data["name"],
        product_data["category"],
        product_data["url"],
        target_price
    ))

    