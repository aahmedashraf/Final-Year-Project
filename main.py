from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import os
import requests
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
# from dotenv import load_dotenv  

# load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = "4f5f6d7e8a9b0c1d2e3f4a5b6c7d8e9f"

# Database path
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
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
            );
            CREATE TABLE IF NOT EXISTS food_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                food_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                dii_score REAL NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)
        conn.commit()

# Uncomment to initialize the database
# init_db()

def fetch_nutrient_data(food_name):
    """
    Fetch nutrient data for a food item using the USDA API.
    Filters for Foundation Foods and sorts by relevance.
    """
    try:
        params = {
            "query": food_name,
            "pageSize": 1,
            "type": "Foundation",  # Filter for Foundation Foods
            "sortBy": "score",
            "sortOrder": "desc",
            "api_key": USDA_API_KEY
        }
        response = requests.get(USDA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "foods" in data and len(data["foods"]) > 0:
            return data["foods"][0]["foodNutrients"]
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching nutrient data: {e}")
        return None

def calculate_food_breakdown(nutrient_data, quantity):
    """
    Generate a nutrient breakdown for a food entry.
    For each nutrient (with nonzero value and matching unit),
    retrieve its dii_score_per_unit from dii_parameter.
    
    Returns a breakdown list and a placeholder dii_score (set to 0).
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        breakdown = []
        placeholder_score = 0  # No individual food DII score
        for nutrient in nutrient_data:
            nutrient_name = nutrient.get("nutrientName")
            amount_per_100g = nutrient.get("value", 0)
            if amount_per_100g == 0:
                continue
            nutrient_unit = nutrient.get("unitName", "").lower()
            cursor.execute("""
                SELECT dii_score_per_unit, unit
                FROM dii_parameter 
                WHERE nutrient_name = ?
            """, (nutrient_name,))
            result = cursor.fetchone()
            if result:
                dii_score_per_unit, db_unit = result
                if nutrient_unit == db_unit.lower():
                    breakdown.append({
                        "nutrient_name": nutrient_name,
                        "dii_score_per_unit": dii_score_per_unit
                    })
            else:
                print(f"No parameter found for nutrient: {nutrient_name}")
        return placeholder_score, breakdown
    except sqlite3.Error as e:
        print(f"SQLite error in calculate_food_breakdown: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def calculate_daily_dii(user_id, date_str):
    """
    Compute the daily DII score for a user on a given date.
    
    Aggregates nutrient amounts from all food_log entries for that day.
    For each aggregated nutrient, retrieves global_mean, std_dev, and dii_score_per_unit
    from dii_parameter, computes:
         z_score = (total_amount - global_mean) / std_dev   (if std_dev exists)
         contribution = z_score * dii_score_per_unit (or a fallback)
    Returns a tuple: (daily_dii_score, daily_breakdown)
    where daily_breakdown is a list of nutrient contributions.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Fetch today's food entries
        cursor.execute("""
            SELECT food_name, quantity 
            FROM food_log 
            WHERE user_id = ? AND date = ?
        """, (user_id, date_str))
        entries = cursor.fetchall()
        print("Entries for date", date_str, ":", entries)  # Debug log
        
        nutrient_totals = {}
        for entry in entries:
            food_name, quantity = entry
            nutrient_data = fetch_nutrient_data(food_name)
            print("Nutrient data for", food_name, ":", nutrient_data)  # Debug log
            if not nutrient_data:
                continue
            for nutrient in nutrient_data:
                nutrient_name = nutrient.get("nutrientName")
                amount_per_100g = nutrient.get("value", 0)
                if amount_per_100g == 0:
                    continue
                # Calculate consumed amount for this nutrient from this food entry.
                amount = (amount_per_100g / 100) * quantity
                # Sum up amounts for each nutrient.
                nutrient_totals[nutrient_name] = nutrient_totals.get(nutrient_name, 0) + amount
        
        print("Aggregated Nutrient Totals:", nutrient_totals)  # Debug log
        
        daily_dii_score = 0
        daily_breakdown = []
        for nutrient_name, total_amount in nutrient_totals.items():
            cursor.execute("""
                SELECT dii_score_per_unit, global_mean, std_dev
                FROM dii_parameter
                WHERE nutrient_name = ?
            """, (nutrient_name,))
            result = cursor.fetchone()
            print("Lookup for", nutrient_name, "returned:", result)  # Debug log
            if result:
                dii_score_per_unit, global_mean, std_dev = result
                # Compute z_score only if std_dev is defined and nonzero.
                if std_dev and std_dev != 0:
                    z_score = (total_amount - global_mean) / std_dev
                else:
                    z_score = None
                # Calculate contribution using z_score if available; otherwise use fallback.
                contribution = z_score * dii_score_per_unit if z_score is not None else total_amount * dii_score_per_unit
                daily_dii_score += contribution
                # Append the breakdown for this nutrient.
                daily_breakdown.append({
                    "nutrient_name": nutrient_name,
                    "total_amount": total_amount,
                    "global_mean": global_mean,
                    "std_dev": std_dev,
                    "z_score": z_score,
                    "dii_score_per_unit": dii_score_per_unit,
                    "contribution": contribution
                })
            else:
                print(f"No dii_parameter entry found for {nutrient_name}")
        
        print("Final Daily DII Score:", daily_dii_score)
        print("Daily Breakdown:", daily_breakdown)
        return daily_dii_score, daily_breakdown
    except sqlite3.Error as e:
        print(f"SQLite error in daily aggregation: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def update_daily_score(user_id, score):
    today = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_data (user_id, date, total_dii_score)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
            total_dii_score = ?
        """, (user_id, today, score, score))
        conn.commit()

@app.route('/confirm_day', methods=['POST'])
def confirm_day():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        user_id = session['user_id']
        today = datetime.now().strftime("%Y-%m-%d")
        daily_dii, breakdown = calculate_daily_dii(user_id, today)
        if daily_dii is None:
            return jsonify({"error": "Failed to calculate daily DII score"}), 500
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_data (user_id, date, total_dii_score)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
            total_dii_score = ?
        """, (user_id, today, daily_dii, daily_dii))
        conn.commit()
        conn.close()
        return jsonify({"daily_dii_score": daily_dii, "breakdown": breakdown})
    except sqlite3.Error as e:
        print(f"Database error in confirm_day: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/get_daily_score', methods=['GET'])
def get_daily_score():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        user_id = session['user_id']
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT total_dii_score FROM daily_data
            WHERE user_id = ? AND date = ?
        """, (user_id, today))
        result = cursor.fetchone()
        conn.close()
        if result:
            return jsonify({"daily_dii_score": result[0]})
        else:
            return jsonify({"daily_dii_score": None})
    except sqlite3.Error as e:
        print(f"Database error in get_daily_score: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/entry_breakdown/<int:entry_id>', methods=['GET'])
def entry_breakdown(entry_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT food_name, quantity, dii_score 
            FROM food_log 
            WHERE id = ? AND user_id = ?
        """, (entry_id, session['user_id']))
        entry = cursor.fetchone()
        if not entry:
            return jsonify({"error": "Entry not found"}), 404
        nutrient_data = fetch_nutrient_data(entry[0])
        if not nutrient_data:
            return jsonify({"error": "Current nutrient data unavailable"}), 404
        placeholder_score, breakdown = calculate_food_breakdown(nutrient_data, entry[1])
        response_data = {
            "food_name": entry[0],
            "quantity": entry[1],
            "dii_score": entry[2],
            "breakdown": breakdown if breakdown else []
        }
        return jsonify(response_data)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, dii_score FROM food_log
            WHERE id = ? AND user_id = ?
        """, (entry_id, session['user_id']))
        entry = cursor.fetchone()
        if not entry:
            return jsonify({"error": "Entry not found"}), 404
        cursor.execute("""
            DELETE FROM food_log
            WHERE id = ? AND user_id = ?
        """, (entry_id, session['user_id']))
        # Update daily_data by subtracting this food's dii_score from the day's total.
        cursor.execute("""
            UPDATE daily_data
            SET total_dii_score = total_dii_score - ?
            WHERE user_id = ? AND date = ?
        """, (entry[1], session['user_id'], entry[0]))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error in delete_entry: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

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
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
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
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'password' not in columns:
            return jsonify({"success": False, "error": "Database schema is invalid"}), 500
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
    except sqlite3.Error as e:
        print(f"Database error in login: {e}")
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
    if not food_name or not quantity:
        return jsonify({"error": "Food name and quantity are required"}), 400
    try:
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid quantity - must be a positive number"}), 400
    nutrient_data = fetch_nutrient_data(food_name)
    if not nutrient_data:
        return jsonify({"error": f"Nutrient data for '{food_name}' not found"}), 404
    dii_score, breakdown = calculate_food_breakdown(nutrient_data, quantity)
    if dii_score is None:
        return jsonify({"error": "Failed to process nutrient data"}), 500
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO food_log (user_id, date, food_name, quantity, dii_score)
            VALUES (?, ?, ?, ?, ?)
        """, (session['user_id'], today, food_name, quantity, dii_score))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error in /calculate: {e}")
        return jsonify({"error": "Failed to save food entry"}), 500
    finally:
        conn.close()
    return jsonify({
        "food_name": food_name,
        "quantity": quantity,
        "dii_score": dii_score,
        "breakdown": breakdown
    })

@app.route('/usda-proxy')
def usda_proxy():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    try:
        params = {
            "query": query,
            "pageSize": 10,
            "type": "Foundation",  # Filter for Foundation Foods
            "sortBy": "score",
            "sortOrder": "desc",
            "api_key": USDA_API_KEY
        }
        response = requests.get(USDA_API_URL, params=params)
        response.raise_for_status()
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
            SELECT id, food_name, quantity 
            FROM food_log 
            WHERE user_id = ? AND date = ?
            ORDER BY id DESC
        """, (user_id, today))
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)
    except sqlite3.Error as e:
        print(f"Database error in daily_data: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

@app.route('/weekly_data')
def weekly_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user_id = session['user_id']
    dates = []
    scores = []
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
