"""
Database configuration for the Flask application to use Django's MySQL database
"""
from MySQLdb.cursors import DictCursor

# MySQL Configuration
MYSQL_CONFIG = {
    'HOST': 'localhost',  # Changed back to localhost as in Django settings
    'USER': 'pcl_user',
    'PASSWORD': 'pcl_password',
    'DB': 'pcl_db',
    'PORT': '3306',  # Changed to string to match Django settings
    'CURSORCLASS': DictCursor,
    'charset': 'utf8mb4',  # Added to match Django settings
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"  # Added to match Django settings
}

# Session Configuration
SECRET_KEY = '83e21k1f8kjn1a2=$x5i=7$=x0@!_c$54xxu^^n(u)3j_js-(k'  # Using Django's secret key

# Authentication Configuration
AUTH_TABLE = 'accounts_user'  # Django's user table
AUTH_USERNAME_FIELD = 'email'  # Django's User model uses email as username
AUTH_PASSWORD_FIELD = 'password'  # Django's password field

# Exam Configuration
PROFILE_UPLOAD_FOLDER = 'static/Profiles'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'} 