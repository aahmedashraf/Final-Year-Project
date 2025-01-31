from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import os
import requests
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv  

load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = "4f5f6d7e8a9b0c1d2e3f4a5b6c7d8e9f"

# Database path
# db_path = os.path.join(os.path.dirname(__file__), 'dii_tool.db')
db_path = r'C:\Users\aahme\OneDrive\Documents\GitHub\Final-Year-Project\dii_tool.db'

# USDA API Config
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_API_KEY = "sns0HxXgofxkqaeFcYRUpPzxcxoN7wy62Mf2Aq85"

# --- Database Initialization (Run once) ---
def init_db():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS daily_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                total_dii_score REAL DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)
        conn.commit()

# Initialize the database
# init_db()

def fetch_nutrient_data(food_name):
    """
    Fetch nutrient data for a food item using the USDA API.
    """
    try:
        params = {
            "query": food_name,
            "pageSize": 1,
            "api_key": USDA_API_KEY
        }
        response = requests.get(USDA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract nutrient data from the first result
        if "foods" in data and len(data["foods"]) > 0:
            return data["foods"][0]["foodNutrients"]
        else:
            return None  # No nutrient data found

    except requests.RequestException as e:
        print(f"Error fetching nutrient data: {e}")
        return None

def calculate_dii_score(nutrient_data, quantity):
    """
    Calculate the total DII score for a food item based on nutrient data and quantity.
    Provides a detailed breakdown of the score calculation.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        total_dii_score = 0
        breakdown = []  # To store the breakdown for each nutrient

        for nutrient in nutrient_data:
            nutrient_name = nutrient.get("nutrientName")
            amount_per_100g = nutrient.get("value", 0)
            nutrient_unit = nutrient.get("unitName", "").lower()  # Convert to lowercase

            # Query the DII score per unit and unit from the dii_parameter table
            cursor.execute(""" 
                SELECT dii_score_per_unit, unit FROM dii_parameter 
                WHERE nutrient_name = ?
            """, (nutrient_name,))
            result = cursor.fetchone()

            if result:
                dii_score_per_unit, db_unit = result
                db_unit = db_unit.lower()  # Convert to lowercase for case-insensitive comparison

                # Compare units before proceeding with the calculation
                if nutrient_unit == db_unit:
                    # Adjust the amount based on the user's input quantity
                    adjusted_amount = (amount_per_100g / 100) * quantity
                    nutrient_dii_score = adjusted_amount * dii_score_per_unit
                    
                    total_dii_score += nutrient_dii_score

                    # Add the breakdown for this nutrient
                    breakdown.append({
                        "nutrient_name": nutrient_name,
                        "amount_per_100g": amount_per_100g,
                        "adjusted_amount": adjusted_amount,
                        "dii_score_per_unit": dii_score_per_unit,
                        "nutrient_dii_score": nutrient_dii_score
                    })
                else:
                    print(f"Skipping nutrient {nutrient_name} due to unit mismatch (USDA: {nutrient_unit}, DB: {db_unit})")

        return total_dii_score, breakdown

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def update_daily_score(user_id, score):
    today = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Update or insert daily total
        cursor.execute("""
            INSERT INTO daily_data (user_id, date, total_dii_score)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
            total_dii_score = total_dii_score + excluded.total_dii_score
        """, (user_id, today, score))
        conn.commit()

# --- Routes ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = generate_password_hash(data.get('password'))

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                          (username, password))
            conn.commit()
            return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Username exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Verify the password column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'password' not in columns:
            return jsonify({"success": False, "error": "Database schema is invalid"}), 500

        # Proceed with login
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"success": False, "error": "Database error"}), 500

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    food_name = data.get('food_name')
    quantity = data.get('quantity')

    # Validate input
    if not food_name or not quantity:
        return jsonify({"error": "Food name and quantity are required"}), 400

    try:
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid quantity - must be a positive number"}), 400

    # Fetch nutrient data
    nutrient_data = fetch_nutrient_data(food_name)
    if not nutrient_data:
        return jsonify({"error": f"Nutrient data for '{food_name}' not found"}), 404

    # Calculate DII score
    dii_score, breakdown = calculate_dii_score(nutrient_data, quantity)
    if dii_score is None:
        return jsonify({"error": "Failed to calculate inflammation score"}), 500

    # Log food entry and update daily total
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert into food_log
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO food_log (user_id, date, food_name, quantity, dii_score)
            VALUES (?, ?, ?, ?, ?)
        """, (session['user_id'], today, food_name, quantity, dii_score))
        
        # Update daily_data using UPSERT
        cursor.execute("""
            INSERT INTO daily_data (user_id, date, total_dii_score)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
            total_dii_score = total_dii_score + excluded.total_dii_score
        """, (session['user_id'], today, dii_score))
        
        conn.commit()
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to save data"}), 500
    finally:
        conn.close()

    return jsonify({
        "food_name": food_name,
        "quantity": quantity,
        "dii_score": round(dii_score, 2),
        "breakdown": breakdown
    })

# from werkzeug.security import generate_password_hash
# print(generate_password_hash('123123'))
@app.route('/usda-proxy')
def usda_proxy():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        params = {
            "query": query,
            "pageSize": 10,  # Limit results to 10
            "api_key": USDA_API_KEY
        }
        response = requests.get(USDA_API_URL, params=params)
        response.raise_for_status()  # Raise HTTP errors
        return jsonify(response.json())
    except requests.RequestException as e:
        print(f"USDA API error: {e}")
        return jsonify({"error": "Failed to fetch food data"}), 500
    

@app.route('/daily_data')
def daily_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT food_name, quantity, dii_score 
            FROM food_log 
            WHERE user_id = ? AND date = ?
        """, (user_id, today))
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500


@app.route('/weekly_data')
def weekly_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    dates = []
    scores = []

    # Get data for last 7 days
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT total_dii_score FROM daily_data
                WHERE user_id = ? AND date = ?
            """, (user_id, date))
            result = cursor.fetchone()
        scores.append(result[0] if result else 0)
        dates.append(date)

    return jsonify({"dates": dates, "scores": scores})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)