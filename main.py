from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import requests

app = Flask(__name__)

# Path to your SQLite database
db_path = os.path.join(os.path.dirname(__file__), 'dii_tool.db')

# USDA API configuration
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_API_KEY = "sns0HxXgofxkqaeFcYRUpPzxcxoN7wy62Mf2Aq85"  # Replace with your USDA API key

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """
    API endpoint to calculate the DII score based on user input.
    Returns a detailed breakdown of the score calculation.
    """
    data = request.json
    food_name = data.get('food_name')
    quantity = data.get('quantity')

    if not food_name or not quantity:
        return jsonify({"error": "Food name and quantity are required."}), 400

    try:
        quantity = float(quantity)  # Ensure quantity is numeric
    except ValueError:
        return jsonify({"error": "Invalid quantity value. It must be numeric."}), 400

    # Fetch nutrient data from the USDA API
    nutrient_data = fetch_nutrient_data(food_name)

    if not nutrient_data:
        return jsonify({"error": f"Nutrient data for '{food_name}' not found."}), 404

    # Calculate the DII score and get the breakdown
    total_dii_score, breakdown = calculate_dii_score(nutrient_data, quantity)

    if total_dii_score is not None:
        return jsonify({
            "food_name": food_name,
            "quantity": quantity,
            "dii_score": total_dii_score,
            "breakdown": breakdown  # Add the breakdown to the response
        })
    else:
        return jsonify({"error": "Error calculating DII score."}), 500

if __name__ == '__main__':
    app.run(debug=True)
