from app import db
from app.models import Role
from run import app

with app.app_context():
    db.create_all()

    # create or update user roles
    Role.insert_roles()
