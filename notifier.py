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