from flask.templating import render_template
from flask_login.utils import login_required
from .routes import users
from app.models import Permission
from flask_login import current_user

@users.app_context_processor
def inject_permissions():
    return {"Permission": Permission}


    
