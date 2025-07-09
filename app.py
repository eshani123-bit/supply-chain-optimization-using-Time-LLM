from flask import Flask, render_template, request, redirect, url_for, session
from model.predictor import predict_demand
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret_key_123'  # Needed for session

# Database config
db_config = {
    'host': 'localhost',
    'port': '3307',
    'user': 'root',
    'password': 'eshani@2004',
    'database': 'supply_chain'
}


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session.clear()
            session['username'] = user[0]
            session['role'] = user[1]  # store role in session
            return redirect(url_for('index'))

        
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('login.html', error=error)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    prediction = None
    forecast_data = []
    product = None

    if request.method == 'POST':
        product = request.form['product']
        prediction, forecast_data = predict_demand(product)

    return render_template('index.html', prediction=prediction, product=product, forecast_data=forecast_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing = cursor.fetchone()

        if existing:
            error = "Username already taken. Please choose another."
        else:
            role = request.form['role']
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
            conn.commit()
            message = "Registration successful! You can now log in."

    return render_template("register.html", error=error, message=message)
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 🔹 Top-selling product
    cursor.execute("SELECT product, SUM(sales) as total FROM sales_data GROUP BY product ORDER BY total DESC LIMIT 1")
    top_row = cursor.fetchone()
    top_product = top_row[0]
    total_sales = top_row[1]

    # 📈 Sales trend (last 7 days)
    cursor.execute("""
        SELECT date, SUM(sales) 
        FROM sales_data 
        WHERE date >= CURDATE() - INTERVAL 7 DAY
        GROUP BY date 
        ORDER BY date
    """)
    trend = cursor.fetchall()
    trend_data = [(row[0].strftime('%Y-%m-%d'), row[1]) for row in trend]

    # 📊 Total sales per product (bar chart)
    cursor.execute("SELECT product, SUM(sales) FROM sales_data GROUP BY product")
    product_sales = cursor.fetchall()
    product_names = [row[0] for row in product_sales]
    product_totals = [row[1] for row in product_sales]

    # ⚠ Inventory alerts
    alerts = []
    cursor.execute("SELECT product, current_stock, reorder_level FROM inventory")
    inventory_data = cursor.fetchall()

    for product, current_stock, reorder_level in inventory_data:
        if current_stock < reorder_level:
            alerts.append(f"⚠ Low stock for {product}! Only {current_stock} units left. Reorder level is {reorder_level}.")

    return render_template("dashboard.html",
                           username=session['username'],
                           top_product=top_product,
                           total_sales=total_sales,
                           trend_data=trend_data,
                           product_names=product_names,
                           product_totals=product_totals,
                           alerts=alerts)
import pandas as pd
import os

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    file = request.files['csv_file']
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)

        # Validate required columns
        if not {'date', 'product', 'sales'}.issubset(df.columns):
            return "Invalid CSV format. Required: date, product, sales"

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO sales_data (date, product, sales) VALUES (%s, %s, %s)",
                (row['date'], row['product'], int(row['sales']))
            )
        conn.commit()
        cursor.execute("""
            UPDATE inventory i
            JOIN (
                SELECT product, SUM(sales) AS sold
                FROM sales_data
                WHERE date = CURDATE()
                GROUP BY product
            ) s ON i.product = s.product
            SET i.current_stock = i.current_stock - s.sold
            WHERE i.product = s.product
        """)
        conn.commit()

        return redirect(url_for('dashboard'))


    return "Upload failed. Please upload a valid .csv file."
@app.route('/recommendations')
def recommendations():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Get distinct products
    cursor.execute("SELECT DISTINCT product FROM sales_data")
    products = [row[0] for row in cursor.fetchall()]

    from model.predictor import predict_demand
    recommendations = []

    for product in products:
        try:
            predicted, _ = predict_demand(product)
            recommendations.append((product, predicted))
        except:
            pass  # Skip if error in prediction (not enough data etc.)

    # Sort products by predicted demand
    recommendations.sort(key=lambda x: x[1], reverse=True)

    top_recommend = recommendations[:3]
    low_recommend = recommendations[-3:]

    return render_template("recommendations.html",
                           username=session['username'],
                           top_recommend=top_recommend,
                           low_recommend=low_recommend)
@app.route('/logistics')
def logistics():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch inventory data
    cursor.execute("SELECT product, current_stock, reorder_level, safety_stock FROM inventory")
    rows = cursor.fetchall()

    from model.predictor import predict_demand

    recommendations = []
    for product, stock, reorder, safety in rows:
        try:
            predicted, _ = predict_demand(product.lower())
            required = predicted + safety
            gap = required - stock
            status = 'Sufficient'
            if stock < reorder:
                status = '⚠ Below Reorder Level'
            if gap > 0:
                status = '🚨 Restock Needed'

            recommendations.append({
                'product': product,
                'predicted': predicted,
                'stock': stock,
                'required': required,
                'gap': gap,
                'status': status
            })
        except:
            continue


    return render_template("logistics.html", recommendations=recommendations)
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if request.method == 'POST':
        product = request.form['product']
        current = request.form['current_stock']
        reorder = request.form['reorder_level']
        safety = request.form['safety_stock']
        max_cap = request.form['max_capacity']

        cursor.execute("""
            UPDATE inventory 
            SET current_stock=%s, reorder_level=%s, safety_stock=%s, max_capacity=%s
            WHERE product=%s
        """, (current, reorder, safety, max_cap, product))
        conn.commit()

    cursor.execute("SELECT * FROM inventory")
    data = cursor.fetchall()
    return render_template("inventory.html", inventory=data)
if __name__ == '__main__':
    app.run(debug=True)