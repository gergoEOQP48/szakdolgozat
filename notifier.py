import sqlite3
import requests

def send_discord_alert(webhook_url, message):
    data = {
        "content": message
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204 or response.status_code == 200:
            print("[DISCORD] Értesítés sikeresen elküldve Discordra!")
        else:
            print(f"[HIBA] Discord hiba: {response.status_code}")
    except Exception as e:
        print(f"[HIBA] Nem sikerült elküldeni a Discord üzenetet: {e}")

def check_price_alerts(db_name="hardware_prices.db"):
    print("Értesítési rendszer futtatása: Árak ellenőrzése a célárak alapján...\n")

    webhook_url = "https://discordapp.com/api/webhooks/1564687049246900316/r3LfyA4dykQLlptlAHSsh-RIGN-bMWOADdTLjKGZBW548jtQB9SW_ubohA64dEfR3iqF"
    
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
            SELECT s.name AS shop_name, ph.price, ph.checked_at
            FROM price_history ph
            JOIN shops s ON ph.shop_id = s.id
            WHERE ph.product_id = ? 
            ORDER BY ph.checked_at DESC
        """, (prod_id,))
        
        offers = cursor.fetchall()

        if not offers:
            continue

        latest_date = offers[0][2]
        latest_offers = [o for o in offers if o[2] == latest_date]

        if not latest_offers:
            continue

        cheapest_offer = min(latest_offers, key=lambda x: x[1])
        cheapest_shop = cheapest_offer[0]
        cheapest_price = cheapest_offer[1]

        print(f"Termék: {name}")
        print(f"  -> Célár: {target_price:,} Ft | Legjobb aktuális ár: {cheapest_price:,} Ft ({cheapest_shop})")

        if cheapest_price <= target_price:
            print(f"ÁRLEESÉS!!!")
            print(f" A(z) {name} most olcsóbb ({cheapest_price:,} Ft), mint a célárad ({target_price:,} Ft)!")
            print(f"Elérhető itt: {cheapest_shop}\n")

            message = f"@everyone FIGYELEM! ÁRLEESÉS!\nA(z) **{name}** termék ára elérte a céláradat!\nLegjobb ár: **{cheapest_price:,} Ft**\nBolt: **{cheapest_shop}**\nCélár volt: {target_price:,} Ft"
            send_discord_alert(webhook_url, message)

            alert_count += 1
        else:
            diff = cheapest_price - target_price
            print(f"Még drágább a célárnál {diff:,} Ft-tal.\n")

    conn.close()
    print(f"Ellenőrzés kész. Találatok száma a célár alatt: {alert_count}")

if __name__ == "__main__":
    check_price_alerts()