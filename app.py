from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():

    conn = sqlite3.connect('hardware_prices.db')
    conn.row_factory = sqlite3.Row
    
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    conn.close()
    
    
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)