import sqlite3
import os

db_path = r'C:\Users\aahme\OneDrive\Documents\GitHub\Final-Year-Project\instance\dii_tool.db'

# Function to add data to the DIIParameter table
def add_dii_parameter(nutrient_name, dii_score_per_unit, unit):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert new record into DIIParameter with the unit
        cursor.execute("""
            INSERT INTO dii_parameter (nutrient_name, dii_score_per_unit, unit)
            VALUES (?, ?, ?)
        """, (nutrient_name, dii_score_per_unit, unit))

        conn.commit()
        print(f"Added {nutrient_name} with DII score {dii_score_per_unit} and unit {unit}.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        cursor.close()
        conn.close()


# Function to delete all DII parameters
def delete_all_dii_parameters():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Delete all records from DIIParameter table
        cursor.execute("DELETE FROM dii_parameter")

        # Commit the transaction
        conn.commit()
        print(f"All records deleted from the dii_parameter table.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to populate data to the DIIParameter table
def populate_dii_parameters():
    dii_parameters = [
        {"nutrient_name": "Alcohol, ethyl", "dii_score_per_unit": -0.278,  "unit": "g"},
    {"nutrient_name": "Vitamin B-12", "dii_score_per_unit": 0.106,  "unit": "ug"},
    {"nutrient_name": "Vitamin B-12, added", "dii_score_per_unit": 0.106,  "unit": "ug"},
    {"nutrient_name": "Vitamin B-12, intrinsic", "dii_score_per_unit": 0.106,  "unit": "ug"},
    {"nutrient_name": "Vitamin B-6", "dii_score_per_unit": -0.365,  "unit": "mg"},
    {"nutrient_name": "Vitamin B-6, pyridoxine, alcohol form", "dii_score_per_unit": -0.365,  "unit": "mg"},
    {"nutrient_name": "Vitamin B-6, pyridoxal, aldehyde form", "dii_score_per_unit": -0.365,  "unit": "mg"},
    {"nutrient_name": "Vitamin B-6, pyridoxamine, amine form", "dii_score_per_unit": -0.365,  "unit": "mg"},
    {"nutrient_name": "Vitamin B-6, N411 + N412 +N413", "dii_score_per_unit": -0.365,  "unit": "mg"},
    {"nutrient_name": "Carotene, beta", "dii_score_per_unit": -0.584,  "unit": "ug"},
    {"nutrient_name": "Caffeine", "dii_score_per_unit": -0.00011,  "unit": "mg"},
    {"nutrient_name": "Carbohydrate, by difference", "dii_score_per_unit": 0.097,  "unit": "g"},
    {"nutrient_name": "Carbohydrate, by summation", "dii_score_per_unit": 0.097,  "unit": "g"},
    {"nutrient_name": "Carbohydrate, other", "dii_score_per_unit": 0.097,  "unit": "g"},
    {"nutrient_name": "Carbohydrates, other", "dii_score_per_unit": 0.097,  "unit": "g"},
    {"nutrient_name": "Cholesterol", "dii_score_per_unit": 0.110,  "unit": "mg"},
    {"nutrient_name": "Energy (Atwater General Factors)", "dii_score_per_unit": 0.180,  "unit": "kcal"},
    # {"nutrient_name": "Energy (Atwater Specific Factors)", "dii_score_per_unit": 0.180,  "unit": "kcal"},
    # {"nutrient_name": "Energy", "dii_score_per_unit": 0.180,  "unit": "kcal"},
    # {"nutrient_name": "Eugenol", "dii_score_per_unit": -0.868,  "unit": "mg"},
    {"nutrient_name": "Total lipid (fat)", "dii_score_per_unit": 0.298,  "unit": "g"},
    {"nutrient_name": "Fiber, total dietary", "dii_score_per_unit": -0.663,  "unit": "g"},
    {"nutrient_name": "Folic acid", "dii_score_per_unit": -0.190,  "unit": "ug"},
    # {"nutrient_name": "Garlic", "dii_score_per_unit": -0.743,  "unit": "g"},
    # {"nutrient_name": "Ginger", "dii_score_per_unit": -0.453,  "unit": "g"},
    {"nutrient_name": "Iron, Fe", "dii_score_per_unit": 0.032,  "unit": "mg"},
    {"nutrient_name": "Magnesium, Mg", "dii_score_per_unit": -0.484,  "unit": "mg"},
    {"nutrient_name": "Fatty acids, total monounsaturated", "dii_score_per_unit": -0.009,  "unit": "g"},
    {"nutrient_name": "Niacin", "dii_score_per_unit": -0.246,  "unit": "mg"},
    # {"nutrient_name": "Omega-3 Fatty Acids", "dii_score_per_unit": -0.436,  "unit": "g"},
    # {"nutrient_name": "Omega-6 Fatty Acids", "dii_score_per_unit": -0.159,  "unit": "g"},
    # {"nutrient_name": "Onion", "dii_score_per_unit": -0.509,  "unit": "g"},
    {"nutrient_name": "Protein", "dii_score_per_unit": 0.021,  "unit": "g"},
    # {"nutrient_name": "PUFA", "dii_score_per_unit": -0.237,  "unit": "g"},
    {"nutrient_name": "Riboflavin", "dii_score_per_unit": -0.068,  "unit": "mg"},
    {"nutrient_name": "Riboflavin, added", "dii_score_per_unit": -0.068,  "unit": "mg"},
    {"nutrient_name": "Riboflavin, intrinsic", "dii_score_per_unit": -0.068,  "unit": "mg"},
    # {"nutrient_name": "Saffron", "dii_score_per_unit": -0.140,  "unit": "g"},
    # {"nutrient_name": "Saturated Fat", "dii_score_per_unit": 0.429,  "unit": "g"},
    {"nutrient_name": "Selenium, Se", "dii_score_per_unit": -0.191,  "unit": "ug"},
    {"nutrient_name": "Thiamin", "dii_score_per_unit": -0.098,  "unit": "mg"},
    {"nutrient_name": "Thiamin, added", "dii_score_per_unit": -0.098,  "unit": "mg"},
    {"nutrient_name": "Thiamin, intrinsic", "dii_score_per_unit": -0.098,  "unit": "mg"},
    # {"nutrient_name": "Trans Fat", "dii_score_per_unit": 0.229,  "unit": "g"},
    # {"nutrient_name": "Turmeric", "dii_score_per_unit": -0.785,  "unit": "g"},
    {"nutrient_name": "Vitamin A, RE", "dii_score_per_unit": -0.401,  "unit": "mcg_re"},
    {"nutrient_name": "Vitamin C, total ascorbic acid", "dii_score_per_unit": -0.424,  "unit": "mg"},
    {"nutrient_name": "Vitamin D (D2 + D3)", "dii_score_per_unit": -0.446,  "unit": "ug"},
    {"nutrient_name": "Vitamin E", "dii_score_per_unit": -0.419,  "unit": "mg"},
    {"nutrient_name": "Zinc, Zn", "dii_score_per_unit": -0.313,  "unit": "mg"},
    # {"nutrient_name": "Green/Black Tea", "dii_score_per_unit": -0.536,  "unit": "g"},
    # {"nutrient_name": "Flavan-3-ol", "dii_score_per_unit": -0.615,  "unit": "g"},
    {"nutrient_name": "Flavones, total", "dii_score_per_unit": -0.616,  "unit": "mg"},
    {"nutrient_name": "Flavonols, total", "dii_score_per_unit": -0.467,  "unit": "mg"},
    {"nutrient_name": "Flavanones, total", "dii_score_per_unit": -0.250,  "unit": "mg"},
    {"nutrient_name": "Anthocyanidins", "dii_score_per_unit": -0.131,  "unit": "mg"},
    {"nutrient_name": "Isoflavones", "dii_score_per_unit": -0.593,  "unit": "mg"},
    # {"nutrient_name": "Pepper", "dii_score_per_unit": -0.397,  "unit": "g"},
    # {"nutrient_name": "Thyme/Oregano", "dii_score_per_unit": -0.102,  "unit": "g"},
    # {"nutrient_name": "Rosemary", "dii_score_per_unit": -0.013,  "unit": "g"},
        
        # Add other nutrients with their respective DII scores
    ]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for param in dii_parameters:
            cursor.execute("""
                INSERT OR IGNORE INTO dii_parameter (nutrient_name, dii_score_per_unit, unit)
                VALUES (?, ?, ?)
            """, (param["nutrient_name"], param["dii_score_per_unit"], param["unit"]))

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
#         rows = cursor.fetchall(s)

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

if __name__ == "__main__":
    # delete_all_dii_parameters()
    populate_dii_parameters()

    # Example usage
    # Add a new DII Parameter (you can call this function wherever needed)
    # add_dii_parameter('Carbohydrate (g)', 1.2)

    # delete_dii_parameter('Carbohydrate (g)')
    # Query all DII parameters
    # query_all_dii_parameters()
# print(f"Database path: {db_path}")
