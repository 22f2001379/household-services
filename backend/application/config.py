class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///homeservices.sqlite3"
    DEBUG = True
    SECRET_KEY = "chinnudhana"
    SECURITY_PASSWORD_HASH = "argon2"
    SECURITY_PASSWORD_SALT = "chinnudhana-salt"
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SECURITY_TOKEN_AUTHENTICATION_KEY = "auth_token"