from flask import Flask, render_template
import sqlite3

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
        db.execute("SELECT shop_name, price FROM price_history WHERE product_id = ? ORDER BY checked_at DESC, price ASC LIMIT 1", (row["id"],))
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

if __name__ == "__main__":
    app.run(debug=True)