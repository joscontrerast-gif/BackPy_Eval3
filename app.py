from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import decimal
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

# ---------------- HEALTH ENDPOINTS (PARA CI/CD) ----------------

@app.route("/")
def home():
    return jsonify({"message": "Backend Product Service running"}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# ---------------- DATABASE CONFIG ----------------

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'products_db')
}

def get_db_connection():
    max_retries = 10
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**db_config)

            if connection.is_connected():
                print("Connected to MySQL")
                return connection

        except Error as e:
            print(f"Attempt {attempt + 1}/{max_retries}: MySQL not ready ({e})")

            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    return None

# ---------------- INIT DB ----------------

def init_db():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                stock INT NOT NULL,
                icon VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()

# ---------------- ROUTES PRODUCTOS ----------------

@app.route('/api/products', methods=['GET'])
def get_all_products():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'DB error'}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    for p in products:
        if isinstance(p.get('price'), decimal.Decimal):
            p['price'] = float(p['price'])

    return jsonify(products)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'DB error'}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    connection.close()

    if not product:
        return jsonify({'error': 'Not found'}), 404

    if isinstance(product.get('price'), decimal.Decimal):
        product['price'] = float(product['price'])

    return jsonify(product)

# ---------------- MAIN ----------------

if __name__ == '__main__':
    init_db()

    port = int(os.getenv('PORT', 8082))
    print(f"Product service running on port {port}")

    app.run(host='0.0.0.0', port=5000)