from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# DII Parameters table
class DIIParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nutrient_name = db.Column(db.String(50), nullable=False, unique=True)  # Matches NutritionalData.nutrient_name
    dii_score_per_unit = db.Column(db.Float, nullable=False)  # DII score per unit (e.g., gram or mg)
    unit = db.Column(db.String(20), nullable=True)  # Add unit column
