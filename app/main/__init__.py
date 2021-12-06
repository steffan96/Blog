from app.models import Permission

from .routes import main


@main.app_context_processor
def inject_permissions():
    return {"Permission": Permission}
