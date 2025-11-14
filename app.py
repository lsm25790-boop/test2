from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'inventory.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS items (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               required_qty INTEGER NOT NULL,
               stock_qty INTEGER NOT NULL
           )'''
    )
    conn.commit()
    conn.close()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', shortage_items=None)


@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get('name')
    required_qty = request.form.get('required_qty')
    stock_qty = request.form.get('stock_qty')

    if not name or required_qty is None or stock_qty is None:
        return redirect(url_for('index'))

    try:
        required_qty = int(required_qty)
        stock_qty = int(stock_qty)
    except ValueError:
        return redirect(url_for('index'))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO items (name, required_qty, stock_qty) VALUES (?, ?, ?)',
        (name, required_qty, stock_qty),
    )
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/check', methods=['GET'])
def check_stock():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'SELECT name, required_qty, stock_qty FROM items WHERE required_qty > stock_qty'
    )
    rows = cur.fetchall()
    conn.close()

    shortage_items = []
    for name, required_qty, stock_qty in rows:
        shortage = stock_qty - required_qty
        shortage_items.append(
            {
                'name': name,
                'required_qty': required_qty,
                'stock_qty': stock_qty,
                'shortage': shortage,
            }
        )

    return render_template('index.html', shortage_items=shortage_items)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
