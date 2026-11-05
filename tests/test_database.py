import os
import sqlite3
import database


def test_database_operations():
    database.DB_NAME = "test_hardware.db"

    if os.path.exists(database.DB_NAME):
        os.remove(database.DB_NAME)

    try:
        database.init_db()
        assert os.path.exists(database.DB_NAME), "Az adatbázis fájl nem jött létre!"

        sample_product = {
            "name": "Kingston Fury 16GB RAM",
            "category": "RAM",
            "url": "https://www.arukereso.hu/teszt-termek",
            "offers": [
                {"shop": "Bolt A", "price": 24500},
                {"shop": "Bolt B", "price": 23900}
            ]
        }

        database.save_scraped_data(sample_product, target_price=23000)

        
        conn = database.get_connection()
        cursor = conn.cursor()

    
        cursor.execute("SELECT name FROM shops ORDER BY name ASC")
        shops = [row["name"] for row in cursor.fetchall()]
        assert shops == ["Bolt A", "Bolt B"], "A boltok nem kerültek be helyesen a shops táblába!"

        
        cursor.execute("SELECT product_id, shop_id, price FROM price_history")
        rows = cursor.fetchall()
        assert len(rows) == 2, "Nem 2 rekord került a price_history táblába!"
        for r in rows:
            assert r["shop_id"] is not None, "Hiányzik a külső kulcs (shop_id)!"

        conn.close()

        
        history = database.get_price_history("Kingston Fury 16GB RAM", days=7)
        assert len(history) == 2, "Nem 2 árat talált az adatbázis a lekérdezés során!"

        prices = [item["price"] for item in history]
        shop_names = [item["shop_name"] for item in history]

        assert 24500 in prices
        assert 23900 in prices
        assert "Bolt A" in shop_names
        assert "Bolt B" in shop_names

        print("Minden 3NF adatbázis-teszt sikeresen lefutott!")

    finally:
        if os.path.exists(database.DB_NAME):
            os.remove(database.DB_NAME)


if __name__ == "__main__":
    test_database_operations()