from flask_sqlalchemy import SQLAlchemy
from main import app  # Importing the Flask app from main.py
from models import db

# Set the absolute path to the database in the project folder
# project_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Get the path to your project folder
# os.path.join(project_folder, 'dii_tool.db')  # Create the path to the database file

db_path = r'C:\Users\aahme\OneDrive\Documents\GitHub\Final-Year-Project\dii_tool.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'  # Update the URI with the full path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Initialize the database (creating tables)
def initialize_db():
    with app.app_context():
        db.create_all()  # Create tables
        print("Database and tables created successfully!")

# Run the database initialization
# initialize_db()
