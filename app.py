from flask import Flask, jsonify, request, send_file, redirect, Blueprint
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from extensions import db, mail
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
from routes.admin_routes import admin_bp
from routes.editaflex_routes import api_bp
from routes.user_routes import user_bp
from routes.stripe import api_stripe
from routes.bsgc_routes import bsgc_bp


app = Flask(__name__)
# Load configuration from environment variables or config file
from config import config

# Allow CORS for development - configure for your domain in production
CORS(app, supports_credentials=True, origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(','))

# Load configuration based on environment
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Override with environment variables if available
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', app.config['SQLALCHEMY_DATABASE_URI'])
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['JWT_SECRET_KEY'])
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', app.config['MAIL_USERNAME'])
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', app.config['MAIL_PASSWORD'])
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_DEFAULT_SENDER'])

# Set upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'sample_files')

db.init_app(app)
jwt = JWTManager(app)
mail.init_app(app)

app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(user_bp)
app.register_blueprint(api_stripe)
app.register_blueprint(bsgc_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.debug = True 
    app.run(host="0.0.0.0", port=port)