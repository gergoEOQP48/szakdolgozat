import sqlite3
from datetime import datetime, timedelta

DB_NAME = "hardware_prices.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


    