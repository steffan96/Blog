import os

from werkzeug.middleware import proxy_fix

from app.decorators import permission_required


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SSL_REDIRECT = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_TYPE = 'filesystem' 
    SESSION_PERMANENT = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    EMAIL_HOST_USER = os.getenv('EMAIL_USER')
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    FLASK_SLOW_DB_QUERY_TIME=0.5
    SQLALCHEMY_RECORD_QUERIES=True
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testsite.db'
    WTF_CSRF_ENABLED = False
    
class ProductionConfig(Config):
    
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        #email errors to the administrator
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.EMAIL_HOST_USER,
            toaddrs=[cls.ADMIN_EMAIL],
            subject='Application Error',
            credentials = credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
# rest of connection code using the connection string `uri`
    SSL_REDIRECT = True if os.environ.get('DYNO') else False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
    @classmethod
    def init_app(cls, app):
        # ...
        # handle reverse proxy server headers
        import werkzeug.middleware.proxy_fix
        app.wsgi_app = proxy_fix(app.wsgi_app)