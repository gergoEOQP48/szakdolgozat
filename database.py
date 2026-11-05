import sqlite3
from datetime import datetime, timedelta

DB_NAME = "hardware_prices.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            url TEXT NOT NULL,
            target_price INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            shop_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            checked_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
            FOREIGN KEY (shop_id) REFERENCES shops (id) ON DELETE CASCADE
        )
    """)

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

    cursor.execute("SELECT id FROM products WHERE name = ?", (product_data["name"],))
    product_id = cursor.fetchone()["id"]

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for offer in product_data["offers"]:
        shop_name = offer["shop"]

        cursor.execute("INSERT OR IGNORE INTO shops (name) VALUES (?)", (shop_name,))
        
        cursor.execute("SELECT id FROM shops WHERE name = ?", (shop_name,))
        shop_id = cursor.fetchone()["id"]

        cursor.execute("""
            INSERT INTO price_history (product_id, shop_id, price, checked_at)
            VALUES (?, ?, ?, ?)
        """, (
            product_id,
            shop_id,
            offer["price"],
            current_time
        ))

    conn.commit()
    conn.close()

def get_price_history(product_name: str, days: int = 7):
    conn = get_connection()
    cursor = conn.cursor()

    time_limit = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT s.name AS shop_name, ph.price, ph.checked_at
        FROM price_history ph
        JOIN products p ON ph.product_id = p.id
        JOIN shops s ON ph.shop_id = s.id
        WHERE p.name = ? AND ph.checked_at >= ?
        ORDER BY ph.checked_at ASC
    """, (product_name, time_limit))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]