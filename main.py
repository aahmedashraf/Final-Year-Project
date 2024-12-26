import sqlite3, requests
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
# from db import log_food_entry  
from models import db, FoodLog  


app = Flask(__name__)

# Set up the database URI
db_path = r'C:\Users\aahme\OneDrive\Documents\GitHub\Final-Year-Project\dii_tool.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)
db_path = r'C:\Users\aahme\OneDrive\Documents\GitHub\Final-Year-Project\dii_tool.db'

# Your USDA API key
API_KEY = "sns0HxXgofxkqaeFcYRUpPzxcxoN7wy62Mf2Aq85"
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


# Function to fetch nutrient data from USDA API
def fetch_usda_data(ingredient):
    params = {
        "query": ingredient,
        "pageSize": 1,  # Limit results to the first match
        "api_key": API_KEY
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if "foods" in data and len(data["foods"]) > 0:
            return data["foods"][0].get("foodNutrients", [])
        else:
            print("No food data found for the ingredient.")
            return None
    else:
        print(f"API error: {response.status_code} - {response.text}")
        return None

# Function to calculate the DII score based on nutrient data
def calculate_dii_score(nutrients):
    total_score = 0
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for nutrient in nutrients:
            name = nutrient.get("nutrientName", "")
            amount = nutrient.get("value", 0)

            # Query for the DII score from the dii_parameter table
            cursor.execute("SELECT dii_score_per_unit FROM dii_parameter WHERE nutrient_name = ?", (name,))
            row = cursor.fetchone()

            if row:
                dii_score_per_unit = row[0]
                score = amount * dii_score_per_unit
                total_score += score
            
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        cursor.close()
        conn.close()

    return total_score


def log_food_entry(ingredient_name, quantity, dii_score):
    food_log_entry = FoodLog(ingredient_name=ingredient_name, quantity=quantity, dii_score=dii_score)
    db.session.add(food_log_entry)
    db.session.commit()
    print(f"Logged food entry: {ingredient_name}, Quantity: {quantity}, DII Score: {dii_score}")

# Flask route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to handle DII calculation
@app.route('/calculate_dii', methods=['POST'])
def calculate_dii():
    ingredient = request.json.get("ingredient")
    if not ingredient:
        return jsonify({"error": "No ingredient provided"}), 400

    nutrients = fetch_usda_data(ingredient)
    if nutrients:
        dii_score = calculate_dii_score(nutrients)
        return jsonify({"ingredient": ingredient, "dii_score": dii_score})
    else:
        return jsonify({"error": "Nutrient data not found"}), 404

@app.route('/test_fetch', methods=['GET'])
def test_fetch():
    ingredient = request.args.get("ingredient", "apple")  # Default ingredient is "apple"
    nutrients = fetch_usda_data(ingredient)
    
    if nutrients:
        return jsonify({"ingredient": ingredient, "nutrients": nutrients})
    else:
        return jsonify({"error": "Nutrient data not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)

