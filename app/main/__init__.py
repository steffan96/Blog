from .routes import main
from blogproject.models import Permission

@main.app_context_processor
def inject_permissions():
    return {"Permission": Permission}