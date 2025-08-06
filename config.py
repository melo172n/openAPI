# Configuration File
# Update with your actual values for production

import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-this-in-production')
    
    # Database Configuration  
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/database_name')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_SAMESITE = 'Lax'    
    JWT_ACCESS_COOKIE_PATH = '/'     
    JWT_COOKIE_DOMAIN = None  # Set your domain in production
    JWT_COOKIE_CSRF_PROTECT = True      
    JWT_CSRF_IN_COOKIES = True 
    
    # Mail Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_email@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_app_password_here')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'your_email@gmail.com')
    
    # Application Settings
    DOMAIN_NAME = os.getenv('DOMAIN_NAME', 'localhost:3000')
    
    # File Upload Settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'sample_files')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    JWT_COOKIE_SECURE = True  # HTTPS only in production
    JWT_COOKIE_SAMESITE = 'None'
    JWT_COOKIE_DOMAIN = '.your-domain.com'  # Update with your domain

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}