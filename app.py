from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey123'

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    price REAL
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '')
    sort = request.args.get('sort', '')

    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    query = "SELECT name, price FROM products WHERE name LIKE ?"
    params = [f"%{search}%"]

    if sort == "low-high":
        query += " ORDER BY price ASC"
    elif sort == "high-low":
        query += " ORDER BY price DESC"
    elif sort == "name-asc":
        query += " ORDER BY name ASC"
    elif sort == "name-desc":
        query += " ORDER BY name DESC"

    c.execute(query, params)
    products = [{'name': row[0], 'price': row[1]} for row in c.fetchall()]
    conn.close()

    return render_template('home.html', products=products, search=search)

@app.route('/', methods=['POST'])
def add_product():
    if 'username' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    price = request.form['price']
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password"
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Username already exists"
        finally:
            conn.close()
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)

