from app import db
from run import app



with app.app_context():
    db.create_all()