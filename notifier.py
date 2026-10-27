import sqlite3

def check_price_alerts(db_name="hardware_prices.db"):
    
    print("Értesítési rendszer futtatása: Árak ellenőrzése a célárak alapján...\n")
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()