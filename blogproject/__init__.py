from flask import Flask
from blogproject.config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_admin import Admin
from flask_migrate import Migrate



db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
bootstrap = Bootstrap()
mail = Mail()



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from blogproject.main.routes import main
    from blogproject.users.routes import users
    from blogproject.errors.handlers import errors
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(errors)

    bootstrap.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)


    from .models import User, MyModelView
    admin = Admin(app)
    admin.add_view(MyModelView(User, db.session))    

    return app


