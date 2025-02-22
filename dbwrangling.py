import os
import sqlite3
import pandas as pd

# 1. FILE PATHS
NUTRIENT_CSV = r"C:\Users\aahme\OneDrive\Desktop\Year3 CS\FYP\nutrient.csv"
FOOD_NUTRIENT_CSV = r"C:\Users\aahme\OneDrive\Desktop\Year3 CS\FYP\food_nutrient.csv"
DB_PATH = r"C:\Users\aahme\OneDrive\Documents\GitHub\Final-Year-Project\dii_tool.db"

# 2. LIST OF RELEVANT NUTRIENTS FROM dii_parameter
RELEVANT_NUTRIENTS = [
    "Alcohol, ethyl",
    "Vitamin B-12",
    "Vitamin B-12, added",
    "Vitamin B-12, intrinsic",
    "Vitamin B-6",
    "Vitamin B-6, pyridoxine, alcohol form",
    "Vitamin B-6, pyridoxal, aldehyde form",
    "Vitamin B-6, pyridoxamine, amine form",
    "Vitamin B-6, N411 + N412 +N413",
    "Carotene, beta",
    "Caffeine",
    "Carbohydrate, by difference",
    "Carbohydrate, by summation",
    "Carbohydrate, other",
    "Carbohydrates, other",
    "Cholesterol",
    "Energy (Atwater General Factors)",
    "Total lipid (fat)",
    "Fiber, total dietary",
    "Folic acid",
    "Iron, Fe",
    "Magnesium, Mg",
    "Fatty acids, total monounsaturated",
    "Niacin",
    "Protein",
    "Riboflavin",
    "Riboflavin, added",
    "Riboflavin, intrinsic",
    "Selenium, Se",
    "Thiamin",
    "Thiamin, added",
    "Thiamin, intrinsic",
    "Vitamin A, RE",
    "Vitamin C, total ascorbic acid",
    "Vitamin D (D2 + D3)",
    "Vitamin E",
    "Zinc, Zn",
    "Flavones, total",
    "Flavonols, total",
    "Flavanones, total",
    "Anthocyanidins",
    "Isoflavones",
    "Energy"
]

def main():
    """
    1. Reads the nutrient.csv and food_nutrient.csv from the SR Legacy dataset.
    2. Merges them to associate each nutrient_id with its 'name' and 'unit_name'.
    3. Filters rows to only keep the relevant nutrients from the dii_parameter table.
    4. Groups by nutrient name to compute the mean and std of 'amount'.
    5. Updates the dii_parameter table with these new 'food_mean' and 'food_std' values.
    """
    # --- 3A. Load CSV files ---
    if not os.path.exists(NUTRIENT_CSV):
        raise FileNotFoundError(f"Could not find {NUTRIENT_CSV}")
    if not os.path.exists(FOOD_NUTRIENT_CSV):
        raise FileNotFoundError(f"Could not find {FOOD_NUTRIENT_CSV}")

    nutrient_df = pd.read_csv(NUTRIENT_CSV)
    food_nutrient_df = pd.read_csv(FOOD_NUTRIENT_CSV)

    # Confirm the columns exist as expected
    # nutrient.csv => columns: [id, name, unit_name, nutrient_nbr, rank, ...]
    # food_nutrient.csv => columns: [id, fdc_id, nutrient_id, amount, data_points, derivation_id, ...]

    # --- 3B. Merge DataFrames on 'id' (nutrient.id) = 'nutrient_id' (food_nutrient.nutrient_id) ---
    merged_df = pd.merge(
        food_nutrient_df, 
        nutrient_df, 
        left_on="nutrient_id", 
        right_on="id",
        how="inner"
    )

    # merged_df now contains:
    #   amount, data_points, derivation_id, ...
    #   name, unit_name, nutrient_nbr, rank, ...
    # The key columns for us are: 'name', 'amount', 'unit_name'

    # --- 3C. Filter to keep only the relevant nutrients that appear in dii_parameter ---
    # We assume the names in RELEVANT_NUTRIENTS match the 'name' column in nutrient.csv exactly.
    subset_df = merged_df[ merged_df['name'].isin(RELEVANT_NUTRIENTS) ].copy()

    # (Optional) If you need to handle synonyms or slight name differences,
    # you'd do that mapping here.

    # --- 3D. Group by 'name' to compute mean and std of the 'amount' ---
    # The USDA SR Legacy data is typically per 100 g of edible portion.
    # So 'amount' is how many grams (or mg, etc.) per 100 g of food.
    stats_df = subset_df.groupby('name')['amount'].agg(['mean', 'std']).reset_index()
    stats_df.rename(columns={'mean': 'food_mean', 'std': 'food_std'}, inplace=True)

    print("Computed stats (first few rows):")
    print(stats_df.head())

    # --- 3E. Update dii_parameter table with these new values ---
    # We'll do:
    #   UPDATE dii_parameter
    #   SET food_mean = <food_mean_value>, food_std = <food_std_value>
    #   WHERE nutrient_name = <nutrient_name>
    #
    # Make sure your dii_parameter table has columns 'food_mean' and 'food_std'.
    #
    # If you haven't added them yet:
    # ALTER TABLE dii_parameter ADD COLUMN food_mean REAL;
    # ALTER TABLE dii_parameter ADD COLUMN food_std REAL;

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # For each row in stats_df, update dii_parameter
    for row in stats_df.itertuples(index=False):
        nutrient_name = row.name
        food_mean_val = row.food_mean
        food_std_val = row.food_std

        # Prepare the SQL statement
        # We do a case-insensitive match if needed, but let's assume exact match:
        cursor.execute("""
            UPDATE dii_parameter
            SET food_mean = ?,
                food_std = ?
            WHERE nutrient_name = ?
        """, (food_mean_val, food_std_val, nutrient_name))

    conn.commit()
    conn.close()

    print("Done updating dii_parameter with food_mean and food_std.")
    print("Note: Verify rows updated by checking your database or by printing cursor.rowcount etc.")

if __name__ == "__main__":
    main()
