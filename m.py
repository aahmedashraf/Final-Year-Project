import sqlite3
import os

# Path to your SQLite database
db_path = os.path.join(os.path.dirname(__file__), 'dii_tool.db')

# Function to add data to the DIIParameter table
def add_dii_parameter(nutrient_name, dii_score_per_unit):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert new record into DIIParameter (using the correct table name)
        cursor.execute("""
            INSERT INTO dii_parameter (nutrient_name, dii_score_per_unit)
            VALUES (?, ?)
        """, (nutrient_name, dii_score_per_unit))

        # Commit the transaction
        conn.commit()
        print(f"Added {nutrient_name} with DII score {dii_score_per_unit}.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        cursor.close()
        conn.close()


# Function to populate data to the DIIParameter table
def populate_dii_parameters():
    dii_parameters = [
        {"nutrient_name": "Alcohol", "dii_score_per_unit": -0.278},
    {"nutrient_name": "Vitamin B12", "dii_score_per_unit": -0.106},
    {"nutrient_name": "Vitamin B6", "dii_score_per_unit": -0.365},
    {"nutrient_name": "Beta-Carotene", "dii_score_per_unit": -0.584},
    {"nutrient_name": "Caffeine", "dii_score_per_unit": 0.085},
    {"nutrient_name": "Carbohydrate", "dii_score_per_unit": 0.097},
    {"nutrient_name": "Cholesterol", "dii_score_per_unit": -0.037},
    {"nutrient_name": "Energy", "dii_score_per_unit": -0.180},
    {"nutrient_name": "Eugenol", "dii_score_per_unit": -0.868},
    {"nutrient_name": "Total Fat", "dii_score_per_unit": 0.298},
    {"nutrient_name": "Fibre", "dii_score_per_unit": -0.663},
    {"nutrient_name": "Folic Acid", "dii_score_per_unit": -0.182},
    {"nutrient_name": "Garlic", "dii_score_per_unit": -0.743},
    {"nutrient_name": "Ginger", "dii_score_per_unit": -0.453},
    {"nutrient_name": "Iron (Fe)", "dii_score_per_unit": -0.032},
    {"nutrient_name": "Magnesium (Mg)", "dii_score_per_unit": -0.484},
    {"nutrient_name": "MUFA", "dii_score_per_unit": 0.021},
    {"nutrient_name": "Niacin", "dii_score_per_unit": -0.246},
    {"nutrient_name": "Omega-3 Fatty Acids", "dii_score_per_unit": -0.436},
    {"nutrient_name": "Omega-6 Fatty Acids", "dii_score_per_unit": -0.159},
    {"nutrient_name": "Onion", "dii_score_per_unit": -0.509},
    {"nutrient_name": "Protein", "dii_score_per_unit": 0.021},
    {"nutrient_name": "PUFA", "dii_score_per_unit": -0.237},
    {"nutrient_name": "Riboflavin", "dii_score_per_unit": -0.727},
    {"nutrient_name": "Saffron", "dii_score_per_unit": -0.168},
    {"nutrient_name": "Saturated Fat", "dii_score_per_unit": 0.429},
    {"nutrient_name": "Selenium (Se)", "dii_score_per_unit": -0.191},
    {"nutrient_name": "Thiamin", "dii_score_per_unit": 0.098},
    {"nutrient_name": "Trans Fat", "dii_score_per_unit": 0.229},
    {"nutrient_name": "Turmeric", "dii_score_per_unit": -0.785},
    {"nutrient_name": "Vitamin A", "dii_score_per_unit": -0.401},
    {"nutrient_name": "Vitamin C", "dii_score_per_unit": -0.424},
    {"nutrient_name": "Vitamin D", "dii_score_per_unit": -0.446},
    {"nutrient_name": "Vitamin E", "dii_score_per_unit": -0.536},
    {"nutrient_name": "Zinc (Zn)", "dii_score_per_unit": -0.313},
    {"nutrient_name": "Green/Black Tea", "dii_score_per_unit": -0.536},
    {"nutrient_name": "Flavan-3-ol", "dii_score_per_unit": -0.615},
    {"nutrient_name": "Flavones", "dii_score_per_unit": -0.616},
    {"nutrient_name": "Flavonols", "dii_score_per_unit": -0.467},
    {"nutrient_name": "Flavanones", "dii_score_per_unit": -0.508},
    {"nutrient_name": "Anthocyanidins", "dii_score_per_unit": -0.449},
    {"nutrient_name": "Isoflavones", "dii_score_per_unit": -0.593},
    {"nutrient_name": "Pepper", "dii_score_per_unit": -0.397},
    {"nutrient_name": "Thyme/Oregano", "dii_score_per_unit": -0.102},
    {"nutrient_name": "Rosemary", "dii_score_per_unit": -0.013},
        
        # Add other nutrients with their respective DII scores
    ]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for param in dii_parameters:
            cursor.execute("""
                INSERT OR IGNORE INTO dii_parameter (nutrient_name, dii_score_per_unit)
                VALUES (?, ?)
            """, (param["nutrient_name"], param["dii_score_per_unit"]))

        conn.commit()
        print("DII parameters populated successfully!")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to query all DII parameters
# def query_all_dii_parameters():
#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()

#         # Query the DIIParameter table (using the correct table name)
#         cursor.execute("SELECT * FROM dii_parameter")
#         rows = cursor.fetchall()

#         for row in rows:
#             print(row)

#     except sqlite3.Error as e:
#         print(f"SQLite error: {e}")
#     finally:
#         cursor.close()
#         conn.close()

# Function to delete a DII parameter by nutrient name
def delete_dii_parameter(nutrient_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Delete record from DIIParameter where nutrient_name matches
        cursor.execute("""
            DELETE FROM dii_parameter
            WHERE nutrient_name = ?
        """, (nutrient_name,))

        # Commit the transaction
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Deleted {nutrient_name} from dii_parameter.")
        else:
            print(f"No entry found with nutrient name: {nutrient_name}.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        cursor.close()
        conn.close()

# Example usage
# Uncomment to test the function
# delete_dii_parameter('Vitamin B-12')

# if __name__ == "__main__":
#     populate_dii_parameters()

    # Example usage
    # Add a new DII Parameter (you can call this function wherever needed)
    # add_dii_parameter('Carbohydrate (g)', 1.2)

    # delete_dii_parameter('Carbohydrate (g)')
    # Query all DII parameters
    # query_all_dii_parameters()
# print(f"Database path: {db_path}")
