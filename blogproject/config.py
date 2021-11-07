import os

from blogproject.decorators import permission_required


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    #SQLALCHEMY_DATABASE_URI = os.getenv('POSTGRES_BLOG')
    SQLALCHEMY_DATABASE_URI = os.getenv('HEROKU_SQL')
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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
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

