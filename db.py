from main import app, db  # Importing the Flask app and db instance
import os

db_path = r'C:\Users\aahme\OneDrive\Documents\GitHub\Final-Year-Project\dii_tool.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'  # Update the URI with the full path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize the database (creating tables)
def initialize_db():
    with app.app_context():
        db.create_all()  # Create tables
        print("Database and tables created successfully!")

# Run the database initialization
# initialize_db()
