"""
WSGI configuration for PythonAnywhere
"""
import sys
import os

# Add project directory to the sys.path
project_home = '/home/tomastomeska/euapp'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from complete_app import app as application
