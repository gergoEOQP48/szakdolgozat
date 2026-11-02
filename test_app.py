import os
import sqlite3
import pytest
from app import app

DB_NAME = "hardware_prices.db"
BACKUP_DB = "hardware_prices.db.bak"


@pytest.fixture(autouse=True)
def setup_teszt_adatbazis():

    if os.path.exists(DB_NAME):
        os.rename(DB_NAME, BACKUP_DB)

    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            target_price INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            shop_name TEXT,
            price INTEGER,
            checked_at TEXT
        )
    """)


    cur.execute("INSERT INTO products VALUES (1, 'Teszt RAM 16GB', 'RAM', 25000)")
    cur.execute("INSERT INTO price_history VALUES (1, 1, 'iPon', 24000, '2026-10-20 12:00:00')")
    conn.commit()
    conn.close()

    yield


    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    if os.path.exists(BACKUP_DB):
        os.rename(BACKUP_DB, DB_NAME)



def test_fooldal_megjelenik():
    client = app.test_client()
    valasz = client.get("/")

    assert valasz.status_code == 200
    html = valasz.get_data(as_text=True)
    assert "Teszt RAM 16GB" in html
    assert "iPon" in html
    assert "24000" in html



def test_termek_grafikon_oldal():
    client = app.test_client()
    valasz = client.get("/product/1")

    assert valasz.status_code == 200
    html = valasz.get_data(as_text=True)
    assert "Teszt RAM 16GB" in html
    assert "history-data" in html
    assert "24000" in html



def test_nem_letezo_termek_404():
    client = app.test_client()
    valasz = client.get("/product/9999")

    assert valasz.status_code == 404
    assert "A termék nem található" in valasz.get_data(as_text=True)