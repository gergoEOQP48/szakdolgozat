import sqlite3
from unittest.mock import patch
import notifier

def create_test_db(db_path, product_data, offers_data):
    """Segédfüggvény a 3NF kompatibilis tesztadatbázis létrehozásához."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            target_price INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            shop_id INTEGER,
            price INTEGER,
            checked_at TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        )
    """)

    cur.execute("INSERT INTO products VALUES (?, ?, ?, ?)", product_data)

    for offer in offers_data:
        prod_id, shop_name, price, checked_at = offer
        cur.execute("INSERT OR IGNORE INTO shops (name) VALUES (?)", (shop_name,))
        cur.execute("SELECT id FROM shops WHERE name = ?", (shop_name,))
        shop_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO price_history (product_id, shop_id, price, checked_at)
            VALUES (?, ?, ?, ?)
        """, (prod_id, shop_id, price, checked_at))

    conn.commit()
    conn.close()


def test_ertesites_ha_elertuk_a_celarat(tmp_path):
    """Ha a legjobb ár kisebb vagy egyenlő mint a célár, el kell küldeni a Discord értesítést."""
    db_file = str(tmp_path / "test_alert.db")

    product = (1, "Kingston FURY Beast 32GB", "RAM", 50000)
    offers = [
        (1, "iPon", 45000, "2026-10-20 10:00:00"),
        (1, "Alza", 48000, "2026-10-20 10:00:00")
    ]
    create_test_db(db_file, product, offers)

    with patch("notifier.send_discord_alert") as mock_discord:
        notifier.check_price_alerts(db_name=db_file)

        assert mock_discord.called
        assert mock_discord.call_count == 1


def test_nincs_ertesites_ha_draga(tmp_path):
    """Ha a termék még drágább a célárnál, NEM szabad értesítést küldenie."""
    db_file = str(tmp_path / "test_no_alert.db")

    product = (1, "AMD Ryzen 7 7800X3D", "CPU", 150000)
    offers = [
        (1, "Foramax", 162900, "2026-10-20 10:00:00")
    ]
    create_test_db(db_file, product, offers)

    with patch("notifier.send_discord_alert") as mock_discord:
        notifier.check_price_alerts(db_name=db_file)

        assert not mock_discord.called


def test_discord_uzenet_tartalma(tmp_path):
    """Ellenőrzi, hogy a kiküldött Discord üzenetben benne van-e a termék, bolt és ár."""
    db_file = str(tmp_path / "test_msg.db")

    product = (1, "Kingston FURY Beast 32GB", "RAM", 50000)
    offers = [
        (1, "iPon", 45000, "2026-10-20 10:00:00")
    ]
    create_test_db(db_file, product, offers)

    with patch("notifier.send_discord_alert") as mock_discord:
        notifier.check_price_alerts(db_name=db_file)

        hivas_szovege = str(mock_discord.call_args)

        assert "Kingston FURY Beast 32GB" in hivas_szovege
        assert "45,000 Ft" in hivas_szovege or "45000" in hivas_szovege
        assert "iPon" in hivas_szovege