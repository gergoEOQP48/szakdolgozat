from flask import Flask, render_template
import sqlite3
import json
from analytics import calculate_price_trend

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect("hardware_prices.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    db.execute("SELECT * FROM products")
    items = db.fetchall()
    
    data = []
    for row in items:
        db.execute("""
            SELECT s.name AS shop_name, ph.price 
            FROM price_history ph
            JOIN shops s ON ph.shop_id = s.id
            WHERE ph.product_id = ? 
            ORDER BY ph.checked_at DESC, ph.price ASC 
            LIMIT 1
        """, (row["id"],))
        price_row = db.fetchone()
        
        p = dict(row)
        if price_row:
            p["best_price"] = price_row["price"]
            p["best_shop"] = price_row["shop_name"]
        else:
            p["best_price"] = 0
            p["best_shop"] = "-"
        data.append(p)
        
    conn.close()
    return render_template("index.html", products=data)


@app.route("/product/<int:product_id>")
def product_chart(product_id):
    conn = sqlite3.connect("hardware_prices.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = db.fetchone()
    
    if not product:
        conn.close()
        return "A termék nem található", 404
        
    db.execute("""
        SELECT s.name AS shop_name, ph.price, ph.checked_at 
        FROM price_history ph
        JOIN shops s ON ph.shop_id = s.id
        WHERE ph.product_id = ? 
        ORDER BY ph.checked_at ASC
    """, (product_id,))
    history = db.fetchall()
    history_list = [dict(h) for h in history]

    db.execute("""
        SELECT checked_at, MIN(price) AS price 
        FROM price_history 
        WHERE product_id = ? 
        GROUP BY checked_at 
        ORDER BY checked_at ASC
    """, (product_id,))
    best_price_history = [dict(h) for h in db.fetchall()]

    analysis = calculate_price_trend(best_price_history)
    
    conn.close()
    return render_template(
        "chart.html", 
        product=product, 
        history_json=json.dumps(history_list),
        analysis=analysis
    )

if __name__ == "__main__":
    app.run(debug=True)