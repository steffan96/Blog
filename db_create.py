from app import db
from run import app
from app.models import Role


with app.app_context():
    db.create_all()
    
    #create or update user roles
    Role.insert_roles()