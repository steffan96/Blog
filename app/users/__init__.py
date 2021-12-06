from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required

from app.models import Permission

from .routes import users


@users.app_context_processor
def inject_permissions():
    return {"Permission": Permission}
