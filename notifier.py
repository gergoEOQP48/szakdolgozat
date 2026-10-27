import sqlite3

def check_price_alerts(db_name="hardware_prices.db"):
    
    print("Értesítési rendszer futtatása: Árak ellenőrzése a célárak alapján...\n")
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()


    cursor.execute("""
        SELECT p.id, p.name, p.category, p.target_price
        FROM products p
    """)
    products = cursor.fetchall()

    if not products:
        print("Nincs rögzített termék az adatbázisban.")
        conn.close()
        return

    alert_count = 0

    for prod_id, name, category, target_price in products:
        if target_price is None or target_price == 0:
            print(f"[INFO] '{name}' - Nincs megadva célár, kihagyva.")
            continue

        cursor.execute("""
            SELECT s.shop_name, o.price, o.checked_at
            FROM offers o
            JOIN shops s ON o.shop_id = s.id
            WHERE o.product_id = ? 
            ORDER BY o.checked_at DESC
        """, (prod_id,))
        
        offers = cursor.fetchall()

        if not offers:
            continue


        
        latest_date = offers[0][2]
        latest_offers = [o for o in offers if o[2] == latest_date]

        if not latest_offers:
            continue

            