from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Ingredient table
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'Grains', 'Proteins'
    portion_size = db.Column(db.Float, nullable=False)  # Default portion size in grams
    dii_score = db.Column(db.Float, nullable=True)  # Computed DII score

# Nutritional Data table
class NutritionalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    nutrient_name = db.Column(db.String(50), nullable=False)  # e.g., 'Carbohydrate (g)'
    amount_per_portion = db.Column(db.Float, nullable=False)  # e.g., grams or mg based on nutrient
    ingredient = db.relationship('Ingredient', backref=db.backref('nutrients', lazy=True))

# DII Parameters table
class DIIParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nutrient_name = db.Column(db.String(50), nullable=False, unique=True)  # Matches NutritionalData.nutrient_name
    dii_score_per_unit = db.Column(db.Float, nullable=False)  # DII score per unit (e.g., gram or mg)

class DII_NutrientParameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nutrient_id = db.Column(db.Integer, db.ForeignKey('dii_parameter.id'), nullable=False)
    mean = db.Column(db.Float, nullable=False)  # Mean value for the nutrient
    standard_deviation = db.Column(db.Float, nullable=False)  # Standard deviation for the nutrient
    inflammatory_weight = db.Column(db.Float, nullable=False)  # Inflammatory weight for the nutrient
    dii_parameter = db.relationship('DIIParameter', backref=db.backref('nutrient_params', lazy=True))

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    dii_score = db.Column(db.Float, nullable=False)