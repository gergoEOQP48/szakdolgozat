import os
import database

def test_database_operations():
    
    database.DB_NAME = "test_hardware.db"
    
    
    if os.path.exists(database.DB_NAME):
        os.remove(database.DB_NAME)

    
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

    
    history = database.get_price_history("Kingston Fury 16GB RAM", days=7)

    
    assert len(history) == 2, "Nem 2 árat talált az adatbázis!"
    
    prices = [item["price"] for item in history]
    assert 24500 in prices
    assert 23900 in prices

    
    if os.path.exists(database.DB_NAME):
        os.remove(database.DB_NAME)

    print("Minden adatbázis teszt sikeresen lefutott!")