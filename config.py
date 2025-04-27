# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace_with_real_secret_key')
    # DATABASE_URL should be provided in the environment in production (from RDS)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
